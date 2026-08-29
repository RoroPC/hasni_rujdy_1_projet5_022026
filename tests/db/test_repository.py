"""
Tests unitaires pour les repositories de base de donnees.
Verifie les operations CRUD.
"""

import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.db.database import Base
from app.db.repository import EmployeeRepository, LogRepository, PredictionRepository

# Configuration de la base de donnees de test
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Fixture de session de base de donnees pour les tests.
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_employee_dict():
    """
    Fixture de donnees employe sous forme de dictionnaire.
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


class TestEmployeeRepository:
    """Tests pour EmployeeRepository."""

    def test_create_employee(self, db_session, sample_employee_dict):
        """
        Verifie la creation d'un employe.
        """
        repo = EmployeeRepository(db_session)

        employee = repo.create(sample_employee_dict)

        assert employee.id is not None
        assert employee.request_id is not None
        assert employee.age == 35

    def test_get_by_id(self, db_session, sample_employee_dict):
        """
        Verifie la recuperation par ID.
        """
        repo = EmployeeRepository(db_session)

        created = repo.create(sample_employee_dict)
        retrieved = repo.get_by_id(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id

    def test_get_by_id_not_found(self, db_session):
        """
        Verifie le comportement quand l'ID n'existe pas.
        """
        repo = EmployeeRepository(db_session)

        result = repo.get_by_id(999)

        assert result is None

    def test_get_by_request_id(self, db_session, sample_employee_dict):
        """
        Verifie la recuperation par request_id.
        """
        repo = EmployeeRepository(db_session)

        created = repo.create(sample_employee_dict)
        retrieved = repo.get_by_request_id(created.request_id)

        assert retrieved is not None
        assert retrieved.request_id == created.request_id

    def test_get_all(self, db_session, sample_employee_dict):
        """
        Verifie la recuperation de tous les employes.
        """
        repo = EmployeeRepository(db_session)

        repo.create(sample_employee_dict)
        repo.create(sample_employee_dict)
        repo.create(sample_employee_dict)

        employees = repo.get_all()

        assert len(employees) == 3

    def test_get_all_with_pagination(self, db_session, sample_employee_dict):
        """
        Verifie la pagination.
        """
        repo = EmployeeRepository(db_session)

        for _ in range(5):
            repo.create(sample_employee_dict)

        # Premier page
        page1 = repo.get_all(skip=0, limit=2)
        assert len(page1) == 2

        # Deuxieme page
        page2 = repo.get_all(skip=2, limit=2)
        assert len(page2) == 2

        # Derniere page
        page3 = repo.get_all(skip=4, limit=2)
        assert len(page3) == 1


class TestPredictionRepository:
    """Tests pour PredictionRepository."""

    def test_create_prediction(self, db_session, sample_employee_dict):
        """
        Verifie la creation d'une prediction.
        """
        employee_repo = EmployeeRepository(db_session)
        prediction_repo = PredictionRepository(db_session)

        employee = employee_repo.create(sample_employee_dict)

        prediction = prediction_repo.create(
            employee_data_id=employee.id,
            probability=0.7234,
            prediction_binary=1,
            risk_level="ELEVE",
            confidence=0.2361,
            threshold_used=0.4873,
            model_version="2.0",
        )

        assert prediction.id is not None
        assert prediction.probability == 0.7234

    def test_get_by_employee_id(self, db_session, sample_employee_dict):
        """
        Verifie la recuperation par employee_id.
        """
        employee_repo = EmployeeRepository(db_session)
        prediction_repo = PredictionRepository(db_session)

        employee = employee_repo.create(sample_employee_dict)
        prediction_repo.create(
            employee_data_id=employee.id,
            probability=0.5,
            prediction_binary=1,
            risk_level="MODERE",
            confidence=0.1,
            threshold_used=0.5,
        )

        prediction = prediction_repo.get_by_employee_id(employee.id)

        assert prediction is not None
        assert prediction.employee_data_id == employee.id

    def test_get_all_predictions(self, db_session, sample_employee_dict):
        """
        Verifie la recuperation de toutes les predictions.
        """
        employee_repo = EmployeeRepository(db_session)
        prediction_repo = PredictionRepository(db_session)

        for _ in range(3):
            employee = employee_repo.create(sample_employee_dict)
            prediction_repo.create(
                employee_data_id=employee.id,
                probability=0.5,
                prediction_binary=1,
                risk_level="MODERE",
                confidence=0.1,
                threshold_used=0.5,
            )

        predictions = prediction_repo.get_all()

        assert len(predictions) == 3

    def test_get_statistics_empty(self, db_session):
        """
        Verifie les statistiques avec une base vide.
        """
        prediction_repo = PredictionRepository(db_session)

        stats = prediction_repo.get_statistics()

        assert stats["total_predictions"] == 0
        assert stats["average_probability"] == 0

    def test_get_statistics_with_data(self, db_session, sample_employee_dict):
        """
        Verifie les statistiques avec des donnees.
        """
        employee_repo = EmployeeRepository(db_session)
        prediction_repo = PredictionRepository(db_session)

        # Creer quelques predictions
        probabilities = [0.3, 0.5, 0.7]
        for prob in probabilities:
            employee = employee_repo.create(sample_employee_dict)
            prediction_repo.create(
                employee_data_id=employee.id,
                probability=prob,
                prediction_binary=1 if prob > 0.5 else 0,
                risk_level="ELEVE" if prob > 0.5 else "FAIBLE",
                confidence=abs(prob - 0.5),
                threshold_used=0.5,
            )

        stats = prediction_repo.get_statistics()

        assert stats["total_predictions"] == 3
        assert stats["average_probability"] == pytest.approx(0.5, rel=0.01)

    def test_statistics_count_accented_high_risk_labels(self, db_session, sample_employee_dict):
        """Les libelles produits par le modele sont comptes comme risques eleves."""
        employee = EmployeeRepository(db_session).create(sample_employee_dict)
        repository = PredictionRepository(db_session)
        repository.create(
            employee_data_id=employee.id,
            probability=0.8,
            prediction_binary=1,
            risk_level="TRÈS ÉLEVÉ",
            confidence=0.44,
            threshold_used=0.36,
        )

        assert repository.get_statistics()["high_risk_count"] == 1
        assert repository.count() == 1


class TestLogRepository:
    """Tests pour LogRepository."""

    def test_create_log(self, db_session):
        """
        Verifie la creation d'un log.
        """
        repo = LogRepository(db_session)

        log = repo.create(
            request_id="test-log",
            endpoint="/predict",
            method="POST",
            status_code=200,
            client_ip="127.0.0.1",
            response_time_ms=150.0,
        )

        assert log.id is not None
        assert log.request_id == "test-log"

    def test_create_log_with_error(self, db_session):
        """
        Verifie la creation d'un log avec erreur.
        """
        repo = LogRepository(db_session)

        log = repo.create(
            request_id="error-log",
            endpoint="/predict",
            method="POST",
            status_code=500,
            error_message="Internal error",
        )

        assert log.status_code == 500
        assert log.error_message == "Internal error"

    def test_log_timestamp_auto(self, db_session):
        """
        Verifie que le timestamp est automatique.
        """
        repo = LogRepository(db_session)

        log = repo.create(
            request_id="timestamp-log", endpoint="/health", method="GET", status_code=200
        )

        assert log.timestamp is not None
