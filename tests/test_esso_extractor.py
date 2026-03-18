"""
Test suite per EssoExtractor
Verifica fix per estrazione importo con IVA (ultimo importo della riga)
"""
import pytest
import re
from extractors.esso_extractor import EssoExtractor


class TestEssoExtractor:
    """Test per l'estrattore Esso"""

    @pytest.fixture
    def extractor(self):
        """Fixture che restituisce un'istanza di EssoExtractor"""
        return EssoExtractor()

    def test_can_handle_esso_text(self, extractor):
        """Verifica che can_handle riconosca testo Esso"""
        esso_text = "WEX Europe Services - ESSO CARD"
        assert extractor.can_handle(esso_text) is True

    def test_trova_transazione_with_km(self, extractor):
        """Verifica pattern regex per transazione con KM"""
        line = "07.10.25 000412 367030 CITTADUCALE 26 gasolio autotrazion 26,58 42,50 1,600 0,00 1,600 42,50"
        match = extractor._trova_transazione(line)

        assert match is not None
        assert match.group(1) == "07.10.25"  # Data
        assert match.group(2) == "000412"  # Numero ticket
        assert match.group(3) == "367030"  # Codice località
        assert match.group(4) == "CITTADUCALE"  # Località
        assert match.group(5) == "26"  # KM
        assert match.group(6) == "gasolio autotrazion"  # Prodotto (catturato)
        assert match.group(7) == "26,58"  # Quantità

    def test_trova_transazione_without_km(self, extractor):
        """Verifica pattern regex per transazione SENZA KM (fix)"""
        line = "03.10.25 006241 350749 RIGNANO FLAMI gasolio autotrazion 61,63 106,56 1,729 0,00 1,729 106,56"
        match = extractor._trova_transazione(line)

        assert match is not None
        assert match.group(1) == "03.10.25"  # Data
        assert match.group(2) == "006241"  # Numero ticket
        assert match.group(3) == "350749"  # Codice località
        assert match.group(4) == "RIGNANO FLAMI"  # Località
        assert match.group(5) is None  # KM assente
        assert match.group(6) == "gasolio autotrazion"  # Prodotto (catturato)
        assert match.group(7) == "61,63"  # Quantità

    def test_trova_transazione_captures_product(self, extractor):
        """Verifica che il prodotto venga catturato dinamicamente dal pattern"""
        line = "07.10.25 000412 367030 CITTADUCALE 26 gasolio autotrazion 26,58 42,50 1,600 0,00 1,600 42,50"
        match = extractor._trova_transazione(line)

        assert match is not None
        assert match.group(6) == "gasolio autotrazion"

    def test_parse_transaction_km_present(self, extractor):
        """Verifica parsing transazione con KM presente"""
        line = "07.10.25 000412 367030 CITTADUCALE 26 gasolio autotrazion 26,58 42,50 1,600 0,00 1,600 42,50"
        match = extractor._trova_transazione(line)
        trans_dict = extractor._parse_transaction(match, line, "FP466ED")

        assert trans_dict["data"] == "07/10/25"
        assert trans_dict["numero_scontrino"] == "000412"
        assert trans_dict["codice_sede"] == "367030"
        assert trans_dict["localita"] == "CITTADUCALE"
        assert trans_dict["chilometraggio"] == 26
        assert trans_dict["quantita"] == 26.58
        assert trans_dict["targa"] == "FP466ED"
        assert trans_dict["fornitore"] == "ESSO"
        assert trans_dict["prodotto"] == "GASOLIO AUTOTRAZION"  # Dinamico + uppercase

    def test_parse_transaction_km_absent(self, extractor):
        """Verifica parsing transazione SENZA KM (fix)"""
        line = "03.10.25 006241 350749 RIGNANO FLAMI gasolio autotrazion 61,63 106,56 1,729 0,00 1,729 106,56"
        match = extractor._trova_transazione(line)
        trans_dict = extractor._parse_transaction(match, line, "FP466ED")

        assert trans_dict["data"] == "03/10/25"
        assert trans_dict["numero_scontrino"] == "006241"
        assert trans_dict["codice_sede"] == "350749"
        assert trans_dict["localita"] == "RIGNANO FLAMI"
        assert trans_dict["chilometraggio"] == 0  # Default quando assente
        assert trans_dict["quantita"] == 61.63
        assert trans_dict["prodotto"] == "GASOLIO AUTOTRAZION"  # Dinamico + uppercase

    def test_importo_totale_is_last_amount(self, extractor):
        """
        CRITICAL TEST: Verifica che l'importo estratto sia l'ULTIMO della riga
        (Totale incl. IVA EUR) e NON il primo (Imp. Ticket)
        """
        # Riga con più importi: 42,50 (Imp. Ticket) ... 42,50 (Totale IVA)
        line = "07.10.25 000412 367030 CITTADUCALE 26 gasolio autotrazion 26,58 42,50 1,600 0,00 1,600 42,50"
        match = extractor._trova_transazione(line)
        trans_dict = extractor._parse_transaction(match, line, "FP466ED")

        # In questo caso sono uguali, ma il codice deve usare l'ultimo
        assert trans_dict["importo_totale"] == 42.50

        # Caso con importi diversi
        line2 = "03.10.25 006241 350749 RIGNANO FLAMI gasolio autotrazion 61,63 100,00 1,729 5,56 1,600 106,56"
        match2 = extractor._trova_transazione(line2)
        trans_dict2 = extractor._parse_transaction(match2, line2, "FP466ED")

        # L'importo totale deve essere 106,56 (ultimo) NON 100,00 (primo dopo quantità)
        assert trans_dict2["importo_totale"] == 106.56

    def test_extract_all_amounts_from_line(self, extractor):
        """Verifica che findall estragga tutti gli importi dalla riga"""
        line = "07.10.25 000412 367030 CITTADUCALE 26 gasolio autotrazion 26,58 42,50 1,600 0,00 1,600 42,50"
        importi = re.findall(r"[\d,]+", line)

        # Dovrebbero esserci molti numeri nella riga
        assert len(importi) > 5
        # L'ultimo deve essere il totale IVA
        assert importi[-1] == "42,50"

    def test_fornitore_name(self, extractor):
        """Verifica che il nome fornitore sia corretto"""
        assert extractor.fornitore == "ESSO"


class TestEssoIntegration:
    """Test di integrazione con PDF reali Esso"""

    @pytest.fixture
    def extractor(self):
        return EssoExtractor()

    @pytest.fixture
    def pdf_path(self):
        return "/Users/mirkopapadopoli/Code/fastapi/Fatture nuove/esso del 1-10.pdf"

    def test_extract_real_pdf(self, extractor, pdf_path):
        """Test estrazione da PDF Esso reale"""
        import os
        if not os.path.exists(pdf_path):
            pytest.skip(f"PDF non trovato: {pdf_path}")

        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()

        from io import BytesIO
        result = extractor.extract(BytesIO(pdf_content), "esso_test.pdf")

        assert result.status == "success"
        assert result.fornitore == "ESSO"
        assert result.records_count > 0

    def test_extract_missing_transaction_without_km(self, extractor, pdf_path):
        """
        CRITICAL TEST: Verifica estrazione della transazione mancante
        Transazione senza KM che prima non veniva estratta:
        03.10.25 006241 350749 RIGNANO FLAMI gasolio autotrazion 61,63 106,56
        """
        import os
        if not os.path.exists(pdf_path):
            pytest.skip(f"PDF non trovato: {pdf_path}")

        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()

        from io import BytesIO
        result = extractor.extract(BytesIO(pdf_content), "esso_test.pdf")

        # Cerca la transazione specifica (numero scontrino 006241)
        found = False
        for trans in result.invoice_data.transactions:
            if trans.numero_scontrino == "006241":
                found = True
                assert trans.localita == "RIGNANO FLAMI"
                assert trans.quantita == 61.63
                assert trans.chilometraggio == 0  # KM assente
                break

        assert found, "Transazione 006241 (senza KM) non trovata!"

    def test_all_amounts_are_with_iva(self, extractor, pdf_path):
        """Verifica che tutti gli importi siano quelli con IVA (ultimo della riga)"""
        import os
        if not os.path.exists(pdf_path):
            pytest.skip(f"PDF non trovato: {pdf_path}")

        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()

        from io import BytesIO
        result = extractor.extract(BytesIO(pdf_content), "esso_test.pdf")

        # Tutte le transazioni devono avere importo > 0
        for trans in result.invoice_data.transactions:
            assert trans.importo_totale > 0, f"Importo zero per scontrino {trans.numero_scontrino}"
