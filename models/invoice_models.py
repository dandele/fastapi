"""
Modelli dati comuni per le fatture di carburante.
Questi modelli sono usati da tutti gli estrattori per garantire un output standardizzato.
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class Transaction(BaseModel):
    """Modello standardizzato per una singola transazione di rifornimento"""
    data: str = Field(description="Data rifornimento (formato DD/MM/YY)")
    ora: str = Field(description="Ora rifornimento (formato HH:MM)")
    numero_scontrino: str = Field(description="Numero scontrino/ticket")
    codice_sede: str = Field(description="Codice punto vendita")
    localita: str = Field(description="Nome località/stazione")
    targa: str = Field(description="Targa veicolo")
    chilometraggio: int = Field(default=0, description="Km veicolo")
    prodotto: str = Field(description="Tipo carburante (GASOLIO, GASOLIO SELF, etc)")
    quantita: float = Field(description="Quantità in litri")
    prezzo_unitario: float = Field(description="Prezzo al litro")
    importo_totale: float = Field(description="Importo totale rifornimento")
    fornitore: str = Field(description="Fornitore (IP, ESSO, Q8)")

    # Campi opzionali aggiuntivi
    sconto: Optional[float] = Field(None, description="Sconto applicato")
    numero_carta: Optional[str] = Field(None, description="Numero carta carburante")
    iva_percentuale: Optional[float] = Field(None, description="Percentuale IVA")
    iva_importo: Optional[float] = Field(None, description="Importo IVA")
    imponibile: Optional[float] = Field(None, description="Imponibile")


class InvoiceData(BaseModel):
    """Modello per i dati aggregati della fattura"""
    numero_fattura: str = Field(description="Numero fattura")
    data_fattura: str = Field(description="Data emissione fattura")
    fornitore: str = Field(description="Nome fornitore")
    cliente: str = Field(description="Nome cliente")
    totale_imponibile: float = Field(description="Totale imponibile")
    totale_iva: float = Field(description="Totale IVA")
    totale_fattura: float = Field(description="Totale fattura")
    transactions: List[Transaction] = Field(default_factory=list, description="Lista transazioni")


class ExtractionResult(BaseModel):
    """Modello per il risultato dell'estrazione"""
    status: str = Field(default="success")
    filename: str
    timestamp: str
    fornitore: str = Field(description="Fornitore identificato (IP, ESSO, Q8)")
    invoice_data: InvoiceData
    records_count: int
    total_amount: float
    message: Optional[str] = None
