"""
Sistema di logging centralizzato per BeeBus Fatture Extractor.
Supporta logging strutturato in formato JSON per produzione.
"""
import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
from config import settings


class JSONFormatter(logging.Formatter):
    """Formatter per log strutturati in JSON"""

    def format(self, record: logging.LogRecord) -> str:
        """Formatta il record come JSON"""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Aggiungi informazioni extra se presenti
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        # Aggiungi traceback se presente
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    """Formatter per log leggibili in development"""

    def format(self, record: logging.LogRecord) -> str:
        """Formatta il record in formato testuale"""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        level = record.levelname.ljust(8)
        message = record.getMessage()

        # Formato: [TIMESTAMP] LEVEL    | message
        log_line = f"[{timestamp}] {level} | {message}"

        # Aggiungi traceback se presente
        if record.exc_info:
            log_line += "\n" + self.formatException(record.exc_info)

        return log_line


def setup_logger(name: str = "beebus") -> logging.Logger:
    """
    Configura e restituisce un logger configurato per l'applicazione.

    Args:
        name: Nome del logger

    Returns:
        Logger configurato
    """
    logger = logging.getLogger(name)

    # Evita duplicati se già configurato
    if logger.handlers:
        return logger

    # Imposta livello di log
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Handler per stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    # Seleziona formatter in base alla configurazione
    if settings.LOG_FORMAT.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Non propagare ai logger parent
    logger.propagate = False

    return logger


# Logger globale per l'applicazione
app_logger = setup_logger("beebus")


def log_request(endpoint: str, method: str, filename: str = None, **kwargs):
    """Log di una richiesta API"""
    app_logger.info(
        f"API Request: {method} {endpoint}",
        extra={
            "endpoint": endpoint,
            "method": method,
            "filename": filename,
            **kwargs
        }
    )


def log_extraction_success(filename: str, fornitore: str, records: int, duration: float):
    """Log di estrazione completata con successo"""
    app_logger.info(
        f"Extraction successful: {filename} ({fornitore}) - {records} records in {duration:.2f}s",
        extra={
            "event": "extraction_success",
            "filename": filename,
            "fornitore": fornitore,
            "records_count": records,
            "duration_seconds": duration
        }
    )


def log_extraction_error(filename: str, error: str, error_type: str = "unknown"):
    """Log di errore durante estrazione"""
    app_logger.error(
        f"Extraction failed: {filename} - {error}",
        extra={
            "event": "extraction_error",
            "filename": filename,
            "error": error,
            "error_type": error_type
        }
    )


def log_batch_processing(files_count: int, total_records: int, duration: float):
    """Log di batch processing completato"""
    app_logger.info(
        f"Batch processing: {files_count} files, {total_records} records in {duration:.2f}s",
        extra={
            "event": "batch_processing",
            "files_count": files_count,
            "total_records": total_records,
            "duration_seconds": duration
        }
    )


def log_health_check(status: str = "healthy"):
    """Log di health check"""
    app_logger.debug(
        f"Health check: {status}",
        extra={
            "event": "health_check",
            "status": status
        }
    )