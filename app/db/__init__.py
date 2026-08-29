"""
Module de base de donnees de l'application.

Contient les modeles SQLAlchemy, la configuration de la connexion
et les repositories pour les operations CRUD.
"""

from app.db.database import Base, SessionLocal, engine, get_db, init_db
from app.db.models import EmployeeData, Prediction, PredictionLog
from app.db.repository import EmployeeRepository, LogRepository, PredictionRepository

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "init_db",
    "EmployeeData",
    "Prediction",
    "PredictionLog",
    "EmployeeRepository",
    "PredictionRepository",
    "LogRepository",
]
