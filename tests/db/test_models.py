"""
Tests unitaires pour les modeles SQLAlchemy.
Verifie la structure et le comportement des modeles de base de donnees.
"""

import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.db.database import Base
from app.db.models import EmployeeData, Prediction, PredictionLog

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


class TestEmployeeDataModel:
    """Tests pour le modele EmployeeData."""

    def test_create_employee_data(self, db_session):
        """
        Verifie qu'un enregistrement EmployeeData peut etre cree.
        """
        employee = EmployeeData(
            request_id="test-request-id",
            age=35,
            statut_marital="Marie(e)",
            distance_domicile_travail=10,
            departement="Consulting",
            poste="Consultant",
            niveau_hierarchique_poste=2,
            revenu_mensuel=5000,
            heure_supplementaires="Oui",
            annee_experience_totale=10,
            annees_dans_le_poste_actuel=3,
            annees_dans_l_entreprise=5,
            annes_sous_responsable_actuel=2,
            nombre_experiences_precedentes=2,
            annees_depuis_la_derniere_promotion=1,
            nb_formations_suivies=2,
            note_evaluation_precedente=3,
            nombre_participation_pee=1,
            satisfaction_employee_nature_travail=3,
            satisfaction_employee_environnement=3,
            satisfaction_employee_equilibre_pro_perso=3,
            satisfaction_employee_equipe=3,
        )

        db_session.add(employee)
        db_session.commit()

        assert employee.id is not None
        assert employee.request_id == "test-request-id"

    def test_employee_data_auto_timestamp(self, db_session):
        """
        Verifie que le timestamp est automatiquement defini.
        """
        employee = EmployeeData(
            request_id="test-timestamp",
            age=30,
            statut_marital="Celibataire",
            distance_domicile_travail=5,
            departement="Developpement",
            poste="Developpeur",
            niveau_hierarchique_poste=1,
            revenu_mensuel=4000,
            heure_supplementaires="Non",
            annee_experience_totale=5,
            annees_dans_le_poste_actuel=2,
            annees_dans_l_entreprise=2,
            annes_sous_responsable_actuel=1,
            nombre_experiences_precedentes=1,
            annees_depuis_la_derniere_promotion=0,
            nb_formations_suivies=1,
            note_evaluation_precedente=3,
            nombre_participation_pee=0,
            satisfaction_employee_nature_travail=3,
            satisfaction_employee_environnement=3,
            satisfaction_employee_equilibre_pro_perso=3,
            satisfaction_employee_equipe=3,
        )

        db_session.add(employee)
        db_session.commit()

        # Le created_at devrait etre defini automatiquement
        assert employee.created_at is not None

    def test_employee_data_unique_request_id(self, db_session):
        """
        Verifie que request_id est unique.
        """
        employee1 = EmployeeData(
            request_id="unique-id",
            age=25,
            statut_marital="Celibataire",
            distance_domicile_travail=5,
            departement="Developpement",
            poste="Developpeur",
            niveau_hierarchique_poste=1,
            revenu_mensuel=3000,
            heure_supplementaires="Non",
            annee_experience_totale=3,
            annees_dans_le_poste_actuel=1,
            annees_dans_l_entreprise=1,
            annes_sous_responsable_actuel=1,
            nombre_experiences_precedentes=1,
            annees_depuis_la_derniere_promotion=0,
            nb_formations_suivies=1,
            note_evaluation_precedente=3,
            nombre_participation_pee=0,
            satisfaction_employee_nature_travail=3,
            satisfaction_employee_environnement=3,
            satisfaction_employee_equilibre_pro_perso=3,
            satisfaction_employee_equipe=3,
        )

        db_session.add(employee1)
        db_session.commit()

        employee2 = EmployeeData(
            request_id="unique-id",  # Meme ID
            age=30,
            statut_marital="Marie(e)",
            distance_domicile_travail=10,
            departement="Consulting",
            poste="Consultant",
            niveau_hierarchique_poste=2,
            revenu_mensuel=4000,
            heure_supplementaires="Oui",
            annee_experience_totale=5,
            annees_dans_le_poste_actuel=2,
            annees_dans_l_entreprise=2,
            annes_sous_responsable_actuel=1,
            nombre_experiences_precedentes=2,
            annees_depuis_la_derniere_promotion=1,
            nb_formations_suivies=2,
            note_evaluation_precedente=3,
            nombre_participation_pee=1,
            satisfaction_employee_nature_travail=3,
            satisfaction_employee_environnement=3,
            satisfaction_employee_equilibre_pro_perso=3,
            satisfaction_employee_equipe=3,
        )

        db_session.add(employee2)

        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()

    def test_employee_data_repr(self, db_session):
        """
        Verifie la representation string du modele.
        """
        employee = EmployeeData(
            request_id="repr-test",
            age=35,
            statut_marital="Marie(e)",
            distance_domicile_travail=10,
            departement="Consulting",
            poste="Consultant",
            niveau_hierarchique_poste=2,
            revenu_mensuel=5000,
            heure_supplementaires="Oui",
            annee_experience_totale=10,
            annees_dans_le_poste_actuel=3,
            annees_dans_l_entreprise=5,
            annes_sous_responsable_actuel=2,
            nombre_experiences_precedentes=2,
            annees_depuis_la_derniere_promotion=1,
            nb_formations_suivies=2,
            note_evaluation_precedente=3,
            nombre_participation_pee=1,
            satisfaction_employee_nature_travail=3,
            satisfaction_employee_environnement=3,
            satisfaction_employee_equilibre_pro_perso=3,
            satisfaction_employee_equipe=3,
        )

        db_session.add(employee)
        db_session.commit()

        repr_str = repr(employee)
        assert "EmployeeData" in repr_str
        assert "repr-test" in repr_str


class TestPredictionModel:
    """Tests pour le modele Prediction."""

    def test_create_prediction(self, db_session):
        """
        Verifie qu'une prediction peut etre creee.
        """
        # D'abord creer un employe
        employee = EmployeeData(
            request_id="pred-test",
            age=35,
            statut_marital="Marie(e)",
            distance_domicile_travail=10,
            departement="Consulting",
            poste="Consultant",
            niveau_hierarchique_poste=2,
            revenu_mensuel=5000,
            heure_supplementaires="Oui",
            annee_experience_totale=10,
            annees_dans_le_poste_actuel=3,
            annees_dans_l_entreprise=5,
            annes_sous_responsable_actuel=2,
            nombre_experiences_precedentes=2,
            annees_depuis_la_derniere_promotion=1,
            nb_formations_suivies=2,
            note_evaluation_precedente=3,
            nombre_participation_pee=1,
            satisfaction_employee_nature_travail=3,
            satisfaction_employee_environnement=3,
            satisfaction_employee_equilibre_pro_perso=3,
            satisfaction_employee_equipe=3,
        )

        db_session.add(employee)
        db_session.commit()

        # Creer la prediction
        prediction = Prediction(
            employee_data_id=employee.id,
            probability=0.7234,
            prediction_binary=1,
            risk_level="ELEVE",
            confidence=0.2361,
            threshold_used=0.4873,
            model_version="2.0",
        )

        db_session.add(prediction)
        db_session.commit()

        assert prediction.id is not None
        assert prediction.probability == 0.7234

    def test_prediction_employee_relationship(self, db_session):
        """
        Verifie la relation entre Prediction et EmployeeData.
        """
        employee = EmployeeData(
            request_id="rel-test",
            age=30,
            statut_marital="Celibataire",
            distance_domicile_travail=15,
            departement="Developpement",
            poste="Developpeur",
            niveau_hierarchique_poste=1,
            revenu_mensuel=4000,
            heure_supplementaires="Non",
            annee_experience_totale=5,
            annees_dans_le_poste_actuel=2,
            annees_dans_l_entreprise=3,
            annes_sous_responsable_actuel=2,
            nombre_experiences_precedentes=1,
            annees_depuis_la_derniere_promotion=1,
            nb_formations_suivies=3,
            note_evaluation_precedente=3,
            nombre_participation_pee=1,
            satisfaction_employee_nature_travail=3,
            satisfaction_employee_environnement=4,
            satisfaction_employee_equilibre_pro_perso=3,
            satisfaction_employee_equipe=4,
        )

        db_session.add(employee)
        db_session.commit()

        prediction = Prediction(
            employee_data_id=employee.id,
            probability=0.35,
            prediction_binary=0,
            risk_level="MODERE",
            confidence=0.15,
            threshold_used=0.5,
        )

        db_session.add(prediction)
        db_session.commit()

        # Verifier la relation
        assert prediction.employee_data.id == employee.id
        assert employee.prediction.id == prediction.id


class TestPredictionLogModel:
    """Tests pour le modele PredictionLog."""

    def test_create_prediction_log(self, db_session):
        """
        Verifie qu'un log peut etre cree.
        """
        log = PredictionLog(
            request_id="log-test",
            endpoint="/predict",
            method="POST",
            status_code=200,
            client_ip="127.0.0.1",
            response_time_ms=150.5,
        )

        db_session.add(log)
        db_session.commit()

        assert log.id is not None
        assert log.endpoint == "/predict"

    def test_prediction_log_with_error(self, db_session):
        """
        Verifie qu'un log avec erreur peut etre cree.
        """
        log = PredictionLog(
            request_id="error-log-test",
            endpoint="/predict",
            method="POST",
            status_code=500,
            error_message="Internal server error",
        )

        db_session.add(log)
        db_session.commit()

        assert log.error_message == "Internal server error"

    def test_prediction_log_repr(self, db_session):
        """
        Verifie la representation string du log.
        """
        log = PredictionLog(
            request_id="repr-log-test", endpoint="/health", method="GET", status_code=200
        )

        db_session.add(log)
        db_session.commit()

        repr_str = repr(log)
        assert "PredictionLog" in repr_str
        assert "200" in repr_str
