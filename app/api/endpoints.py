"""
Endpoints de l'API de prediction du turnover.
Definit toutes les routes disponibles pour l'application.
"""

import time
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.schemas import (
    EmployeeDataRequest,
    ErrorResponse,
    HealthResponse,
    ModelInfoResponse,
    PredictionHistoryItem,
    PredictionHistoryResponse,
    PredictionResponse,
    StatisticsResponse,
)
from app.core.config import get_settings
from app.core.security import verify_api_key
from app.db.database import get_db
from app.db.repository import EmployeeRepository, LogRepository, PredictionRepository
from app.ml.predict import TurnoverPredictor

# Router principal
router = APIRouter()

# Settings
settings = get_settings()


def get_predictor() -> TurnoverPredictor:
    """
    Dependency pour obtenir une instance du predicteur.

    Returns:
        TurnoverPredictor: Instance du predicteur initialise
    """
    return TurnoverPredictor(
        model_path=settings.MODEL_PATH,
        scaler_path=settings.SCALER_PATH,
        threshold_path=settings.THRESHOLD_PATH,
        schema_path=settings.SCHEMA_PATH,
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Verifie l'etat de sante de l'application.",
    tags=["Monitoring"],
)
async def health_check():
    """
    Endpoint de verification de l'etat de sante.

    Retourne le statut de l'application, sa version et l'horodatage actuel.
    Utile pour les systemes de monitoring et les load balancers.
    """
    return HealthResponse(
        status="healthy", version=settings.APP_VERSION, timestamp=datetime.utcnow()
    )


@router.get(
    "/model/info",
    response_model=ModelInfoResponse,
    summary="Informations du Modele",
    description="Retourne les informations sur le modele de prediction utilise.",
    tags=["Modele"],
    responses={500: {"model": ErrorResponse, "description": "Erreur lors du chargement du modele"}},
)
async def get_model_info():
    """
    Endpoint pour obtenir les informations du modele.

    Retourne le type de modele, sa version, le seuil optimal utilise,
    le nombre de features et une description.
    """
    try:
        predictor = get_predictor()
        info = predictor.get_model_info()

        return ModelInfoResponse(
            model_type=info.get("model_type", "Unknown"),
            model_version=info.get("model_version", "1.0"),
            threshold=info.get("threshold", 0.5),
            n_features=info.get("n_features", 34),
            description=info.get("description", "Modele de prediction du turnover"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du chargement du modele: {str(e)}",
        )


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Prediction de Turnover",
    description="Effectue une prediction de turnover pour un employe.",
    tags=["Prediction"],
    responses={
        400: {"model": ErrorResponse, "description": "Donnees invalides"},
        500: {"model": ErrorResponse, "description": "Erreur lors de la prediction"},
    },
)
async def predict_turnover(
    request: Request,
    employee_data: EmployeeDataRequest,
    db: Session = Depends(get_db),
    _auth: None = Depends(verify_api_key),
):
    """
    Endpoint principal de prediction de turnover.

    Recoit les donnees d'un employe, les enregistre en base de donnees,
    effectue la prediction via le modele ML et retourne le resultat.

    Parameters:
        employee_data: Donnees de l'employe pour la prediction
        db: Session de base de donnees

    Returns:
        PredictionResponse: Resultat de la prediction avec probabilite et niveau de risque
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())

    try:
        # 1. Enregistrement des donnees en base
        employee_repo = EmployeeRepository(db)
        employee_record = employee_repo.create(employee_data.model_dump())

        # 2. Preparation des donnees pour le modele
        predictor = get_predictor()
        prediction_data = employee_data.model_dump()

        # 3. Execution de la prediction
        result = predictor.predict_single(prediction_data)

        # 4. Enregistrement de la prediction en base
        prediction_repo = PredictionRepository(db)
        prediction_repo.create(
            employee_data_id=employee_record.id,
            probability=result["probability"],
            prediction_binary=result["prediction_binary"],
            risk_level=result["risk_level"],
            confidence=result["confidence"],
            threshold_used=result["threshold"],
            model_version=predictor.schema.get("model_info", {}).get("version", "1.0"),
        )

        # 5. Logging de la requete
        response_time = (time.time() - start_time) * 1000
        log_repo = LogRepository(db)
        log_repo.create(
            request_id=employee_record.request_id,
            endpoint="/predict",
            method="POST",
            status_code=200,
            client_ip=request.client.host if request.client else None,
            response_time_ms=response_time,
        )

        # 6. Construction de la reponse
        return PredictionResponse(
            request_id=employee_record.request_id,
            prediction=result["prediction"],
            prediction_binary=result["prediction_binary"],
            probability=result["probability"],
            risk_level=result["risk_level"],
            confidence=result["confidence"],
            threshold=result["threshold"],
        )

    except ValueError as e:
        # Erreur de validation des donnees
        log_repo = LogRepository(db)
        log_repo.create(
            request_id=request_id,
            endpoint="/predict",
            method="POST",
            status_code=400,
            error_message=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Erreur de validation: {str(e)}"
        )

    except Exception as e:
        # Erreur interne
        log_repo = LogRepository(db)
        log_repo.create(
            request_id=request_id,
            endpoint="/predict",
            method="POST",
            status_code=500,
            error_message=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la prediction: {str(e)}",
        )


@router.get(
    "/predictions/{request_id}",
    response_model=PredictionResponse,
    summary="Recuperer une Prediction",
    description="Recupere une prediction existante par son identifiant de requete.",
    tags=["Prediction"],
    responses={404: {"model": ErrorResponse, "description": "Prediction non trouvee"}},
)
async def get_prediction(
    request_id: str,
    db: Session = Depends(get_db),
    _auth: None = Depends(verify_api_key),
):
    """
    Endpoint pour recuperer une prediction existante.

    Parameters:
        request_id: Identifiant unique de la requete
        db: Session de base de donnees

    Returns:
        PredictionResponse: Resultat de la prediction
    """
    employee_repo = EmployeeRepository(db)
    employee_record = employee_repo.get_by_request_id(request_id)

    if not employee_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction non trouvee pour request_id: {request_id}",
        )

    prediction_repo = PredictionRepository(db)
    prediction_record = prediction_repo.get_by_employee_id(employee_record.id)

    if not prediction_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction non trouvee pour request_id: {request_id}",
        )

    prediction_label = (
        "Risque de depart"
        if prediction_record.prediction_binary == 1
        else "Reste dans l'entreprise"
    )

    return PredictionResponse(
        request_id=request_id,
        prediction=prediction_label,
        prediction_binary=prediction_record.prediction_binary,
        probability=prediction_record.probability,
        risk_level=prediction_record.risk_level,
        confidence=prediction_record.confidence,
        threshold=prediction_record.threshold_used,
    )


@router.get(
    "/predictions",
    response_model=PredictionHistoryResponse,
    summary="Historique des Predictions",
    description="Recupere l'historique des predictions avec pagination.",
    tags=["Prediction"],
)
async def get_predictions_history(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _auth: None = Depends(verify_api_key),
):
    """
    Endpoint pour recuperer l'historique des predictions.

    Parameters:
        skip: Nombre d'enregistrements a sauter
        limit: Nombre maximum d'enregistrements
        db: Session de base de donnees

    Returns:
        PredictionHistoryResponse: Liste paginee des predictions
    """
    prediction_repo = PredictionRepository(db)
    predictions = prediction_repo.get_all(skip=skip, limit=limit)

    items = []
    for pred in predictions:
        employee = pred.employee_data
        items.append(
            PredictionHistoryItem(
                request_id=employee.request_id,
                created_at=pred.created_at,
                probability=pred.probability,
                risk_level=pred.risk_level,
                prediction_binary=pred.prediction_binary,
            )
        )

    return PredictionHistoryResponse(total=prediction_repo.count(), items=items)


@router.get(
    "/statistics",
    response_model=StatisticsResponse,
    summary="Statistiques des Predictions",
    description="Retourne les statistiques globales des predictions.",
    tags=["Monitoring"],
)
async def get_statistics(
    db: Session = Depends(get_db),
    _auth: None = Depends(verify_api_key),
):
    """
    Endpoint pour obtenir les statistiques globales.

    Returns:
        StatisticsResponse: Statistiques agregees des predictions
    """
    prediction_repo = PredictionRepository(db)
    stats = prediction_repo.get_statistics()

    return StatisticsResponse(**stats)
