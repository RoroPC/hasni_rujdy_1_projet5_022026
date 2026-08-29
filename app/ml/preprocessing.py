"""
Module de preprocessing pour le modèle de prédiction du turnover.
Contient toutes les transformations appliquées aux données brutes.
"""

import logging
from typing import Dict, List, Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


class TurnoverDataPreprocessor:
    """
    Classe pour preprocesser les données RH pour la prédiction du turnover.

    Cette classe encapsule toutes les transformations :
    - Gestion des valeurs manquantes
    - Encodage des variables binaires et catégorielles
    - Feature engineering
    - Sélection des features finales
    """

    def __init__(self):
        """Initialise le preprocessor avec les configurations."""

        # Colonnes à exclure (identifiants et target)
        self.colonnes_exclues = [
            "id_employee",
            "eval_number",
            "code_sondage",
            "a_quitte_l_entreprise",
            "a_quitte_num",
            "augementation_salaire_precedente",
        ]

        # Variables binaires à encoder (Oui/Non -> 1/0)
        self.variables_binaires = ["heure_supplementaires", "ayant_enfants"]

        # Variables catégorielles pour One-Hot Encoding
        self.variables_onehot = ["statut_marital", "departement", "poste"]

        # Vocabulaire fixe utilise lors de l'entrainement. L'encodage ne doit
        # jamais dependre des seules categories presentes dans une requete.
        self.categorical_levels = {
            "statut_marital": ["Célibataire", "Divorcé(e)", "Marié(e)"],
            "departement": ["Développement", "Consulting", "Ressources Humaines"],
            "poste": [
                "Développeur",
                "Cadre Commercial",
                "Consultant",
                "Directeur Technique",
                "Manager",
                "Représentant Commercial",
                "Ressources Humaines",
                "Senior Manager",
                "Tech Lead",
            ],
        }

        # Features finales attendues (dans l'ordre) - 34 features avec feature engineering
        self.expected_features = [
            "heure_supplementaires",
            "annee_experience_totale",
            "niveau_hierarchique_poste",
            "annees_dans_le_poste_actuel",
            "revenu_mensuel",
            "age",
            "annes_sous_responsable_actuel",
            "nombre_participation_pee",
            "annees_dans_l_entreprise",
            "note_evaluation_precedente",
            "satisfaction_employee_nature_travail",
            "satisfaction_employee_environnement",
            "distance_domicile_travail",
            "satisfaction_employee_equilibre_pro_perso",
            "nb_formations_suivies",
            "satisfaction_employee_equipe",
            "nombre_experiences_precedentes",
            "annees_depuis_la_derniere_promotion",
            "statut_marital_Divorcé(e)",
            "statut_marital_Marié(e)",
            "departement_Consulting",
            "departement_Ressources Humaines",
            "poste_Cadre Commercial",
            "poste_Consultant",
            "poste_Directeur Technique",
            "poste_Manager",
            "poste_Représentant Commercial",
            "poste_Ressources Humaines",
            "poste_Senior Manager",
            "poste_Tech Lead",
            "salaire_par_age",
            "stagnation_poste",
            "promotion_recente",
            "distance_longue",
        ]

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Gère les valeurs manquantes en supprimant les lignes.

        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame avec potentiellement des valeurs manquantes

        Returns:
        --------
        pd.DataFrame
            DataFrame sans valeurs manquantes
        """
        initial_rows = len(df)
        df_clean = df.dropna()
        removed_rows = initial_rows - len(df_clean)

        if removed_rows > 0:
            logger.warning(
                "%s lignes supprimees car elles contiennent des valeurs manquantes", removed_rows
            )

        return df_clean

    def encode_binary_variables(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Encode les variables binaires Oui/Non en 1/0.

        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame avec variables binaires

        Returns:
        --------
        pd.DataFrame
            DataFrame avec variables binaires encodées
        """
        df = df.copy()

        for col in self.variables_binaires:
            if col in df.columns:
                # Mapping flexible pour gérer différents formats
                mapping = {"Oui": 1, "Non": 0, "Y": 1, "N": 0, "yes": 1, "no": 0}
                df[col] = df[col].map(mapping)

                # Vérifier si l'encodage a réussi
                if df[col].isnull().any():
                    logger.warning("Valeurs non reconnues dans %s", col)

        return df

    def encode_categorical_variables(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applique One-Hot Encoding aux variables catégorielles.

        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame avec variables catégorielles

        Returns:
        --------
        pd.DataFrame
            DataFrame avec variables catégorielles encodées
        """
        df = df.copy()

        aliases = {
            "statut_marital": {
                "celibataire": "Célibataire",
                "célibataire": "Célibataire",
                "marie(e)": "Marié(e)",
                "marié(e)": "Marié(e)",
                "divorce(e)": "Divorcé(e)",
                "divorcé(e)": "Divorcé(e)",
            },
            "departement": {
                "developpement": "Développement",
                "développement": "Développement",
                "consulting": "Consulting",
                "ressources humaines": "Ressources Humaines",
            },
            "poste": {
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
            },
        }

        for column in self.variables_onehot:
            if column not in df.columns:
                continue

            normalized = df[column].astype(str).str.strip().str.lower().map(aliases[column])
            if normalized.isnull().any():
                invalid_values = sorted(df.loc[normalized.isnull(), column].astype(str).unique())
                raise ValueError(f"Valeurs categorielles inconnues dans {column}: {invalid_values}")

            # La premiere modalite est la reference. Les autres colonnes sont
            # creees explicitement, y compris pour une observation unique.
            for level in self.categorical_levels[column][1:]:
                df[f"{column}_{level}"] = (normalized == level).astype(int)
            df = df.drop(columns=[column])

        return df

    def create_engineered_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crée les features engineered.

        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame avec features de base

        Returns:
        --------
        pd.DataFrame
            DataFrame avec features engineered ajoutées
        """
        df = df.copy()

        # 1. Salaire par âge (ratio de rémunération)
        if "revenu_mensuel" in df.columns and "age" in df.columns:
            # Éviter division par zéro
            df["salaire_par_age"] = df.apply(
                lambda row: row["revenu_mensuel"] / row["age"] if row["age"] > 0 else 0, axis=1
            )

        # 2. Stagnation dans le poste (ratio temporel)
        if "annees_dans_le_poste_actuel" in df.columns and "annee_experience_totale" in df.columns:
            df["stagnation_poste"] = df.apply(
                lambda row: (
                    row["annees_dans_le_poste_actuel"] / row["annee_experience_totale"]
                    if row["annee_experience_totale"] > 0
                    else 0
                ),
                axis=1,
            )

        # 3. Promotion récente (indicateur binaire)
        if "annees_depuis_la_derniere_promotion" in df.columns:
            df["promotion_recente"] = (df["annees_depuis_la_derniere_promotion"] <= 2).astype(int)

        # 4. Distance longue domicile-travail (indicateur binaire)
        if "distance_domicile_travail" in df.columns:
            df["distance_longue"] = (df["distance_domicile_travail"] > 15).astype(int)

        return df

    def select_and_order_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Sélectionne et ordonne les features selon le schéma attendu.

        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame avec toutes les features

        Returns:
        --------
        pd.DataFrame
            DataFrame avec les features sélectionnées et ordonnées
        """
        # Vérifier les features manquantes
        missing_features = set(self.expected_features) - set(df.columns)
        if missing_features:
            logger.debug("Features absentes completees avec zero: %s", sorted(missing_features))
            # Créer les colonnes manquantes avec des zéros
            for feat in missing_features:
                df[feat] = 0

        # Sélectionner et ordonner
        df_final = df[self.expected_features].copy()

        return df_final

    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Valide que les données sont conformes aux attentes.

        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame à valider

        Returns:
        --------
        Tuple[bool, List[str]]
            (is_valid, list_of_errors)
        """
        errors = []

        # Vérifier le nombre de features
        if len(df.columns) != 34:
            errors.append(f"Nombre de features incorrect: {len(df.columns)} au lieu de 34")

        # Vérifier l'ordre des features
        if list(df.columns) != self.expected_features:
            errors.append("Ordre des features incorrect")

        # Vérifier les types de données
        for col in df.columns:
            if df[col].isnull().any():
                errors.append(f"Valeurs manquantes dans {col}")

        # Vérifier les valeurs binaires
        binary_features = [
            "heure_supplementaires",
            "promotion_recente",
            "distance_longue",
            "statut_marital_Divorcé(e)",
            "statut_marital_Marié(e)",
            "departement_Consulting",
            "departement_Ressources Humaines",
        ] + [f for f in self.expected_features if f.startswith("poste_")]

        for feat in binary_features:
            if feat in df.columns:
                unique_vals = df[feat].unique()
                if not set(unique_vals).issubset({0, 1, False, True}):
                    errors.append(f"{feat} contient des valeurs non-binaires: {unique_vals}")

        is_valid = len(errors) == 0
        return is_valid, errors

    def transform(self, df: pd.DataFrame, validate: bool = True) -> pd.DataFrame:
        """
        Pipeline complet de transformation des données.

        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame brut à transformer
        validate : bool
            Si True, valide les données après transformation

        Returns:
        --------
        pd.DataFrame
            DataFrame transformé prêt pour la prédiction
        """
        # 1. Copie pour ne pas modifier l'original
        df_processed = df.copy()

        # 2. Gestion des valeurs manquantes
        df_processed = self.handle_missing_values(df_processed)
        if df_processed.empty:
            raise ValueError("Aucune observation complete a predire")

        # 3. Encodage des variables binaires
        df_processed = self.encode_binary_variables(df_processed)

        # 4. Encodage des variables catégorielles
        df_processed = self.encode_categorical_variables(df_processed)

        # 5. Feature engineering
        df_processed = self.create_engineered_features(df_processed)

        # 6. Suppression des colonnes exclues
        cols_to_drop = [col for col in self.colonnes_exclues if col in df_processed.columns]
        if cols_to_drop:
            df_processed = df_processed.drop(columns=cols_to_drop)

        # 7. Sélection et ordre des features
        df_processed = self.select_and_order_features(df_processed)

        # 8. Validation (optionnelle)
        if validate:
            is_valid, errors = self.validate_data(df_processed)
            if not is_valid:
                raise ValueError("Donnees invalides apres preprocessing: " + "; ".join(errors))

        return df_processed


def prepare_single_prediction(data: Dict) -> pd.DataFrame:
    """
    Prépare un dictionnaire de données pour une prédiction unique.

    Parameters:
    -----------
    data : Dict
        Dictionnaire avec les données d'un employé

    Returns:
    --------
    pd.DataFrame
        DataFrame prêt pour la prédiction (1 ligne, 34 features)

    Example:
    --------
    >>> data = {
    ...     'age': 35,
    ...     'revenu_mensuel': 5000,
    ...     'statut_marital': 'Marié(e)',
    ...     'departement': 'Consulting',
    ...     'poste': 'Consultant',
    ...     'heure_supplementaires': 'Oui',
    ...     # ... autres features
    ... }
    >>> df = prepare_single_prediction(data)
    >>> # df peut maintenant être passé au modèle
    """
    # Créer un DataFrame à partir du dictionnaire
    df = pd.DataFrame([data])

    # Appliquer le preprocessing
    preprocessor = TurnoverDataPreprocessor()
    df_processed = preprocessor.transform(df, validate=True)

    return df_processed


def load_and_prepare_csv(
    filepath: str, has_target: bool = False
) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
    """
    Charge un fichier CSV et prépare les données.

    Parameters:
    -----------
    filepath : str
        Chemin vers le fichier CSV
    has_target : bool
        Si True, le fichier contient la colonne target 'a_quitte_l_entreprise'

    Returns:
    --------
    Tuple[pd.DataFrame, Optional[pd.Series]]
        (X_processed, y) si has_target=True, sinon (X_processed, None)
    """
    # Charger les données
    df = pd.read_csv(filepath)
    print(f"Données chargées: {df.shape}")

    # Extraire la target si présente
    y = None
    if has_target and "a_quitte_l_entreprise" in df.columns:
        y = df["a_quitte_l_entreprise"].map({"Oui": 1, "Non": 0})
        print(f"Target extraite: {y.value_counts().to_dict()}")

    # Preprocessing
    preprocessor = TurnoverDataPreprocessor()
    features = preprocessor.transform(df, validate=True)

    return features, y


if __name__ == "__main__":
    """Tests du module de preprocessing."""

    print("=" * 70)
    print("TEST DU MODULE DE PREPROCESSING")
    print("=" * 70)

    # Test 1: Preprocessing d'un fichier CSV
    print("\nTest 1: Chargement et preprocessing d'un CSV")
    try:
        X, y = load_and_prepare_csv("donnees_fusionnees.csv", has_target=True)
        print(f"X shape: {X.shape}")
        print(f"y shape: {y.shape if y is not None else 'None'}")
        print(f"Features: {list(X.columns[:5])}...")
    except FileNotFoundError:
        print("Warning: Fichier donnees_fusionnees.csv non trouvé")
    except Exception as e:
        print(f"Erreur: {e}")

    # Test 2: Préparation d'une prédiction unique
    print("\nTest 2: Préparation d'une prédiction unique")
    sample_data = {
        "age": 35,
        "revenu_mensuel": 5000,
        "statut_marital": "Marié(e)",
        "departement": "Consulting",
        "poste": "Consultant",
        "heure_supplementaires": "Oui",
        "annee_experience_totale": 10,
        "niveau_hierarchique_poste": 2,
        "annees_dans_le_poste_actuel": 3,
        "annes_sous_responsable_actuel": 2,
        "nombre_participation_pee": 1,
        "annees_dans_l_entreprise": 5,
        "note_evaluation_precedente": 3,
        "satisfaction_employee_nature_travail": 3,
        "satisfaction_employee_environnement": 3,
        "distance_domicile_travail": 10,
        "satisfaction_employee_equilibre_pro_perso": 3,
        "nb_formations_suivies": 2,
        "satisfaction_employee_equipe": 3,
        "nombre_experiences_precedentes": 2,
        "annees_depuis_la_derniere_promotion": 1,
        "ayant_enfants": "Oui",
    }

    try:
        df_pred = prepare_single_prediction(sample_data)
        print(f"Données préparées: {df_pred.shape}")
        print(f"Première feature: {df_pred.iloc[0, 0]}")
    except Exception as e:
        print(f"Erreur: {e}")

    print("\n" + "=" * 70)
    print("TESTS TERMINÉS")
    print("=" * 70)
