"""Tests de l'authentification optionnelle par cle d'API."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app.core.security import verify_api_key


def test_api_key_is_optional_when_not_configured():
    """Le developpement local reste accessible sans secret."""
    with patch("app.core.security.get_settings", return_value=SimpleNamespace(API_KEY="")):
        assert verify_api_key(None) is None


def test_valid_api_key_is_accepted():
    """Une cle identique au secret configure est acceptee."""
    with patch("app.core.security.get_settings", return_value=SimpleNamespace(API_KEY="secret")):
        assert verify_api_key("secret") is None


def test_invalid_api_key_is_rejected():
    """Une cle absente ou incorrecte retourne une erreur 401."""
    with (
        patch("app.core.security.get_settings", return_value=SimpleNamespace(API_KEY="secret")),
        pytest.raises(HTTPException) as error,
    ):
        verify_api_key("wrong")

    assert error.value.status_code == 401
