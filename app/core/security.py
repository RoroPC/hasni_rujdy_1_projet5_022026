"""Dependances de securite de l'API."""

import secrets

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import get_settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str | None = Security(api_key_header)) -> None:
    """Valide la cle d'API quand ``API_KEY`` est configuree.

    Le mode developpement reste utilisable sans secret lorsque ``API_KEY`` est
    vide. En staging et en production, la variable doit etre fournie par le
    gestionnaire de secrets de la plateforme.
    """
    expected_key = get_settings().API_KEY
    if not expected_key:
        return

    if api_key is None or not secrets.compare_digest(api_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cle d'API absente ou invalide",
        )
