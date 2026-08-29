"""Insere des exemples, execute le modele et persiste les sorties."""

import argparse
import csv
from pathlib import Path

from app.api.schemas import EmployeeDataRequest
from app.core.config import get_settings
from app.db.database import SessionLocal, init_db
from app.db.repository import EmployeeRepository, LogRepository, PredictionRepository
from app.ml.predict import TurnoverPredictor


def parse_args() -> argparse.Namespace:
    """Construit les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("database/sample_inputs.csv"),
        help="CSV contenant les entrees conformes au schema OpenAPI",
    )
    return parser.parse_args()


def main() -> None:
    """Charge le CSV et trace le cycle entree-prediction-sortie en base."""
    args = parse_args()
    settings = get_settings()
    predictor = TurnoverPredictor(
        model_path=settings.MODEL_PATH,
        scaler_path=settings.SCALER_PATH,
        threshold_path=settings.THRESHOLD_PATH,
        schema_path=settings.SCHEMA_PATH,
    )
    init_db()

    inserted = 0
    with args.input.open(encoding="utf-8", newline="") as stream, SessionLocal() as db:
        for raw_row in csv.DictReader(stream):
            payload = EmployeeDataRequest.model_validate(raw_row).model_dump()
            employee = EmployeeRepository(db).create(payload)
            result = predictor.predict_single(payload)
            PredictionRepository(db).create(
                employee_data_id=employee.id,
                probability=result["probability"],
                prediction_binary=result["prediction_binary"],
                risk_level=result["risk_level"],
                confidence=result["confidence"],
                threshold_used=result["threshold"],
                model_version=predictor.schema.get("model_info", {}).get("version", "unknown"),
            )
            LogRepository(db).create(
                request_id=employee.request_id,
                endpoint="scripts/seed_database.py",
                method="BATCH",
                status_code=200,
            )
            inserted += 1

    print(f"{inserted} exemple(s) insere(s), predit(s) et journalise(s).")


if __name__ == "__main__":
    main()
