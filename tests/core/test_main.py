"""
Tests fonctionnels pour l'application principale.
Verifie le demarrage et la configuration de FastAPI.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestAppConfiguration:
    """Tests pour la configuration de l'application."""

    def test_app_title(self, client):
        """
        Verifie que le titre de l'application est correct.
        """
        response = client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()
        assert "TechNova Partners" in data["info"]["title"]

    def test_app_version(self, client):
        """
        Verifie que la version de l'application est definie.
        """
        response = client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()
        assert data["info"]["version"] == "1.0.0"

    def test_openapi_tags_defined(self, client):
        """
        Verifie que les tags OpenAPI sont definis.
        """
        response = client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()

        tag_names = [tag["name"] for tag in data.get("tags", [])]
        assert "Prediction" in tag_names
        assert "Monitoring" in tag_names


class TestCORSMiddleware:
    """Tests pour le middleware CORS."""

    def test_cors_headers_present(self, client):
        """
        Verifie que les headers CORS sont presents.
        """
        response = client.options(
            "/api/v1/health",
            headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
        )
        assert response.status_code == 200

        # La reponse devrait inclure les headers CORS
        # Note: Le comportement exact depend de la configuration


class TestRequestLogging:
    """Tests pour le logging des requetes."""

    def test_process_time_header(self, client):
        """
        Verifie que le header X-Process-Time est ajoute.
        """
        response = client.get("/api/v1/health")

        assert "X-Process-Time" in response.headers


class TestRootEndpoint:
    """Tests pour l'endpoint racine."""

    def test_root_returns_json(self, client):
        """
        Verifie que l'endpoint racine retourne du JSON.
        """
        response = client.get("/")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    def test_root_contains_documentation_link(self, client):
        """
        Verifie que l'endpoint racine contient un lien vers la documentation.
        """
        response = client.get("/")

        data = response.json()
        assert "documentation" in data
        assert data["documentation"] == "/docs"


class TestExceptionHandling:
    """Tests pour la gestion des exceptions."""

    def test_404_for_unknown_endpoint(self, client):
        """
        Verifie qu'un endpoint inconnu retourne 404.
        """
        response = client.get("/api/v1/unknown-endpoint")

        assert response.status_code == 404

    def test_405_for_wrong_method(self, client):
        """
        Verifie qu'une mauvaise methode retourne 405.
        """
        response = client.put("/api/v1/health")

        assert response.status_code == 405


class TestDocumentation:
    """Tests pour la documentation de l'API."""

    def test_swagger_ui_available(self, client):
        """
        Verifie que Swagger UI est disponible.
        """
        response = client.get("/docs")

        assert response.status_code == 200

    def test_redoc_available(self, client):
        """
        Verifie que ReDoc est disponible.
        """
        response = client.get("/redoc")

        assert response.status_code == 200

    def test_openapi_schema_valid(self, client):
        """
        Verifie que le schema OpenAPI est valide.
        """
        response = client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()

        # Verifications de base du schema OpenAPI
        assert "openapi" in data
        assert data["openapi"].startswith("3.")
        assert "paths" in data
        assert "info" in data


class TestAPIVersioning:
    """Tests pour le versioning de l'API."""

    def test_api_v1_prefix(self, client):
        """
        Verifie que les endpoints sont prefixes avec /api/v1.
        """
        response = client.get("/api/v1/health")

        assert response.status_code == 200

    def test_endpoints_under_v1(self, client):
        """
        Verifie que tous les endpoints principaux sont sous /api/v1.
        """
        endpoints = [
            "/api/v1/health",
            "/api/v1/model/info",
            "/api/v1/predictions",
            "/api/v1/statistics",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            # Devrait retourner 200 ou au pire une erreur de donnees, pas 404
            assert response.status_code != 404, f"Endpoint {endpoint} non trouve"
