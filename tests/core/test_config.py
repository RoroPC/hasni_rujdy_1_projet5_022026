"""
Tests unitaires pour le module de configuration.
Verifie le comportement des settings et de la configuration.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestSettings:
    """Tests pour la classe Settings."""

    def test_default_values(self):
        """
        Verifie les valeurs par defaut des settings.
        """
        from app.core.config import Settings

        settings = Settings()

        assert settings.APP_NAME == "TechNova Partners - Turnover Prediction API"
        assert settings.APP_VERSION == "1.0.0"
        assert settings.DEBUG is False

    def test_api_defaults(self):
        """
        Verifie les valeurs par defaut pour l'API.
        """
        from app.core.config import Settings

        settings = Settings()

        assert settings.API_HOST == "0.0.0.0"
        assert settings.API_PORT == 8000
        assert settings.LOG_LEVEL == "info"

    def test_database_url_property(self):
        """
        Verifie la construction de l'URL de base de donnees.
        """
        from app.core.config import Settings

        settings = Settings()
        url = settings.DATABASE_URL

        assert "postgresql://" in url

    def test_database_url_async(self):
        """
        Verifie la construction de l'URL asynchrone.
        """
        from app.core.config import Settings

        settings = Settings()
        url = settings.database_url_async

        assert "postgresql+asyncpg://" in url

    def test_ml_artifact_paths(self):
        """
        Verifie les chemins des artifacts ML.
        """
        from app.core.config import Settings

        settings = Settings()

        assert "best_model_v2.pkl" in settings.MODEL_PATH
        assert "scaler.pkl" in settings.SCALER_PATH
        assert "seuil_optimal.txt" in settings.THRESHOLD_PATH

    def test_get_settings_singleton(self):
        """
        Verifie que get_settings retourne toujours la meme instance.
        """
        from app.core.config import get_settings

        settings1 = get_settings()
        settings2 = get_settings()

        # Devrait etre la meme instance (cache lru_cache)
        assert settings1 is settings2

    def test_environment_default(self):
        """
        Verifie la valeur par defaut de l'environnement.
        """
        from app.core.config import Settings

        settings = Settings()

        assert settings.ENVIRONMENT == "dev"


class TestDatabaseUrlConstruction:
    """Tests pour la construction des URLs de base de donnees."""

    def test_database_url_format(self):
        """
        Verifie le format de l'URL de base de donnees.
        """
        from app.core.config import Settings

        settings = Settings()
        url = settings.DATABASE_URL

        # Format: postgresql://user:password@host:port/dbname
        assert url.startswith("postgresql://")

    def test_database_url_sync_property(self):
        """
        Verifie la propriete database_url_sync.
        """
        from app.core.config import Settings

        settings = Settings()

        assert settings.database_url_sync == settings.DATABASE_URL
