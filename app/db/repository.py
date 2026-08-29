"""
Repository pour les operations CRUD sur la base de donnees.
Encapsule toute la logique d'acces aux donnees.
"""

import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.db.models import EmployeeData, Prediction, PredictionLog


class EmployeeRepository:
    """
    Repository pour les operations sur les donnees employe.

    Fournit une interface propre pour les operations CRUD
    sur la table employee_data.
    """

    def __init__(self, db: Session):
        """
        Initialise le repository avec une session de base de donnees.

        Parameters:
            db: Session SQLAlchemy active
        """
        self.db = db

    def create(self, data: Dict[str, Any]) -> EmployeeData:
        """
        Cree un nouvel enregistrement de donnees employe.

        Parameters:
            data: Dictionnaire contenant les donnees de l'employe

        Returns:
            EmployeeData: Instance creee et persistee
        """
        request_id = str(uuid.uuid4())

        employee = EmployeeData(
            request_id=request_id,
            age=data.get("age"),
            statut_marital=data.get("statut_marital"),
            ayant_enfants=data.get("ayant_enfants"),
            distance_domicile_travail=data.get("distance_domicile_travail"),
            departement=data.get("departement"),
            poste=data.get("poste"),
            niveau_hierarchique_poste=data.get("niveau_hierarchique_poste"),
            revenu_mensuel=data.get("revenu_mensuel"),
            heure_supplementaires=data.get("heure_supplementaires"),
            annee_experience_totale=data.get("annee_experience_totale"),
            annees_dans_le_poste_actuel=data.get("annees_dans_le_poste_actuel"),
            annees_dans_l_entreprise=data.get("annees_dans_l_entreprise"),
            annes_sous_responsable_actuel=data.get("annes_sous_responsable_actuel"),
            nombre_experiences_precedentes=data.get("nombre_experiences_precedentes"),
            annees_depuis_la_derniere_promotion=data.get("annees_depuis_la_derniere_promotion"),
            nb_formations_suivies=data.get("nb_formations_suivies"),
            note_evaluation_precedente=data.get("note_evaluation_precedente"),
            nombre_participation_pee=data.get("nombre_participation_pee"),
            satisfaction_employee_nature_travail=data.get("satisfaction_employee_nature_travail"),
            satisfaction_employee_environnement=data.get("satisfaction_employee_environnement"),
            satisfaction_employee_equilibre_pro_perso=data.get(
                "satisfaction_employee_equilibre_pro_perso"
            ),
            satisfaction_employee_equipe=data.get("satisfaction_employee_equipe"),
        )

        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)

        return employee

    def get_by_id(self, employee_id: int) -> Optional[EmployeeData]:
        """
        Recupere un employe par son ID.

        Parameters:
            employee_id: ID de l'employe

        Returns:
            EmployeeData ou None si non trouve
        """
        return self.db.query(EmployeeData).filter(EmployeeData.id == employee_id).first()

    def get_by_request_id(self, request_id: str) -> Optional[EmployeeData]:
        """
        Recupere un employe par son request_id.

        Parameters:
            request_id: UUID de la requete

        Returns:
            EmployeeData ou None si non trouve
        """
        return self.db.query(EmployeeData).filter(EmployeeData.request_id == request_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[EmployeeData]:
        """
        Recupere tous les employes avec pagination.

        Parameters:
            skip: Nombre d'enregistrements a sauter
            limit: Nombre maximum d'enregistrements a retourner

        Returns:
            Liste d'EmployeeData
        """
        return self.db.query(EmployeeData).offset(skip).limit(limit).all()


class PredictionRepository:
    """
    Repository pour les operations sur les predictions.

    Fournit une interface propre pour les operations CRUD
    sur la table predictions.
    """

    def __init__(self, db: Session):
        """
        Initialise le repository avec une session de base de donnees.

        Parameters:
            db: Session SQLAlchemy active
        """
        self.db = db

    def create(
        self,
        employee_data_id: int,
        probability: float,
        prediction_binary: int,
        risk_level: str,
        confidence: float,
        threshold_used: float,
        model_version: Optional[str] = None,
    ) -> Prediction:
        """
        Cree un nouvel enregistrement de prediction.

        Parameters:
            employee_data_id: ID des donnees employe associees
            probability: Probabilite de depart
            prediction_binary: Prediction binaire (0 ou 1)
            risk_level: Niveau de risque
            confidence: Confiance de la prediction
            threshold_used: Seuil utilise pour la prediction
            model_version: Version du modele utilise

        Returns:
            Prediction: Instance creee et persistee
        """
        prediction = Prediction(
            employee_data_id=employee_data_id,
            probability=probability,
            prediction_binary=prediction_binary,
            risk_level=risk_level,
            confidence=confidence,
            threshold_used=threshold_used,
            model_version=model_version,
        )

        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)

        return prediction

    def get_by_employee_id(self, employee_id: int) -> Optional[Prediction]:
        """
        Recupere la prediction associee a un employe.

        Parameters:
            employee_id: ID des donnees employe

        Returns:
            Prediction ou None si non trouvee
        """
        return self.db.query(Prediction).filter(Prediction.employee_data_id == employee_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Prediction]:
        """
        Recupere toutes les predictions avec pagination.

        Parameters:
            skip: Nombre d'enregistrements a sauter
            limit: Nombre maximum d'enregistrements a retourner

        Returns:
            Liste de Prediction
        """
        return self.db.query(Prediction).offset(skip).limit(limit).all()

    def count(self) -> int:
        """Retourne le nombre total de predictions persistees."""
        from sqlalchemy import func

        return int(self.db.query(func.count(Prediction.id)).scalar() or 0)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Calcule les statistiques globales des predictions.

        Returns:
            Dictionnaire avec les statistiques
        """
        from sqlalchemy import func

        total = self.db.query(func.count(Prediction.id)).scalar()
        avg_probability = self.db.query(func.avg(Prediction.probability)).scalar()
        high_risk_count = (
            self.db.query(func.count(Prediction.id))
            .filter(Prediction.risk_level.in_(["ELEVE", "TRES ELEVE", "ÉLEVÉ", "TRÈS ÉLEVÉ"]))
            .scalar()
        )

        return {
            "total_predictions": total or 0,
            "average_probability": round(avg_probability or 0, 4),
            "high_risk_count": high_risk_count or 0,
        }


class LogRepository:
    """
    Repository pour les logs de prediction.

    Fournit une interface pour l'enregistrement et la consultation
    des logs d'audit.
    """

    def __init__(self, db: Session):
        """
        Initialise le repository avec une session de base de donnees.

        Parameters:
            db: Session SQLAlchemy active
        """
        self.db = db

    def create(
        self,
        request_id: str,
        endpoint: str,
        method: str,
        status_code: int,
        client_ip: Optional[str] = None,
        response_time_ms: Optional[float] = None,
        error_message: Optional[str] = None,
    ) -> PredictionLog:
        """
        Cree un nouvel enregistrement de log.

        Parameters:
            request_id: UUID de la requete
            endpoint: Endpoint appele
            method: Methode HTTP
            status_code: Code de statut HTTP
            client_ip: Adresse IP du client
            response_time_ms: Temps de reponse en millisecondes
            error_message: Message d'erreur eventuel

        Returns:
            PredictionLog: Instance creee et persistee
        """
        log = PredictionLog(
            request_id=request_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            client_ip=client_ip,
            response_time_ms=response_time_ms,
            error_message=error_message,
        )

        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)

        return log
