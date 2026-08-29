"""
Module de prédiction pour le modèle de turnover.
Encapsule le chargement du modèle, le preprocessing et la prédiction.

Author: TechNova Partners - HR Analytics
Date: 2026-02-05
Version: 1.0
"""

import json
import logging
import pickle
from pathlib import Path
from typing import Dict, List, Union

import numpy as np
import pandas as pd

from .preprocessing import TurnoverDataPreprocessor, prepare_single_prediction

logger = logging.getLogger(__name__)


class TurnoverPredictor:
    """
    Classe pour effectuer des prédictions de turnover.

    Encapsule:
    - Chargement du modèle et du scaler
    - Preprocessing des données
    - Prédiction avec seuil optimal
    - Interprétation des résultats
    """

    def __init__(
        self,
        model_path: str = "best_model_v2.pkl",
        scaler_path: str = "scaler.pkl",
        threshold_path: str = "seuil_optimal.txt",
        schema_path: str = "features_schema.json",
    ):
        """
        Initialise le prédicteur en chargeant les artifacts.

        Parameters:
        -----------
        model_path : str
            Chemin vers le fichier du modèle (.pkl)
        scaler_path : str
            Chemin vers le fichier du scaler (.pkl)
        threshold_path : str
            Chemin vers le fichier du seuil optimal (.txt)
        schema_path : str
            Chemin vers le schéma des features (.json)
        """
        self.model_path = Path(model_path)
        self.scaler_path = Path(scaler_path)
        self.threshold_path = Path(threshold_path)
        self.schema_path = Path(schema_path)

        # Charger les artifacts
        self.model = self._load_model()
        self.scaler = self._load_scaler()
        self.threshold = self._load_threshold()
        self.schema = self._load_schema()

        # Initialiser le preprocessor
        self.preprocessor = TurnoverDataPreprocessor()
        self._validate_artifacts()

        logger.info(
            "Predicteur initialise: modele=%s, seuil=%.4f",
            self.model_path.name,
            self.threshold,
        )

    def _validate_artifacts(self) -> None:
        """Verifie la compatibilite des artefacts avec le preprocessing."""
        expected_count = len(self.preprocessor.expected_features)
        for label, artifact in (("modele", self.model), ("scaler", self.scaler)):
            artifact_count = getattr(artifact, "n_features_in_", expected_count)
            if isinstance(artifact_count, (int, np.integer)) and artifact_count != expected_count:
                raise ValueError(
                    f"Incompatibilite {label}: {artifact_count} features au lieu de {expected_count}"
                )

    def _load_model(self):
        """Charge le modèle depuis le fichier pickle."""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Modèle non trouvé: {self.model_path}")

        with open(self.model_path, "rb") as f:
            model = pickle.load(f)

        return model

    def _load_scaler(self):
        """Charge le scaler depuis le fichier pickle."""
        if not self.scaler_path.exists():
            raise FileNotFoundError(f"Scaler non trouvé: {self.scaler_path}")

        with open(self.scaler_path, "rb") as f:
            scaler = pickle.load(f)

        return scaler

    def _load_threshold(self) -> float:
        """Charge le seuil optimal depuis le fichier texte."""
        if not self.threshold_path.exists():
            logger.warning(
                "Seuil non trouve (%s), utilisation de 0.5 par defaut",
                self.threshold_path,
            )
            return 0.5

        with open(self.threshold_path, "r") as f:
            threshold = float(f.read().strip())

        return threshold

    def _load_schema(self) -> Dict:
        """Charge le schéma des features depuis le fichier JSON."""
        if not self.schema_path.exists():
            logger.warning("Schema non trouve: %s", self.schema_path)
            return {}

        with open(self.schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        return schema

    def preprocess(self, data: Union[Dict, pd.DataFrame]) -> pd.DataFrame:
        """
        Preprocessing des données d'entrée.

        Parameters:
        -----------
        data : Union[Dict, pd.DataFrame]
            Données à preprocesser (dict pour une prédiction, DataFrame pour batch)

        Returns:
        --------
        pd.DataFrame
            Données preprocessées
        """
        # Si c'est un dictionnaire, le convertir en DataFrame
        if isinstance(data, dict):
            data = prepare_single_prediction(data)
        elif isinstance(data, pd.DataFrame):
            data = self.preprocessor.transform(data, validate=True)
        else:
            raise ValueError("data doit être un Dict ou un DataFrame")

        return data

    def predict_proba(self, features: pd.DataFrame) -> np.ndarray:
        """
        Prédit les probabilités de départ.

        Parameters:
        -----------
        X : pd.DataFrame
            Features preprocessées

        Returns:
        --------
        np.ndarray
            Probabilités de départ (classe 1)
        """
        # Standardiser les features
        features_scaled = self.scaler.transform(features)

        # Prédire les probabilités
        probas = self.model.predict_proba(features_scaled)[:, 1]

        return probas

    def predict(self, features: pd.DataFrame) -> np.ndarray:
        """
        Prédit les classes (départ ou non) avec le seuil optimal.

        Parameters:
        -----------
        X : pd.DataFrame
            Features preprocessées

        Returns:
        --------
        np.ndarray
            Prédictions binaires (0=reste, 1=part)
        """
        # Obtenir les probabilités
        probas = self.predict_proba(features)

        # Appliquer le seuil
        predictions = (probas >= self.threshold).astype(int)

        return predictions

    def predict_single(self, data: Dict) -> Dict:
        """
        Effectue une prédiction pour un employé unique et retourne un résultat détaillé.

        Parameters:
        -----------
        data : Dict
            Données d'un employé

        Returns:
        --------
        Dict
            Résultat de la prédiction avec détails

        Example:
        --------
        >>> predictor = TurnoverPredictor()
        >>> result = predictor.predict_single({
        ...     'age': 35,
        ...     'revenu_mensuel': 5000,
        ...     ...
        ... })
        >>> print(result)
        {
            'prediction': 'Risque de départ',
            'probability': 0.73,
            'risk_level': 'ÉLEVÉ',
            'confidence': 0.46
        }
        """
        # Preprocessing
        features = self.preprocess(data)

        # Prédiction
        proba = self.predict_proba(features)[0]
        pred = int(proba >= self.threshold)

        # Interprétation
        prediction_label = "Risque de départ" if pred == 1 else "Reste dans l'entreprise"

        # Niveau de risque basé sur la probabilité
        if proba >= 0.7:
            risk_level = "TRÈS ÉLEVÉ"
        elif proba >= 0.5:
            risk_level = "ÉLEVÉ"
        elif proba >= 0.3:
            risk_level = "MODÉRÉ"
        else:
            risk_level = "FAIBLE"

        # Confiance = distance au seuil
        confidence = abs(proba - self.threshold)

        result = {
            "prediction": prediction_label,
            "prediction_binary": int(pred),
            "probability": round(float(proba), 4),
            "risk_level": risk_level,
            "confidence": round(float(confidence), 4),
            "threshold": self.threshold,
        }

        return result

    def predict_batch(self, data: Union[pd.DataFrame, str]) -> pd.DataFrame:
        """
        Effectue des prédictions pour un batch d'employés.

        Parameters:
        -----------
        data : Union[pd.DataFrame, str]
            DataFrame ou chemin vers un fichier CSV

        Returns:
        --------
        pd.DataFrame
            DataFrame avec les prédictions ajoutées
        """
        # Charger les données si c'est un chemin
        if isinstance(data, str):
            source_path = data
            data = pd.read_csv(source_path)
            logger.info("%s observations chargees depuis %s", len(data), source_path)

        # Preprocessing
        features = self.preprocess(data)

        # Prédictions
        probas = self.predict_proba(features)
        preds = self.predict(features)

        # Créer le DataFrame de résultats
        results = pd.DataFrame(
            {
                "prediction": preds,
                "probability": probas,
                "risk_level": pd.cut(
                    probas,
                    bins=[-np.inf, 0.3, 0.5, 0.7, np.inf],
                    labels=["FAIBLE", "MODÉRÉ", "ÉLEVÉ", "TRÈS ÉLEVÉ"],
                ),
            }
        )

        # Ajouter les résultats aux données originales
        results_final = pd.concat([data.reset_index(drop=True), results], axis=1)

        return results_final

    def get_feature_names(self) -> List[str]:
        """Retourne la liste des noms de features attendues."""
        return self.preprocessor.expected_features

    def get_model_info(self) -> Dict:
        """Retourne les informations sur le modèle."""
        info = {
            "model_type": type(self.model).__name__,
            "threshold": self.threshold,
            "n_features": len(self.preprocessor.expected_features),
            "feature_names": self.preprocessor.expected_features[:5] + ["..."],
        }

        if self.schema:
            info.update(
                {
                    "model_version": self.schema.get("model_info", {}).get("version", "unknown"),
                    "description": self.schema.get("model_info", {}).get("description", ""),
                }
            )

        return info


def example_usage():
    """Exemples d'utilisation du TurnoverPredictor."""

    print("=" * 70)
    print("EXEMPLES D'UTILISATION DU TURNOVERPREDICTOR")
    print("=" * 70)

    # Initialiser le prédicteur
    try:
        predictor = TurnoverPredictor()
    except FileNotFoundError as e:
        print(f"Erreur: {e}")
        print("Assurez-vous que les fichiers suivants sont présents:")
        print("  - best_model_v2.pkl")
        print("  - scaler.pkl")
        print("  - seuil_optimal.txt")
        print("  - features_schema.json")
        return

    # Exemple 1: Prédiction unique
    print("\n" + "=" * 70)
    print("EXEMPLE 1: Prédiction pour un employé unique")
    print("=" * 70)

    employee_data = {
        "age": 28,
        "revenu_mensuel": 3500,
        "statut_marital": "Célibataire",
        "departement": "Consulting",
        "poste": "Consultant",
        "heure_supplementaires": "Oui",
        "annee_experience_totale": 5,
        "niveau_hierarchique_poste": 1,
        "annees_dans_le_poste_actuel": 3,
        "annes_sous_responsable_actuel": 2,
        "nombre_participation_pee": 0,
        "annees_dans_l_entreprise": 3,
        "note_evaluation_precedente": 2,
        "satisfaction_employee_nature_travail": 2,
        "satisfaction_employee_environnement": 2,
        "distance_domicile_travail": 20,
        "satisfaction_employee_equilibre_pro_perso": 2,
        "nb_formations_suivies": 1,
        "satisfaction_employee_equipe": 2,
        "nombre_experiences_precedentes": 2,
        "annees_depuis_la_derniere_promotion": 3,
        "ayant_enfants": "Non",
    }

    try:
        result = predictor.predict_single(employee_data)
        print("\nRésultat de la prédiction:")
        for key, value in result.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"Erreur lors de la prédiction: {e}")

    # Exemple 2: Informations sur le modèle
    print("\n" + "=" * 70)
    print("EXEMPLE 2: Informations sur le modèle")
    print("=" * 70)

    model_info = predictor.get_model_info()
    print("\nInformations du modèle:")
    for key, value in model_info.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 70)
    print("EXEMPLES TERMINÉS")
    print("=" * 70)


if __name__ == "__main__":
    example_usage()
