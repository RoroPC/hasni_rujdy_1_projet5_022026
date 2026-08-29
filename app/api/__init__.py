"""
Module API de l'application.

Contient les endpoints FastAPI, les schemas Pydantic
et la logique de routage.
"""

from app.api.endpoints import router
from app.api.schemas import (
    EmployeeDataRequest,
    ErrorResponse,
    HealthResponse,
    ModelInfoResponse,
    PredictionResponse,
)

__all__ = [
    "router",
    "EmployeeDataRequest",
    "PredictionResponse",
    "HealthResponse",
    "ModelInfoResponse",
    "ErrorResponse",
]
