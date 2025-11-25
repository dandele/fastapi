"""
Factory per identificare automaticamente il tipo di fattura e restituire l'estrattore appropriato.
"""
import pdfplumber
from io import BytesIO
from typing import Optional
from .base_extractor import BaseExtractor
from .ip_extractor import IPExtractor
from .esso_extractor import EssoExtractor
from .q8_extractor import Q8Extractor
from .tamoil_extractor import TamoilExtractor


class ExtractorFactory:
    """
    Factory per creare l'estrattore appropriato basandosi sul contenuto del PDF.
    """

    # Registra tutti gli estrattori disponibili
    EXTRACTORS = [
        IPExtractor,
        EssoExtractor,
        Q8Extractor,
        TamoilExtractor
    ]

    @classmethod
    def get_extractor(cls, pdf_content: bytes) -> Optional[BaseExtractor]:
        """
        Identifica il tipo di fattura e restituisce l'estrattore appropriato.

        Args:
            pdf_content: Contenuto binario del PDF

        Returns:
            Istanza dell'estrattore appropriato o None se nessuno corrisponde

        Raises:
            ValueError: Se non viene trovato un estrattore compatibile
        """
        try:
            # Estrai il testo dal PDF
            pdf_text = cls._extract_text_from_pdf(pdf_content)

            # Prova ogni estrattore
            for extractor_class in cls.EXTRACTORS:
                extractor = extractor_class()
                if extractor.can_handle(pdf_text):
                    return extractor

            # Nessun estrattore trovato
            raise ValueError(
                "Tipo di fattura non riconosciuto. "
                "Formati supportati: IP Plus, Esso, Q8, Tamoil"
            )

        except Exception as e:
            raise ValueError(f"Errore nell'identificazione del tipo di fattura: {str(e)}")

    @staticmethod
    def _extract_text_from_pdf(pdf_content: bytes) -> str:
        """
        Estrae il testo completo dal PDF per l'identificazione.

        Args:
            pdf_content: Contenuto binario del PDF

        Returns:
            Testo completo del PDF
        """
        text = ""
        pdf_stream = BytesIO(pdf_content)

        with pdfplumber.open(pdf_stream) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        return text

    @classmethod
    def extract_from_pdf(cls, pdf_content: bytes, filename: str) -> dict:
        """
        Metodo di convenienza che identifica il tipo e estrae i dati in un solo passaggio.

        Args:
            pdf_content: Contenuto binario del PDF
            filename: Nome del file

        Returns:
            Dizionario con i dati estratti (compatibile con l'output legacy)
        """
        # Ottieni l'estrattore appropriato
        extractor = cls.get_extractor(pdf_content)

        # Estrai i dati
        pdf_stream = BytesIO(pdf_content)
        result = extractor.extract(pdf_stream, filename)

        # Converti in formato legacy per retrocompatibilità
        return cls._convert_to_legacy_format(result)

    @staticmethod
    def _convert_to_legacy_format(extraction_result) -> dict:
        """
        Converte ExtractionResult nel formato legacy usato dal vecchio main.py.

        Args:
            extraction_result: Oggetto ExtractionResult

        Returns:
            Dizionario in formato legacy
        """
        # Converti le transazioni in dizionari
        data = []
        for transaction in extraction_result.invoice_data.transactions:
            record = {
                "Targa": transaction.targa,
                "Data_Rifornimento": transaction.data,
                "Ora_Rifornimento": transaction.ora,
                "Chilometraggio": transaction.chilometraggio,
                "Litri": transaction.quantita,
                "Importo_Totale": transaction.importo_totale,
                "Fornitore": transaction.fornitore,
                "Tipo_Rifornimento": "esterno",  # Default per compatibilità
                "Numero_Scontrino": transaction.numero_scontrino,
                "Localita": transaction.localita
            }
            data.append(record)

        return {
            "status": extraction_result.status,
            "filename": extraction_result.filename,
            "timestamp": extraction_result.timestamp,
            "records_count": extraction_result.records_count,
            "total_amount": extraction_result.total_amount,
            "data": data,
            "fornitore": extraction_result.fornitore,
            "message": extraction_result.message
        }
