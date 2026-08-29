"""
Modeles SQLAlchemy pour la base de donnees.
Definit les tables pour stocker les donnees des employes et les predictions.
"""

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class EmployeeData(Base):
    """
    Modele representant les donnees d'un employe soumises pour prediction.

    Stocke toutes les features necessaires au modele de prediction
    ainsi que les metadonnees de la requete.
    """

    __tablename__ = "employee_data"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Metadonnees
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    request_id = Column(String(36), unique=True, index=True, nullable=False)

    # Donnees demographiques
    age = Column(Integer, nullable=False)
    statut_marital = Column(String(50), nullable=False)
    ayant_enfants = Column(String(10), nullable=True)
    distance_domicile_travail = Column(Integer, nullable=False)

    # Donnees professionnelles
    departement = Column(String(100), nullable=False)
    poste = Column(String(100), nullable=False)
    niveau_hierarchique_poste = Column(Integer, nullable=False)
    revenu_mensuel = Column(Integer, nullable=False)
    heure_supplementaires = Column(String(10), nullable=False)

    # Experience
    annee_experience_totale = Column(Integer, nullable=False)
    annees_dans_le_poste_actuel = Column(Integer, nullable=False)
    annees_dans_l_entreprise = Column(Integer, nullable=False)
    annes_sous_responsable_actuel = Column(Integer, nullable=False)
    nombre_experiences_precedentes = Column(Integer, nullable=False)
    annees_depuis_la_derniere_promotion = Column(Integer, nullable=False)

    # Formation et evaluation
    nb_formations_suivies = Column(Integer, nullable=False)
    note_evaluation_precedente = Column(Integer, nullable=False)
    nombre_participation_pee = Column(Integer, nullable=False)

    # Satisfaction
    satisfaction_employee_nature_travail = Column(Integer, nullable=False)
    satisfaction_employee_environnement = Column(Integer, nullable=False)
    satisfaction_employee_equilibre_pro_perso = Column(Integer, nullable=False)
    satisfaction_employee_equipe = Column(Integer, nullable=False)

    # Relation avec la prediction
    prediction = relationship(
        "Prediction",
        back_populates="employee_data",
        cascade="all, delete-orphan",
        uselist=False,
    )

    def __repr__(self) -> str:
        return f"<EmployeeData(id={self.id}, request_id={self.request_id})>"


class Prediction(Base):
    """
    Modele representant le resultat d'une prediction de turnover.

    Stocke la probabilite de depart, la prediction binaire,
    le niveau de risque et les metadonnees du modele utilise.
    """

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Metadonnees
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Cle etrangere vers les donnees employe
    employee_data_id = Column(
        Integer,
        ForeignKey("employee_data.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Resultats de la prediction
    probability = Column(Float, nullable=False)
    prediction_binary = Column(Integer, nullable=False)
    risk_level = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    threshold_used = Column(Float, nullable=False)

    # Informations sur le modele
    model_version = Column(String(20), nullable=True)

    # Relation inverse
    employee_data = relationship("EmployeeData", back_populates="prediction")

    def __repr__(self) -> str:
        return f"<Prediction(id={self.id}, probability={self.probability}, risk={self.risk_level})>"


class PredictionLog(Base):
    """
    Modele pour le logging des predictions.

    Permet de tracer l'historique des appels a l'API
    pour audit et monitoring.
    """

    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Metadonnees
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    request_id = Column(String(36), index=True, nullable=False)

    # Informations de la requete
    endpoint = Column(String(100), nullable=False)
    method = Column(String(10), nullable=False)
    client_ip = Column(String(45), nullable=True)

    # Resultat
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<PredictionLog(id={self.id}, request_id={self.request_id}, status={self.status_code})>"
