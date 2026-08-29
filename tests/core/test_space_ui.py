"""Tests de l'interface Hugging Face sans démarrer de serveur."""

from app.space_ui import SAMPLE_VALUES, predict_for_space


def test_space_prediction_returns_human_and_machine_readable_results():
    summary, details = predict_for_space(*SAMPLE_VALUES)

    assert "Probabilité de départ" in summary
    assert details["prediction_binary"] in (0, 1)
    assert 0 <= details["probability"] <= 1
    assert details["risk_level"] in {"FAIBLE", "MODERE", "ELEVE", "TRES ELEVE"}
    assert details["threshold"] == 0.36
    assert details["model_version"] == "2.0"


def test_space_prediction_reports_the_current_environment():
    _, details = predict_for_space(*SAMPLE_VALUES)

    assert details["environnement"] in {"dev", "staging", "prod"}
