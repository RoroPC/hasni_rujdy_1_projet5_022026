"""
Configuration et fixtures pour les tests pytest.
Definit les fixtures partagees entre tous les modules de test.
"""

import sys
from pathlib import Path
from typing import Any, Dict, Generator
from unittest.mock import MagicMock

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ajout du chemin racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))


from app.db.database import Base, get_db
from app.main import app

# Configuration de la base de donnees de test (SQLite en memoire)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator:
    """
    Fixture de session de base de donnees pour les tests.

    Cree les tables au debut du test et les supprime a la fin.
    Garantit l'isolation entre les tests.

    Yields:
        Session: Session SQLAlchemy pour les tests
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session) -> Generator:
    """
    Fixture du client de test FastAPI.

    Configure l'application pour utiliser la base de donnees de test
    et fournit un client HTTP pour les tests d'integration.

    Yields:
        TestClient: Client de test FastAPI
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_employee_data() -> Dict[str, Any]:
    """
    Fixture de donnees employe valides pour les tests.

    Returns:
        Dict: Dictionnaire contenant les donnees d'un employe type
    """
    return {
        "age": 35,
        "statut_marital": "Marie(e)",
        "ayant_enfants": "Oui",
        "distance_domicile_travail": 10,
        "departement": "Consulting",
        "poste": "Consultant",
        "niveau_hierarchique_poste": 2,
        "revenu_mensuel": 5000,
        "heure_supplementaires": "Oui",
        "annee_experience_totale": 10,
        "annees_dans_le_poste_actuel": 3,
        "annees_dans_l_entreprise": 5,
        "annes_sous_responsable_actuel": 2,
        "nombre_experiences_precedentes": 2,
        "annees_depuis_la_derniere_promotion": 1,
        "nb_formations_suivies": 2,
        "note_evaluation_precedente": 3,
        "nombre_participation_pee": 1,
        "satisfaction_employee_nature_travail": 3,
        "satisfaction_employee_environnement": 3,
        "satisfaction_employee_equilibre_pro_perso": 3,
        "satisfaction_employee_equipe": 3,
    }


@pytest.fixture
def sample_employee_high_risk() -> Dict[str, Any]:
    """
    Fixture de donnees employe a haut risque de depart.

    Returns:
        Dict: Dictionnaire contenant les donnees d'un employe a risque
    """
    return {
        "age": 28,
        "statut_marital": "Celibataire",
        "ayant_enfants": "Non",
        "distance_domicile_travail": 25,
        "departement": "Consulting",
        "poste": "Consultant",
        "niveau_hierarchique_poste": 1,
        "revenu_mensuel": 3000,
        "heure_supplementaires": "Oui",
        "annee_experience_totale": 4,
        "annees_dans_le_poste_actuel": 4,
        "annees_dans_l_entreprise": 2,
        "annes_sous_responsable_actuel": 2,
        "nombre_experiences_precedentes": 3,
        "annees_depuis_la_derniere_promotion": 4,
        "nb_formations_suivies": 0,
        "note_evaluation_precedente": 2,
        "nombre_participation_pee": 0,
        "satisfaction_employee_nature_travail": 1,
        "satisfaction_employee_environnement": 1,
        "satisfaction_employee_equilibre_pro_perso": 1,
        "satisfaction_employee_equipe": 1,
    }


@pytest.fixture
def sample_preprocessed_dataframe() -> pd.DataFrame:
    """
    Fixture de DataFrame preprocesse pour les tests ML.

    Returns:
        pd.DataFrame: DataFrame avec les 34 features attendues
    """
    features = [
        "heure_supplementaires",
        "annee_experience_totale",
        "niveau_hierarchique_poste",
        "annees_dans_le_poste_actuel",
        "revenu_mensuel",
        "age",
        "annes_sous_responsable_actuel",
        "nombre_participation_pee",
        "annees_dans_l_entreprise",
        "note_evaluation_precedente",
        "satisfaction_employee_nature_travail",
        "satisfaction_employee_environnement",
        "distance_domicile_travail",
        "satisfaction_employee_equilibre_pro_perso",
        "nb_formations_suivies",
        "satisfaction_employee_equipe",
        "nombre_experiences_precedentes",
        "annees_depuis_la_derniere_promotion",
        "statut_marital_Divorcé(e)",
        "statut_marital_Marié(e)",
        "departement_Consulting",
        "departement_Ressources Humaines",
        "poste_Cadre Commercial",
        "poste_Consultant",
        "poste_Directeur Technique",
        "poste_Manager",
        "poste_Représentant Commercial",
        "poste_Ressources Humaines",
        "poste_Senior Manager",
        "poste_Tech Lead",
        "salaire_par_age",
        "stagnation_poste",
        "promotion_recente",
        "distance_longue",
    ]

    data = {feat: [0] for feat in features}
    data["age"] = [35]
    data["revenu_mensuel"] = [5000]
    data["salaire_par_age"] = [5000 / 35]

    return pd.DataFrame(data)


@pytest.fixture
def mock_predictor():
    """
    Fixture de predicteur mocke pour les tests unitaires.

    Returns:
        MagicMock: Mock du TurnoverPredictor
    """
    predictor = MagicMock()
    predictor.predict_single.return_value = {
        "prediction": "Risque de depart",
        "prediction_binary": 1,
        "probability": 0.7234,
        "risk_level": "ELEVE",
        "confidence": 0.2361,
        "threshold": 0.36,
    }
    predictor.get_model_info.return_value = {
        "model_type": "LogisticRegression",
        "model_version": "2.0",
        "threshold": 0.36,
        "n_features": 34,
        "description": "Modele de prediction du turnover",
    }
    predictor.schema = {"model_info": {"version": "2.0"}}

    return predictor
