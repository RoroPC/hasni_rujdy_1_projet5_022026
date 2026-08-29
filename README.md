---
title: Turnover Prediction API
emoji: 📉
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 6.26.0
python_version: 3.10
app_file: app.py
pinned: false
license: mit
short_description: Interface publique du modèle de prédiction du turnover
---

# Déployez un modèle de Machine Learning

API FastAPI de prédiction du risque de départ des employés, complétée par une interface Gradio publique pour Hugging Face Spaces, avec validation Pydantic, traçabilité PostgreSQL, tests Pytest et pipeline CI/CD.

Projet OpenClassrooms 5 réalisé par **Rujdy Hasni**. Démarrage : **février 2026**.

## État du projet

- API et documentation Swagger/ReDoc : fonctionnelles.
- Modèle Random Forest et preprocessing déterministe : fonctionnels.
- PostgreSQL, script SQL, ORM, jeu d'exemples et script d'insertion : fonctionnels.
- Tests unitaires et fonctionnels : 138 tests validés, couverture globale 86,77 %.
- Docker Compose et image Docker : fournis.
- CI/CD `dev` / `staging` / `prod` : configuré.
- Déploiement cloud : interface Gradio gratuite synchronisée séparément pour `dev`, `staging` et `prod`.

## Architecture

```mermaid
flowchart LR
    U[Client API] -->|JSON + X-API-Key| F[FastAPI / Pydantic]
    F -->|1. entrée validée| DB[(PostgreSQL)]
    DB -->|2. entrée persistée| ML[Preprocessing + Random Forest]
    ML -->|3. probabilité + classe| DB
    DB -->|4. résultat tracé| F
    F --> U
```

Le flux `/predict` enregistre l'entrée avant l'inférence, puis persiste la sortie et le journal technique. Les tables et relations sont détaillées dans [database/schema.md](database/schema.md).

## Structure du dépôt

```text
.
├── .github/workflows/ci-cd.yml   # tests, couverture, Docker et déploiement
├── app/
│   ├── api/                      # endpoints et schémas Pydantic
│   ├── core/                     # configuration et authentification
│   ├── db/                       # SQLAlchemy et repositories
│   ├── ml/                       # preprocessing et prédiction
│   └── main.py                   # application FastAPI
├── artifacts/                    # modèle, scaler et seuil 0.36
├── database/
│   ├── create_db.sql             # création PostgreSQL idempotente
│   ├── schema.md                 # modèle de données/UML
│   ├── sample_inputs.csv         # exemples anonymisés
│   └── sample_inputs.xlsx        # version lisible et filtrable
├── scripts/
│   ├── create_db.py              # création via SQLAlchemy
│   └── seed_database.py          # entrée -> modèle -> sortie -> journal
├── tests/                        # tests API, DB, ML et intégration
├── Dockerfile
├── docker-compose.yml
├── MODEL_CARD.md
├── SECURITY.md
├── DEPLOYMENT_GUIDE.md
├── pyproject.toml
└── uv.lock
```

## Installation locale

Prérequis : Python 3.10, [uv](https://docs.astral.sh/uv/) et PostgreSQL 16, ou Docker Desktop.

```bash
git clone git@github.com:RoroPC/hasni_rujdy_1_projet5_022026.git
cd hasni_rujdy_1_projet5_022026
cp .env.example .env
uv sync --frozen --extra dev
```

Renseignez au minimum `DATABASE_URL`. Pour protéger les routes métier, renseignez également une valeur longue et aléatoire dans `API_KEY`.

### Démarrage avec Docker Compose

```bash
docker compose up --build
```

Services disponibles :

- API : <http://localhost:8000>
- Swagger : <http://localhost:8000/docs>
- ReDoc : <http://localhost:8000/redoc>
- PostgreSQL : `localhost:5432`

### Démarrage sans Docker

Créez d'abord la base et les tables :

```bash
uv run python scripts/create_db.py
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Utilisation de l'API

| Méthode | Endpoint | Description | Protégé par clé |
|---|---|---|---|
| `GET` | `/api/v1/health` | état de santé | non |
| `GET` | `/api/v1/model/info` | métadonnées du modèle | non |
| `POST` | `/api/v1/predict` | prédiction et persistance | oui si `API_KEY` est définie |
| `GET` | `/api/v1/predictions/{request_id}` | résultat historique | oui |
| `GET` | `/api/v1/predictions` | historique paginé | oui |
| `GET` | `/api/v1/statistics` | statistiques agrégées | oui |

Exemple :

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: votre-cle' \
  --data @database/sample_request.json
```

Le schéma complet, les contraintes et un exemple interactif sont exposés dans Swagger. Les catégories sans accents (`Marie(e)`, `Developpement`, etc.) sont acceptées puis normalisées vers le vocabulaire d'entraînement.

## Base PostgreSQL et traçabilité

Deux méthodes d'initialisation équivalentes sont fournies :

```bash
psql "$DATABASE_URL" -f database/create_db.sql
uv run python scripts/create_db.py
```

Pour insérer les exemples, exécuter le modèle et enregistrer les sorties :

```bash
uv run python scripts/seed_database.py --input database/sample_inputs.csv
```

Le script produit un enregistrement dans chacune des tables `employee_inputs`, `predictions` et `prediction_logs`. Le fichier fourni contient des exemples anonymisés; il ne remplace pas un dataset RH réel pour l'évaluation scientifique du modèle.

### Stockage et besoins analytiques

- `employee_inputs` conserve les variables reçues après validation, sans secret applicatif.
- `predictions` rattache à chaque entrée sa probabilité, sa décision et son niveau de risque.
- `prediction_logs` conserve l'endpoint, le statut HTTP et la latence afin de suivre l'exploitation.
- Les relations et contraintes sont décrites dans [database/schema.md](database/schema.md); l'historique et les agrégats sont accessibles par `/history` et `/statistics`.

Pour un futur tableau de bord, les besoins prioritaires sont le volume de prédictions, la répartition des niveaux de risque, le taux d'erreur et la latence. Une mise en production devra aussi suivre la dérive des entrées et des scores par rapport à un jeu de référence validé, tout en appliquant une politique de rétention adaptée aux données RH.

## Modèle de Machine Learning

- Algorithme : `RandomForestClassifier` avec `class_weight="balanced"`.
- Estimateurs : 200; profondeur maximale : 15; graine : 42.
- Entrée : 34 features (18 numériques/binaires, 12 one-hot, 4 features dérivées).
- Seuil de décision effectivement chargé : **0.36**.
- Artefacts : `best_model_v2.pkl`, `scaler.pkl`, `seuil_optimal.txt`.

Le prédicteur vérifie que le modèle et le scaler attendent bien 34 features. Le preprocessing utilise un vocabulaire fixe : l'encodage ne dépend donc pas des seules catégories présentes dans une requête unitaire. Les performances de validation ne sont pas inventées dans ce dépôt, car le jeu d'évaluation du projet source n'y est pas présent. Voir [MODEL_CARD.md](MODEL_CARD.md).

## Tests et couverture

```bash
uv run pytest \
  --cov=app \
  --cov-report=term-missing \
  --cov-report=html:reports/coverage_html \
  --cov-report=xml:reports/coverage.xml \
  --cov-fail-under=80
```

La suite couvre les endpoints, les erreurs de validation, le flux complet de prédiction, la persistance, les repositories, le preprocessing et les cas limites. Le rapport synthétique est dans [reports/coverage_report.md](reports/coverage_report.md) et le rapport HTML local se consulte dans `reports/coverage_html/index.html`.

Qualité de code :

```bash
uv run ruff check app tests scripts
```

## CI/CD et environnements

Le workflow [ci-cd.yml](.github/workflows/ci-cd.yml) s'exécute à chaque `push` et `pull_request` :

1. installation verrouillée avec `uv.lock`;
2. contrôle Ruff;
3. initialisation d'un service PostgreSQL;
4. tests et couverture minimale de 80 %;
5. construction de l'image Docker;
6. déploiement conditionnel vers un Space Hugging Face.

Les branches d'environnement sont :

- `dev` : développement et intégration continue;
- `staging` : validation avant production;
- `prod` : production, avec environnement GitHub protégé;

Activez les règles de protection GitHub sur `dev`, `staging` et `prod` afin d'exiger la réussite du job `quality` et une revue avant fusion.

### Secrets et variables GitHub

Dans chacun des environnements `dev`, `staging` et `prod` :

- variable `HF_SPACE_ID` : identifiant du Space correspondant;
- variable `HF_DEPLOY_ENABLED` : `true` pour autoriser le déploiement;
- publication sans secret permanent via un Trusted Publisher OIDC limité au dépôt, à la branche et au workflow.

Les Spaces gratuits exécutent l'interface Gradio et le modèle sans enregistrer de données RH. L'API FastAPI et la traçabilité PostgreSQL restent disponibles avec Docker Compose.

Les étapes complètes sont dans [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

## Authentification et sécurité

- Les routes métier utilisent l'en-tête `X-API-Key` lorsque `API_KEY` est configurée.
- Les comparaisons de clés sont effectuées avec une comparaison constante.
- `.env` est exclu de Git; `.env.example` ne contient que des valeurs fictives.
- CORS est limité par `CORS_ORIGINS` et n'autorise pas les credentials par défaut.
- Les secrets sont injectés par variables d'environnement/GitHub Environments.
- Les données d'entrée sont validées par Pydantic et contraintes en base.

Consultez [SECURITY.md](SECURITY.md) avant toute mise en production avec des données RH réelles.

## Maintenance

Pour publier une nouvelle version du modèle :

1. remplacer ensemble le modèle et le scaler;
2. mettre à jour `seuil_optimal.txt` et `features_schema.json`;
3. adapter les transformations et tests si le nombre ou l'ordre des features change;
4. exécuter la suite complète et comparer les performances sur le même jeu de validation;
5. documenter la version dans `MODEL_CARD.md` et créer un tag Git (`v1.1.0`, par exemple).

## Licence et contexte

Proof of Concept pédagogique réalisé dans le cadre du parcours Data Scientist - Machine Learning d'OpenClassrooms. Les données d'exemple sont synthétiques et ne doivent pas être interprétées comme des données RH réelles.
