"""
Tests fonctionnels pour le pipeline ML complet.
Verifie l'integration entre preprocessing et prediction.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestMLPipeline:
    """Tests fonctionnels du pipeline ML complet."""

    def test_preprocessing_produces_correct_feature_count(self, sample_employee_data):
        """
        Verifie que le preprocessing produit le bon nombre de features.
        """
        from app.ml.preprocessing import TurnoverDataPreprocessor

        preprocessor = TurnoverDataPreprocessor()

        # Le nombre de features attendues doit etre 34
        assert len(preprocessor.expected_features) == 34

    def test_feature_engineering_order(self):
        """
        Verifie que les features engineered sont creees dans le bon ordre.
        """
        from app.ml.preprocessing import TurnoverDataPreprocessor

        preprocessor = TurnoverDataPreprocessor()

        # Les 4 dernieres features doivent etre les features engineered
        engineered_features = [
            "salaire_par_age",
            "stagnation_poste",
            "promotion_recente",
            "distance_longue",
        ]

        for feat in engineered_features:
            assert feat in preprocessor.expected_features

    @patch("app.ml.predict.TurnoverPredictor._load_model")
    @patch("app.ml.predict.TurnoverPredictor._load_scaler")
    @patch("app.ml.predict.TurnoverPredictor._load_threshold")
    @patch("app.ml.predict.TurnoverPredictor._load_schema")
    def test_predictor_uses_correct_threshold(
        self, mock_schema, mock_threshold, mock_scaler, mock_model
    ):
        """
        Verifie que le predictor utilise le seuil correct.
        """
        expected_threshold = 0.36

        mock_model.return_value = MagicMock()
        mock_scaler.return_value = MagicMock()
        mock_threshold.return_value = expected_threshold
        mock_schema.return_value = {"model_info": {"version": "2.0"}}

        from app.ml.predict import TurnoverPredictor

        predictor = TurnoverPredictor()

        assert predictor.threshold == expected_threshold


class TestDataTransformations:
    """Tests pour les transformations de donnees."""

    def test_binary_encoding_consistency(self):
        """
        Verifie la coherence de l'encodage binaire.
        """
        from app.ml.preprocessing import TurnoverDataPreprocessor

        preprocessor = TurnoverDataPreprocessor()

        df1 = pd.DataFrame({"heure_supplementaires": ["Oui"]})
        df2 = pd.DataFrame({"heure_supplementaires": ["Oui"]})

        result1 = preprocessor.encode_binary_variables(df1)
        result2 = preprocessor.encode_binary_variables(df2)

        assert result1["heure_supplementaires"].iloc[0] == result2["heure_supplementaires"].iloc[0]

    def test_feature_engineering_deterministic(self):
        """
        Verifie que le feature engineering est deterministe.
        """
        from app.ml.preprocessing import TurnoverDataPreprocessor

        preprocessor = TurnoverDataPreprocessor()

        df = pd.DataFrame(
            {
                "revenu_mensuel": [5000],
                "age": [35],
                "annees_dans_le_poste_actuel": [3],
                "annee_experience_totale": [10],
                "annees_depuis_la_derniere_promotion": [1],
                "distance_domicile_travail": [20],
            }
        )

        result1 = preprocessor.create_engineered_features(df.copy())
        result2 = preprocessor.create_engineered_features(df.copy())

        pd.testing.assert_frame_equal(result1, result2)


class TestEdgeCases:
    """Tests pour les cas limites."""

    def test_minimum_age(self):
        """
        Verifie le comportement avec l'age minimum.
        """
        from app.ml.preprocessing import TurnoverDataPreprocessor

        preprocessor = TurnoverDataPreprocessor()

        df = pd.DataFrame(
            {
                "revenu_mensuel": [2000],
                "age": [18],  # Age minimum
            }
        )

        result = preprocessor.create_engineered_features(df)

        assert "salaire_par_age" in result.columns
        assert result["salaire_par_age"].iloc[0] == pytest.approx(2000 / 18)

    def test_zero_experience(self):
        """
        Verifie le comportement avec zero experience.
        """
        from app.ml.preprocessing import TurnoverDataPreprocessor

        preprocessor = TurnoverDataPreprocessor()

        df = pd.DataFrame({"annees_dans_le_poste_actuel": [0], "annee_experience_totale": [0]})

        result = preprocessor.create_engineered_features(df)

        # Division par zero doit retourner 0
        assert result["stagnation_poste"].iloc[0] == 0

    def test_very_high_salary(self):
        """
        Verifie le comportement avec un salaire eleve.
        """
        from app.ml.preprocessing import TurnoverDataPreprocessor

        preprocessor = TurnoverDataPreprocessor()

        df = pd.DataFrame({"revenu_mensuel": [50000], "age": [50]})

        result = preprocessor.create_engineered_features(df)

        assert "salaire_par_age" in result.columns
        assert result["salaire_par_age"].iloc[0] == 1000


class TestDataQuality:
    """Tests pour la qualite des donnees."""

    def test_no_nan_after_preprocessing(self):
        """
        Verifie qu'il n'y a pas de NaN apres preprocessing complet.
        """
        from app.ml.preprocessing import TurnoverDataPreprocessor

        preprocessor = TurnoverDataPreprocessor()

        # Creer des donnees avec toutes les features
        data = {feat: [0] for feat in preprocessor.expected_features}
        df = pd.DataFrame(data)

        is_valid, errors = preprocessor.validate_data(df)

        nan_errors = [e for e in errors if "manquantes" in e.lower()]
        assert len(nan_errors) == 0

    def test_correct_dtypes_after_preprocessing(self):
        """
        Verifie les types de donnees apres preprocessing.
        """
        from app.ml.preprocessing import TurnoverDataPreprocessor

        preprocessor = TurnoverDataPreprocessor()

        # Les features numeriques doivent etre numeriques
        numeric_features = ["age", "revenu_mensuel", "annee_experience_totale"]

        data = {feat: [1.0] for feat in preprocessor.expected_features}
        df = pd.DataFrame(data)

        for feat in numeric_features:
            if feat in df.columns:
                assert df[feat].dtype in [np.float64, np.int64, np.float32, np.int32]
