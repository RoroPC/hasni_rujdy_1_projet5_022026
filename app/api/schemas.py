"""
Schemas Pydantic pour la validation et serialisation des donnees.
Definit les modeles de requete et de reponse pour l'API.
"""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class EmployeeDataRequest(BaseModel):
    """
    Schema de validation pour les donnees d'un employe.

    Represente toutes les features necessaires pour effectuer
    une prediction de turnover.
    """

    # Donnees demographiques
    age: int = Field(..., ge=18, le=70, description="Age de l'employe (entre 18 et 70 ans)")
    statut_marital: Literal["Célibataire", "Marié(e)", "Divorcé(e)"] = Field(
        ..., description="Statut marital de l'employe"
    )
    ayant_enfants: Literal["Oui", "Non"] = Field(
        default="Non", description="Indique si l'employe a des enfants (Oui/Non)"
    )
    distance_domicile_travail: int = Field(
        ..., ge=0, le=100, description="Distance entre le domicile et le travail en km"
    )

    # Donnees professionnelles
    departement: Literal["Développement", "Consulting", "Ressources Humaines"] = Field(
        ..., description="Departement de l'employe"
    )
    poste: Literal[
        "Développeur",
        "Cadre Commercial",
        "Consultant",
        "Directeur Technique",
        "Manager",
        "Représentant Commercial",
        "Ressources Humaines",
        "Senior Manager",
        "Tech Lead",
    ] = Field(..., description="Poste occupe par l'employe")
    niveau_hierarchique_poste: int = Field(
        ..., ge=1, le=5, description="Niveau hierarchique du poste (1 a 5)"
    )
    revenu_mensuel: int = Field(..., ge=0, description="Revenu mensuel de l'employe en euros")
    heure_supplementaires: Literal["Oui", "Non"] = Field(
        ..., description="Indique si l'employe fait des heures supplementaires (Oui/Non)"
    )

    # Experience
    annee_experience_totale: int = Field(
        ..., ge=0, le=50, description="Nombre total d'annees d'experience professionnelle"
    )
    annees_dans_le_poste_actuel: int = Field(
        ..., ge=0, description="Nombre d'annees dans le poste actuel"
    )
    annees_dans_l_entreprise: int = Field(
        ..., ge=0, description="Nombre d'annees dans l'entreprise"
    )
    annes_sous_responsable_actuel: int = Field(
        ..., ge=0, description="Nombre d'annees sous le responsable actuel"
    )
    nombre_experiences_precedentes: int = Field(
        ..., ge=0, description="Nombre d'experiences professionnelles precedentes"
    )
    annees_depuis_la_derniere_promotion: int = Field(
        ..., ge=0, description="Nombre d'annees depuis la derniere promotion"
    )

    # Formation et evaluation
    nb_formations_suivies: int = Field(..., ge=0, description="Nombre de formations suivies")
    note_evaluation_precedente: int = Field(
        ..., ge=1, le=4, description="Note de la derniere evaluation (1 a 4)"
    )
    nombre_participation_pee: int = Field(..., ge=0, description="Nombre de participations au PEE")

    # Satisfaction
    satisfaction_employee_nature_travail: int = Field(
        ..., ge=1, le=4, description="Satisfaction concernant la nature du travail (1 a 4)"
    )
    satisfaction_employee_environnement: int = Field(
        ..., ge=1, le=4, description="Satisfaction concernant l'environnement de travail (1 a 4)"
    )
    satisfaction_employee_equilibre_pro_perso: int = Field(
        ..., ge=1, le=4, description="Satisfaction concernant l'equilibre vie pro/perso (1 a 4)"
    )
    satisfaction_employee_equipe: int = Field(
        ..., ge=1, le=4, description="Satisfaction concernant l'equipe (1 a 4)"
    )

    @field_validator("statut_marital", mode="before")
    @classmethod
    def normalize_statut_marital(cls, value: str) -> str:
        """Normalise et valide les libelles utilises lors de l'entrainement."""
        mapping = {
            "celibataire": "Célibataire",
            "célibataire": "Célibataire",
            "marie(e)": "Marié(e)",
            "marié(e)": "Marié(e)",
            "divorce(e)": "Divorcé(e)",
            "divorcé(e)": "Divorcé(e)",
        }
        normalized = mapping.get(value.strip().lower())
        if normalized is None:
            raise ValueError("statut_marital doit etre Celibataire, Marie(e) ou Divorce(e)")
        return normalized

    @field_validator("departement", mode="before")
    @classmethod
    def normalize_departement(cls, value: str) -> str:
        """Normalise et valide le departement."""
        mapping = {
            "developpement": "Développement",
            "développement": "Développement",
            "consulting": "Consulting",
            "ressources humaines": "Ressources Humaines",
        }
        normalized = mapping.get(value.strip().lower())
        if normalized is None:
            raise ValueError(
                "departement doit etre Developpement, Consulting ou Ressources Humaines"
            )
        return normalized

    @field_validator("poste", mode="before")
    @classmethod
    def normalize_poste(cls, value: str) -> str:
        """Normalise et valide le poste."""
        values = {
            "developpeur": "Développeur",
            "développeur": "Développeur",
            "cadre commercial": "Cadre Commercial",
            "consultant": "Consultant",
            "directeur technique": "Directeur Technique",
            "manager": "Manager",
            "representant commercial": "Représentant Commercial",
            "représentant commercial": "Représentant Commercial",
            "ressources humaines": "Ressources Humaines",
            "senior manager": "Senior Manager",
            "tech lead": "Tech Lead",
        }
        normalized = values.get(value.strip().lower())
        if normalized is None:
            raise ValueError(
                "poste inconnu; consultez le schema OpenAPI pour les valeurs autorisees"
            )
        return normalized

    @field_validator("ayant_enfants", "heure_supplementaires", mode="before")
    @classmethod
    def normalize_oui_non(cls, value: str) -> str:
        """Normalise et valide les valeurs binaires Oui/Non."""
        mapping = {"oui": "Oui", "non": "Non", "yes": "Oui", "no": "Non"}
        normalized = mapping.get(value.strip().lower())
        if normalized is None:
            raise ValueError("la valeur doit etre Oui ou Non")
        return normalized

    model_config = {
        "json_schema_extra": {
            "example": {
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
        }
    }


class PredictionResponse(BaseModel):
    """
    Schema de reponse pour une prediction de turnover.

    Contient le resultat de la prediction ainsi que les metadonnees
    associees a la requete.
    """

    request_id: str = Field(..., description="Identifiant unique de la requete")
    prediction: str = Field(
        ..., description="Label de la prediction (Risque de depart / Reste dans l'entreprise)"
    )
    prediction_binary: int = Field(
        ..., ge=0, le=1, description="Prediction binaire (0 = reste, 1 = part)"
    )
    probability: float = Field(
        ..., ge=0.0, le=1.0, description="Probabilite de depart de l'employe"
    )
    risk_level: str = Field(..., description="Niveau de risque (FAIBLE, MODERE, ELEVE, TRES ELEVE)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiance de la prediction")
    threshold: float = Field(..., description="Seuil utilise pour la prediction")

    model_config = {
        "json_schema_extra": {
            "example": {
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "prediction": "Risque de depart",
                "prediction_binary": 1,
                "probability": 0.7234,
                "risk_level": "ELEVE",
                "confidence": 0.2361,
                "threshold": 0.36,
            }
        }
    }


class HealthResponse(BaseModel):
    """Schema de reponse pour le health check."""

    status: str = Field(..., description="Statut de l'application")
    version: str = Field(..., description="Version de l'application")
    timestamp: datetime = Field(..., description="Horodatage de la reponse")


class ModelInfoResponse(BaseModel):
    """Schema de reponse pour les informations du modele."""

    model_type: str = Field(..., description="Type du modele")
    model_version: str = Field(..., description="Version du modele")
    threshold: float = Field(..., description="Seuil optimal utilise")
    n_features: int = Field(..., description="Nombre de features attendues")
    description: str = Field(..., description="Description du modele")


class ErrorResponse(BaseModel):
    """Schema de reponse pour les erreurs."""

    error: str = Field(..., description="Type d'erreur")
    message: str = Field(..., description="Message d'erreur detaille")
    details: Optional[dict] = Field(None, description="Details supplementaires")


class PredictionHistoryItem(BaseModel):
    """Schema pour un element de l'historique des predictions."""

    request_id: str
    created_at: datetime
    probability: float
    risk_level: str
    prediction_binary: int


class PredictionHistoryResponse(BaseModel):
    """Schema de reponse pour l'historique des predictions."""

    total: int = Field(..., description="Nombre total de predictions")
    items: List[PredictionHistoryItem] = Field(..., description="Liste des predictions")


class StatisticsResponse(BaseModel):
    """Schema de reponse pour les statistiques."""

    total_predictions: int = Field(..., description="Nombre total de predictions")
    average_probability: float = Field(..., description="Probabilite moyenne de depart")
    high_risk_count: int = Field(..., description="Nombre de predictions a haut risque")
