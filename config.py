"""
Configurazione centralizzata per BeeBus Fatture Extractor.
Gestisce variabili d'ambiente e impostazioni di produzione.
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurazione applicazione con supporto variabili d'ambiente"""

    # App info
    APP_NAME: str = "BeeBus Fatture Extractor"
    APP_VERSION: str = "2.0.0"
    APP_DESCRIPTION: str = "Estrazione automatica dati da fatture carburante (IP, Esso, Q8)"

    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # CORS configuration
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS",
        "*"  # In produzione: specificare domini separati da virgola
    ).split(",") if os.getenv("CORS_ORIGINS") else ["*"]

    # File upload limits
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))  # 50MB
    MAX_BATCH_FILES: int = int(os.getenv("MAX_BATCH_FILES", 10))

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", 100))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", 60))  # secondi

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")  # json or text

    # Monitoring
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")

    # API Keys (opzionale per autenticazione)
    API_KEY_ENABLED: bool = os.getenv("API_KEY_ENABLED", "false").lower() == "true"
    API_KEYS: List[str] = os.getenv("API_KEYS", "").split(",") if os.getenv("API_KEYS") else []

    class Config:
        env_file = ".env"
        case_sensitive = True


# Istanza singleton delle impostazioni
settings = Settings()


def is_production() -> bool:
    """Verifica se siamo in ambiente di produzione"""
    return settings.ENVIRONMENT.lower() == "production"


def is_development() -> bool:
    """Verifica se siamo in ambiente di sviluppo"""
    return settings.ENVIRONMENT.lower() == "development"
