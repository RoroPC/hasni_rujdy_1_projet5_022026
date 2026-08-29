"""
Module de gestion de la connexion a la base de donnees PostgreSQL.
Utilise SQLAlchemy pour l'ORM et la gestion des sessions.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings

settings = get_settings()

engine_options = {
    "pool_pre_ping": True,
    "echo": settings.DATABASE_ECHO,
}
if not settings.DATABASE_URL.startswith("sqlite"):
    engine_options.update({"pool_size": 5, "max_overflow": 10})

# Creation du moteur SQLAlchemy
engine = create_engine(settings.DATABASE_URL, **engine_options)

# Factory de sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base pour les modeles
Base = declarative_base()


def get_db() -> Generator:
    """
    Generateur de sessions de base de donnees.

    Utilise le pattern context manager pour garantir la fermeture
    de la session apres utilisation.

    Yields:
        Session: Session SQLAlchemy active

    Example:
        >>> with get_db() as db:
        ...     result = db.query(Model).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialise la base de donnees en creant toutes les tables.

    Cette fonction doit etre appelee au demarrage de l'application
    pour s'assurer que le schema de la base est a jour.
    """
    from app.db.models import Base

    Base.metadata.create_all(bind=engine)


def create_test_engine(database_url: str = "sqlite:///:memory:"):
    """
    Cree un moteur de base de donnees pour les tests.

    Utilise SQLite en memoire par defaut pour des tests rapides
    et isoles.

    Parameters:
        database_url: URL de la base de donnees de test

    Returns:
        Engine: Moteur SQLAlchemy configure pour les tests
    """
    return create_engine(
        database_url,
        connect_args={"check_same_thread": False} if "sqlite" in database_url else {},
        poolclass=StaticPool if "sqlite" in database_url else None,
    )
