"""
Tests unitaires pour les endpoints de l'API.
Verifie le comportement des routes FastAPI.
"""

from unittest.mock import patch

from fastapi import status


class TestHealthEndpoint:
    """Tests pour l'endpoint de health check."""

    def test_health_check_returns_healthy_status(self, client):
        """
        Verifie que l'endpoint /health retourne un statut healthy.
        """
        response = client.get("/api/v1/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    def test_health_check_returns_correct_version(self, client):
        """
        Verifie que l'endpoint /health retourne la bonne version.
        """
        response = client.get("/api/v1/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["version"] == "1.0.0"


class TestModelInfoEndpoint:
    """Tests pour l'endpoint d'information du modele."""

    @patch("app.api.endpoints.get_predictor")
    def test_model_info_returns_correct_structure(self, mock_get_predictor, client, mock_predictor):
        """
        Verifie que l'endpoint /model/info retourne la structure attendue.
        """
        mock_get_predictor.return_value = mock_predictor

        response = client.get("/api/v1/model/info")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "model_type" in data
        assert "model_version" in data
        assert "threshold" in data
        assert "n_features" in data
        assert "description" in data

    @patch("app.api.endpoints.get_predictor")
    def test_model_info_returns_correct_values(self, mock_get_predictor, client, mock_predictor):
        """
        Verifie que l'endpoint /model/info retourne les valeurs correctes.
        """
        mock_get_predictor.return_value = mock_predictor

        response = client.get("/api/v1/model/info")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["n_features"] == 34
        assert data["model_version"] == "2.0"


class TestPredictEndpoint:
    """Tests pour l'endpoint de prediction."""

    @patch("app.api.endpoints.get_predictor")
    def test_predict_with_valid_data_returns_prediction(
        self, mock_get_predictor, client, sample_employee_data, mock_predictor
    ):
        """
        Verifie qu'une prediction est retournee pour des donnees valides.
        """
        mock_get_predictor.return_value = mock_predictor

        response = client.post("/api/v1/predict", json=sample_employee_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "request_id" in data
        assert "prediction" in data
        assert "probability" in data
        assert "risk_level" in data

    @patch("app.api.endpoints.get_predictor")
    def test_predict_returns_valid_probability(
        self, mock_get_predictor, client, sample_employee_data, mock_predictor
    ):
        """
        Verifie que la probabilite retournee est valide.
        """
        mock_get_predictor.return_value = mock_predictor

        response = client.post("/api/v1/predict", json=sample_employee_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 0 <= data["probability"] <= 1

    @patch("app.api.endpoints.get_predictor")
    def test_predict_returns_valid_risk_level(
        self, mock_get_predictor, client, sample_employee_data, mock_predictor
    ):
        """
        Verifie que le niveau de risque retourne est valide.
        """
        mock_get_predictor.return_value = mock_predictor

        response = client.post("/api/v1/predict", json=sample_employee_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["risk_level"] in ["FAIBLE", "MODERE", "ELEVE", "TRES ELEVE"]

    def test_predict_with_missing_fields_returns_error(self, client):
        """
        Verifie qu'une erreur est retournee pour des donnees incompletes.
        """
        incomplete_data = {
            "age": 35,
            "statut_marital": "Marie(e)",
            # Autres champs manquants
        }

        response = client.post("/api/v1/predict", json=incomplete_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_predict_with_invalid_age_returns_error(self, client, sample_employee_data):
        """
        Verifie qu'une erreur est retournee pour un age invalide.
        """
        invalid_data = sample_employee_data.copy()
        invalid_data["age"] = 15  # Age inferieur au minimum

        response = client.post("/api/v1/predict", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_predict_with_invalid_satisfaction_returns_error(self, client, sample_employee_data):
        """
        Verifie qu'une erreur est retournee pour une satisfaction invalide.
        """
        invalid_data = sample_employee_data.copy()
        invalid_data["satisfaction_employee_nature_travail"] = 5  # Valeur hors plage

        response = client.post("/api/v1/predict", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_predict_with_unknown_category_returns_error(self, client, sample_employee_data):
        """Verifie qu'une categorie absente du vocabulaire est refusee."""
        invalid_data = sample_employee_data.copy()
        invalid_data["poste"] = "Astronaute"

        response = client.post("/api/v1/predict", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetPredictionEndpoint:
    """Tests pour l'endpoint de recuperation de prediction."""

    def test_get_prediction_not_found_returns_404(self, client):
        """
        Verifie qu'une erreur 404 est retournee pour une prediction inexistante.
        """
        response = client.get("/api/v1/predictions/nonexistent-id")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPredictionsHistoryEndpoint:
    """Tests pour l'endpoint d'historique des predictions."""

    def test_predictions_history_returns_list(self, client):
        """
        Verifie que l'historique retourne une liste.
        """
        response = client.get("/api/v1/predictions")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total" in data
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_predictions_history_pagination(self, client):
        """
        Verifie que la pagination fonctionne correctement.
        """
        response = client.get("/api/v1/predictions?skip=0&limit=10")

        assert response.status_code == status.HTTP_200_OK


class TestStatisticsEndpoint:
    """Tests pour l'endpoint de statistiques."""

    def test_statistics_returns_correct_structure(self, client):
        """
        Verifie que les statistiques retournent la structure attendue.
        """
        response = client.get("/api/v1/statistics")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_predictions" in data
        assert "average_probability" in data
        assert "high_risk_count" in data


class TestRootEndpoint:
    """Tests pour l'endpoint racine."""

    def test_root_returns_welcome_message(self, client):
        """
        Verifie que l'endpoint racine retourne un message de bienvenue.
        """
        response = client.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "documentation" in data
        assert "version" in data
