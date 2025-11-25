"""
Estrattore per fatture Esso (WEX Europe Services).
Gestisce il formato specifico delle fatture Esso Card.
"""
import re
from typing import List, Dict, Any
from collections import defaultdict
from .base_extractor import BaseExtractor
from models.invoice_models import Transaction


class EssoExtractor(BaseExtractor):
    """Estrattore specifico per fatture Esso"""

    def __init__(self):
        super().__init__()
        self.fornitore = "ESSO"

    def can_handle(self, pdf_text: str) -> bool:
        """Verifica se il PDF è una fattura Esso"""
        indicators = ["WEX Europe Services", "ESSO CARD", "essocard"]
        return any(indicator in pdf_text for indicator in indicators)

    def extract_invoice_header(self, pdf) -> Dict[str, Any]:
        """Estrae i dati dell'intestazione della fattura Esso"""
        text = self.get_pdf_text(pdf)

        header = {
            "numero_fattura": "",
            "data_fattura": "",
            "cliente": "BEEBUS SPA",
            "totale_imponibile": 0.0,
            "totale_iva": 0.0,
            "totale_fattura": 0.0
        }

        # Estrai numero fattura (formato: 00573119)
        match_nr = re.search(r"Fattura No\s*:\s*(\d+)", text, re.IGNORECASE)
        if match_nr:
            header["numero_fattura"] = match_nr.group(1)

        # Estrai data fattura
        match_data = re.search(r"Data\s*:\s*(\d{2}\.\d{2}\.\d{4})", text)
        if match_data:
            # Converti formato DD.MM.YYYY a DD/MM/YYYY
            data_raw = match_data.group(1)
            header["data_fattura"] = data_raw.replace('.', '/')

        # Estrai cliente
        match_cliente = re.search(r"Cliente\s*:\s*([A-Z\s]+)", text)
        if match_cliente:
            header["cliente"] = match_cliente.group(1).strip()

        # Estrai totali dalla tabella riepilogo
        # Cerca pattern: TOTALE: <importo> <iva> <totale>
        match_totale = re.search(r"TOTALE:\s*([\d.,]+)\s*([\d.,]+)\s*([\d.,]+)", text)
        if match_totale:
            header["totale_imponibile"] = self.normalizza_numero(match_totale.group(1))
            header["totale_iva"] = self.normalizza_numero(match_totale.group(2))
            header["totale_fattura"] = self.normalizza_numero(match_totale.group(3))

        return header

    def extract_transactions(self, pdf) -> List[Transaction]:
        """Estrae le transazioni dalla fattura Esso"""
        transactions = []
        visti = set()
        targa_corrente = None

        for page_num, page in enumerate(pdf.pages):
            # Salta la prima pagina (riepilogo) e l'ultima (totali)
            if page_num == 0:
                # Cerca comunque le transazioni anche nella prima pagina
                pass

            words = page.extract_words(
                x_tolerance=3,
                y_tolerance=3,
                keep_blank_chars=False,
                use_text_flow=True
            )

            # Raggruppa parole per riga
            righe = defaultdict(list)
            for w in words:
                righe[round(w["top"])].append(w["text"])

            # Processa ogni riga
            for top in sorted(righe.keys()):
                line = " ".join(righe[top]).strip()
                if not line:
                    continue

                # Cerca intestazione carta con targa
                # Formato: "Carta: 078 FH682DD 7033166200912540788"
                match_carta = re.search(r"Carta:\s*\d+\s+([A-Z]{2}\d{3}[A-Z]{2})", line)
                if match_carta:
                    targa_corrente = match_carta.group(1)
                    continue

                # Cerca transazioni
                # Formato: DD.MM.YY NNNNNN LOCALITÀ KM gasolio autotrazion QQ,QQ PP,PP ...
                match_txn = self._trova_transazione(line)
                if match_txn and targa_corrente:
                    try:
                        trans_dict = self._parse_transaction(match_txn, line, targa_corrente)
                        key = (
                            trans_dict["data"],
                            trans_dict["ora"],
                            trans_dict["numero_scontrino"]
                        )
                        if key not in visti:
                            visti.add(key)
                            transactions.append(Transaction(**trans_dict))
                    except Exception as e:
                        continue

        return transactions

    def _trova_transazione(self, line: str):
        """
        Pattern regex per identificare una transazione Esso.
        Formato: 07.10.25 000412 367030 CITTADUCALE 1 gasolio autotrazion 26,58 42,50 ...
        Nota: Il campo KM può essere presente o assente.
        """
        pattern = (
            r"(\d{2}\.\d{2}\.\d{2})\s+"     # Data (DD.MM.YY)
            r"(\d{6})\s+"                   # Numero ticket
            r"(\d+)\s+"                     # Codice località
            r"([A-Z\s]+?)\s+"               # Nome località
            r"(\d+)?\s*"                    # Km (opzionale - può essere assente)
            r"gasolio\s+autotrazion\s+"     # Prodotto
            r"([\d,]+)\s+"                  # Quantità
            r"([\d,]+)"                     # Importo
        )
        return re.search(pattern, line, re.IGNORECASE)

    def _parse_transaction(self, match, line: str, targa: str) -> Dict[str, Any]:
        """Converte il match regex in un dizionario per Transaction"""
        data_raw = match.group(1)  # DD.MM.YY
        # Converti a DD/MM/YY
        data = data_raw.replace('.', '/')

        numero_ticket = match.group(2)
        codice_localita = match.group(3)
        localita = match.group(4).strip()
        # Gruppo 5 è KM - può essere None se assente
        km_raw = match.group(5)
        km = int(km_raw) if km_raw else 0
        quantita_raw = match.group(6)

        quantita = self.normalizza_numero(quantita_raw)

        # Estrai l'ULTIMO importo dalla riga (Totale incl. IVA EUR)
        # Formato tipico: ... quantità imp_ticket prezzo_pompa sconto totale_iva
        importi = re.findall(r"[\d,]+", line)
        # L'ultimo importo è il totale con IVA
        importo = self.normalizza_numero(importi[-1]) if importi else 0.0

        # Estrai ora se presente nella riga (non sempre catturata nel pattern)
        # Alcune fatture Esso non hanno l'ora, usiamo un default
        ora = "00:00"

        prezzo_unitario = importo / quantita if quantita > 0 else 0.0

        return {
            "data": data,
            "ora": ora,
            "numero_scontrino": numero_ticket,
            "codice_sede": codice_localita,
            "localita": localita,
            "targa": targa,
            "chilometraggio": km,
            "prodotto": "GASOLIO",
            "quantita": quantita,
            "prezzo_unitario": prezzo_unitario,
            "importo_totale": importo,
            "fornitore": "ESSO"
        }
