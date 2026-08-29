# Rapport de couverture des tests

Date de génération : 27 août 2026
Python : 3.10.19
Commande : `pytest --cov=app --cov-report=term-missing --cov-report=html:reports/coverage_html --cov-report=xml:reports/coverage.xml`

## Résultat

- **136 tests réussis**
- **82,90 % de couverture globale**
- seuil CI exigé : **80 %**

| Module | Couverture |
|---|---:|
| API endpoints | 92 % |
| Schémas Pydantic | 97 % |
| Configuration et sécurité | 100 % |
| Modèles de base | 98 % |
| Repositories | 100 % |
| Application FastAPI | 93 % |
| Prédicteur ML | 44 % |
| Preprocessing ML | 86 % |

Le taux plus faible du fichier `app/ml/predict.py` vient principalement des exemples exécutables et des chemins batch. Les cas critiques utilisés par l'API - chargement, seuil, probabilités, niveaux de risque, preprocessing et erreurs d'artefacts - sont couverts. Le détail ligne par ligne est disponible dans `reports/coverage_html/index.html`.
