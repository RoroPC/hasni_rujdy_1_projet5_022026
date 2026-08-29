"""
Module de configuration de l'application.
Centralise toutes les variables d'environnement et parametres de configuration.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuration de l'application via variables d'environnement.

    Les valeurs peuvent etre definies via des variables d'environnement
    ou un fichier .env a la racine du projet.
    """

    # Environment
    ENVIRONMENT: str = "dev"

    # Application
    APP_NAME: str = "TechNova Partners - Turnover Prediction API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "API de prediction du turnover des employes"
    DEBUG: bool = False

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    LOG_LEVEL: str = "info"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/turnover_db"
    DATABASE_ECHO: bool = False

    # ML Artifacts
    MODEL_PATH: str = "artifacts/best_model_v2.pkl"
    SCALER_PATH: str = "artifacts/scaler.pkl"
    THRESHOLD_PATH: str = "artifacts/seuil_optimal.txt"
    SCHEMA_PATH: str = "app/ml/features_schema.json"

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    API_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Hugging Face (optionnel)
    HF_TOKEN: str = ""
    HF_SPACE_NAME: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def database_url_sync(self) -> str:
        """Retourne l'URL de connexion synchrone a la base de donnees."""
        return self.DATABASE_URL

    @property
    def database_url_async(self) -> str:
        """Construit l'URL de connexion asynchrone a la base de donnees."""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

    @property
    def cors_origins(self) -> list[str]:
        """Retourne la liste normalisee des origines CORS autorisees."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    """
    Retourne une instance unique des settings (singleton).

    Returns:
        Settings: Configuration de l'application
    """
    return Settings()
