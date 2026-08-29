"""
Suite de tests pour l'application de prediction du turnover.

Organisation des tests:
- tests/api/: Tests des endpoints FastAPI
- tests/ml/: Tests du preprocessing et de la prediction
- tests/db/: Tests des modeles et repositories
- tests/core/: Tests de la configuration et de l'application principale

Execution des tests:
    pytest                     # Tous les tests
    pytest tests/api/          # Tests API uniquement
    pytest tests/ml/           # Tests ML uniquement
    pytest -v                  # Mode verbose
    pytest --cov=app           # Avec couverture de code
"""
