"""Interface Gradio publique utilisant les artefacts du modèle de turnover."""

import os
from typing import Any

import gradio as gr

from app.api.schemas import EmployeeDataRequest
from app.ml.predict import TurnoverPredictor

ENVIRONMENT = os.getenv("ENVIRONMENT", "dev").lower()
ENVIRONMENT_LABELS = {
    "dev": "Développement",
    "staging": "Recette",
    "prod": "Production",
}

INPUT_NAMES = [
    "age",
    "statut_marital",
    "ayant_enfants",
    "distance_domicile_travail",
    "departement",
    "poste",
    "niveau_hierarchique_poste",
    "revenu_mensuel",
    "heure_supplementaires",
    "annee_experience_totale",
    "annees_dans_le_poste_actuel",
    "annees_dans_l_entreprise",
    "annes_sous_responsable_actuel",
    "nombre_experiences_precedentes",
    "annees_depuis_la_derniere_promotion",
    "nb_formations_suivies",
    "note_evaluation_precedente",
    "nombre_participation_pee",
    "satisfaction_employee_nature_travail",
    "satisfaction_employee_environnement",
    "satisfaction_employee_equilibre_pro_perso",
    "satisfaction_employee_equipe",
]

SAMPLE_VALUES = [
    35,
    "Marié(e)",
    "Oui",
    10,
    "Consulting",
    "Consultant",
    2,
    5000,
    "Oui",
    10,
    3,
    5,
    2,
    2,
    1,
    2,
    3,
    1,
    3,
    3,
    3,
    3,
]

predictor = TurnoverPredictor(
    model_path="artifacts/best_model_v2.pkl",
    scaler_path="artifacts/scaler.pkl",
    threshold_path="artifacts/seuil_optimal.txt",
    schema_path="app/ml/features_schema.json",
)


def predict_for_space(*values: Any) -> tuple[str, dict[str, Any]]:
    """Valide le formulaire puis retourne une prédiction lisible et son détail."""
    payload = dict(zip(INPUT_NAMES, values, strict=True))
    employee = EmployeeDataRequest(**payload)
    result = predictor.predict_single(employee.model_dump())

    probability = float(result["probability"])
    prediction_binary = int(result["prediction_binary"])
    decision = "Risque de départ" if prediction_binary == 1 else "Maintien probable"
    icon = "⚠️" if prediction_binary == 1 else "✅"
    summary = (
        f"## {icon} {decision}\n\n"
        f"**Probabilité de départ : {probability:.1%}**  \n"
        f"Niveau de risque : **{result['risk_level']}**  \n"
        f"Seuil de décision : **{float(result['threshold']):.0%}**"
    )
    details = {
        "environnement": ENVIRONMENT,
        "prediction": decision,
        "prediction_binary": prediction_binary,
        "probability": round(probability, 4),
        "risk_level": result["risk_level"],
        "confidence": round(float(result["confidence"]), 4),
        "threshold": float(result["threshold"]),
        "model_version": predictor.schema.get("model_info", {}).get("version", "2.0"),
    }
    return summary, details


def build_demo() -> gr.Blocks:
    """Construit l'interface de démonstration déployée sur Hugging Face Spaces."""
    environment_label = ENVIRONMENT_LABELS.get(ENVIRONMENT, ENVIRONMENT)
    with gr.Blocks(title="Prédiction du turnover") as demo:
        gr.Markdown(
            "# Prédiction du risque de départ\n"
            f"**Environnement : {environment_label}**  \n"
            "Renseignez le profil d'un employé puis lancez le modèle Random Forest. "
            "Cette démonstration n'est pas une décision RH automatisée."
        )

        with gr.Accordion("Profil et poste", open=True):
            with gr.Row():
                age = gr.Slider(18, 70, value=35, step=1, label="Âge")
                statut_marital = gr.Dropdown(
                    ["Célibataire", "Marié(e)", "Divorcé(e)"],
                    value="Marié(e)",
                    label="Statut marital",
                )
                ayant_enfants = gr.Radio(["Oui", "Non"], value="Oui", label="Enfants")
                distance = gr.Slider(0, 100, value=10, step=1, label="Distance domicile (km)")
            with gr.Row():
                departement = gr.Dropdown(
                    ["Développement", "Consulting", "Ressources Humaines"],
                    value="Consulting",
                    label="Département",
                )
                poste = gr.Dropdown(
                    [
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
                    value="Consultant",
                    label="Poste",
                )
                niveau = gr.Slider(1, 5, value=2, step=1, label="Niveau hiérarchique")
                revenu = gr.Number(value=5000, precision=0, label="Revenu mensuel (€)")
                heures_supp = gr.Radio(
                    ["Oui", "Non"], value="Oui", label="Heures supplémentaires"
                )

        with gr.Accordion("Expérience et évolution", open=False):
            with gr.Row():
                experience = gr.Slider(0, 50, value=10, step=1, label="Expérience totale")
                poste_actuel = gr.Slider(0, 40, value=3, step=1, label="Années dans le poste")
                entreprise = gr.Slider(0, 40, value=5, step=1, label="Années dans l'entreprise")
                responsable = gr.Slider(
                    0, 40, value=2, step=1, label="Années avec le responsable"
                )
            with gr.Row():
                experiences = gr.Slider(0, 15, value=2, step=1, label="Expériences précédentes")
                promotion = gr.Slider(0, 30, value=1, step=1, label="Années depuis promotion")
                formations = gr.Slider(0, 20, value=2, step=1, label="Formations suivies")
                evaluation = gr.Slider(1, 4, value=3, step=1, label="Note d'évaluation")
                pee = gr.Slider(0, 10, value=1, step=1, label="Participations PEE")

        with gr.Accordion("Satisfaction", open=False):
            with gr.Row():
                sat_travail = gr.Slider(1, 4, value=3, step=1, label="Nature du travail")
                sat_env = gr.Slider(1, 4, value=3, step=1, label="Environnement")
                sat_equilibre = gr.Slider(1, 4, value=3, step=1, label="Équilibre pro/perso")
                sat_equipe = gr.Slider(1, 4, value=3, step=1, label="Équipe")

        inputs = [
            age,
            statut_marital,
            ayant_enfants,
            distance,
            departement,
            poste,
            niveau,
            revenu,
            heures_supp,
            experience,
            poste_actuel,
            entreprise,
            responsable,
            experiences,
            promotion,
            formations,
            evaluation,
            pee,
            sat_travail,
            sat_env,
            sat_equilibre,
            sat_equipe,
        ]

        predict_button = gr.Button("Calculer le risque", variant="primary")
        summary = gr.Markdown()
        details = gr.JSON(label="Détail technique")
        predict_button.click(
            fn=predict_for_space,
            inputs=inputs,
            outputs=[summary, details],
            api_name="predict",
        )
        gr.Examples(examples=[SAMPLE_VALUES], inputs=inputs, label="Exemple de démonstration")

    return demo


demo = build_demo()
