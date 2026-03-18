"""
Test suite per IPExtractor
Verifica fix per supporto prodotti generici (non solo GASOLIO/GASOLIO SELF)
"""
import pytest
from extractors.ip_extractor import IPExtractor


class TestIPExtractor:
    """Test per l'estrattore IP Plus"""

    @pytest.fixture
    def extractor(self):
        """Fixture che restituisce un'istanza di IPExtractor"""
        return IPExtractor()

    def test_can_handle_ip_text(self, extractor):
        """Verifica che can_handle riconosca testo IP"""
        ip_text = "IP PLUS S.R.L - fattura rifornimenti"
        assert extractor.can_handle(ip_text) is True

    def test_trova_transazione_gasolio(self, extractor):
        """Verifica pattern regex per GASOLIO"""
        line = "01/10/25 18:48 00006015 46620 CAPENA - TIBERINA 110 1 0000 GASOLIO 50,58 82,93"
        match = extractor._trova_transazione(line)

        assert match is not None
        assert match.group(1) == "01/10/25"  # Data
        assert match.group(2) == "18:48"  # Ora
        assert match.group(3) == "00006015"  # Numero scontrino
        assert match.group(4) == "46620"  # Codice PV
        assert match.group(5) == "CAPENA - TIBERINA 110"  # Località (regex lazy include il numero)
        assert match.group(6) == "1"  # KM (il "1" prima di 0000)
        assert match.group(7) == "GASOLIO"  # Prodotto
        assert match.group(8) == "50,58"  # Quantità

    def test_trova_transazione_gasolio_self(self, extractor):
        """Verifica pattern regex per GASOLIO SELF"""
        line = "02/10/25 09:30 00006016 46620 CAPENA - TIBERINA 120 1 0000 GASOLIO SELF 45,23 74,12"
        match = extractor._trova_transazione(line)

        assert match is not None
        assert match.group(7) == "GASOLIO SELF"

    def test_trova_transazione_metano(self, extractor):
        """
        CRITICAL TEST: Verifica pattern regex per METANO (nuovo fix)
        Prima non funzionava, ora deve supportare qualsiasi prodotto
        """
        line = "04/10/25 12:46 00005546 43887 RIANO - TIBERINA 110 1 0000 METANO 124,80 153,38"
        match = extractor._trova_transazione(line)

        assert match is not None
        assert match.group(1) == "04/10/25"
        assert match.group(2) == "12:46"
        assert match.group(3) == "00005546"
        assert match.group(4) == "43887"
        assert match.group(5) == "RIANO - TIBERINA 110"  # Regex lazy include il numero
        assert match.group(6) == "1"  # KM (il "1" prima di 0000)
        assert match.group(7) == "METANO"  # Prodotto generico
        assert match.group(8) == "124,80"

    def test_trova_transazione_generic_product(self, extractor):
        """Verifica che il pattern catturi qualsiasi prodotto in maiuscolo"""
        # Test con prodotto ipotetico
        line = "04/10/25 12:46 00005546 43887 RIANO - TIBERINA 110 1 0000 GPL SPECIALE 50,00 75,00"
        match = extractor._trova_transazione(line)

        assert match is not None
        assert match.group(7) == "GPL SPECIALE"

    def test_parse_transaction_gasolio(self, extractor):
        """Verifica parsing transazione GASOLIO"""
        line = "01/10/25 18:48 00006015 46620 CAPENA - TIBERINA 110 1 0000 GASOLIO 50,58 82,93"
        match = extractor._trova_transazione(line)
        trans_dict = extractor._parse_transaction(match, line)

        assert trans_dict["data"] == "01/10/25"
        assert trans_dict["ora"] == "18:48"
        assert trans_dict["numero_scontrino"] == "00006015"
        assert trans_dict["codice_sede"] == "46620"
        assert trans_dict["localita"] == "CAPENA - TIBERINA 110"
        assert trans_dict["chilometraggio"] == 1
        assert trans_dict["prodotto"] == "GASOLIO"
        assert trans_dict["quantita"] == 50.58
        assert trans_dict["importo_totale"] == 82.93
        assert trans_dict["fornitore"] == "IP"

    def test_parse_transaction_metano(self, extractor):
        """
        CRITICAL TEST: Verifica parsing transazione METANO
        Prima falliva perché il regex non catturava METANO
        """
        line = "04/10/25 12:46 00005546 43887 RIANO - TIBERINA 110 1 0000 METANO 124,80 153,38"
        match = extractor._trova_transazione(line)
        trans_dict = extractor._parse_transaction(match, line)

        assert trans_dict["data"] == "04/10/25"
        assert trans_dict["ora"] == "12:46"
        assert trans_dict["numero_scontrino"] == "00005546"
        assert trans_dict["codice_sede"] == "43887"
        assert trans_dict["localita"] == "RIANO - TIBERINA 110"
        assert trans_dict["chilometraggio"] == 1
        assert trans_dict["prodotto"] == "METANO"  # Prodotto catturato correttamente
        assert trans_dict["quantita"] == 124.80
        assert trans_dict["importo_totale"] == 153.38
        assert trans_dict["fornitore"] == "IP"

    def test_fornitore_name(self, extractor):
        """Verifica che il nome fornitore sia corretto"""
        assert extractor.fornitore == "IP"


class TestIPIntegration:
    """Test di integrazione con PDF reali IP"""

    @pytest.fixture
    def extractor(self):
        return IPExtractor()

    @pytest.fixture
    def pdf_path(self):
        return "/Users/mirkopapadopoli/Code/fastapi/Fatture nuove/ip del 1-10.pdf"

    def test_extract_real_pdf(self, extractor, pdf_path):
        """Test estrazione da PDF IP reale"""
        import os
        if not os.path.exists(pdf_path):
            pytest.skip(f"PDF non trovato: {pdf_path}")

        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()

        from io import BytesIO
        result = extractor.extract(BytesIO(pdf_content), "ip_test.pdf")

        assert result.status == "success"
        assert result.fornitore == "IP"
        assert result.records_count > 0

    def test_extract_metano_transaction(self, extractor, pdf_path):
        """
        CRITICAL TEST: Verifica estrazione della transazione METANO
        Transazione che prima non veniva estratta:
        04/10/25 12:46 00005546 43887 RIANO - TIBERINA 110 1 0000 METANO 124,80 153,38
        """
        import os
        if not os.path.exists(pdf_path):
            pytest.skip(f"PDF non trovato: {pdf_path}")

        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()

        from io import BytesIO
        result = extractor.extract(BytesIO(pdf_content), "ip_test.pdf")

        # Cerca la transazione METANO specifica (numero scontrino 00005546)
        found = False
        for trans in result.invoice_data.transactions:
            if trans.numero_scontrino == "00005546":
                found = True
                assert trans.prodotto == "METANO"
                assert trans.localita == "RIANO - TIBERINA 110"
                assert trans.quantita == 124.80
                assert trans.importo_totale == 153.38
                break

        assert found, "Transazione METANO 00005546 non trovata!"

    def test_product_variety(self, extractor, pdf_path):
        """Verifica che vengano estratti diversi tipi di prodotto"""
        import os
        if not os.path.exists(pdf_path):
            pytest.skip(f"PDF non trovato: {pdf_path}")

        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()

        from io import BytesIO
        result = extractor.extract(BytesIO(pdf_content), "ip_test.pdf")

        # Raccogli tutti i prodotti unici
        prodotti = set(trans.prodotto for trans in result.invoice_data.transactions)

        # Deve esserci almeno GASOLIO o METANO
        assert len(prodotti) > 0
        # Se il PDF contiene METANO, deve essere estratto
        if any(trans.numero_scontrino == "00005546" for trans in result.invoice_data.transactions):
            assert "METANO" in prodotti
