# Guide de déploiement

## 1. Validation locale

```bash
cp .env.example .env
uv sync --frozen --extra dev
docker compose up --build -d
curl http://localhost:8000/api/v1/health
uv run pytest --cov=app --cov-fail-under=80
```

La documentation interactive doit être visible sur <http://localhost:8000/docs>. Exécutez ensuite :

```bash
uv run python scripts/seed_database.py
```

Vérifiez que les trois tables contiennent le même nombre d'exemples.

## 2. Préparation de Hugging Face Spaces

Le compte utilise le runtime Gradio gratuit. Deux Spaces publics isolent les versions distantes :

- `RoroPC/turnover-prediction-api-staging` avec `ENVIRONMENT=staging`;
- `RoroPC/turnover-prediction-api` avec `ENVIRONMENT=prod`.

`dev` reste l'environnement de développement local et d'intégration continue. Chaque Space distant possède un Trusted Publisher GitHub Actions limité au dépôt `RoroPC/hasni_rujdy_1_projet5_022026`, à la branche correspondante et au workflow `ci-cd.yml`. L'identité OIDC produit un jeton court et limité au Space; aucun `HF_TOKEN` permanent n'est stocké dans GitHub.

L'interface publique exécute le modèle sans persister les profils saisis. L'API FastAPI et la traçabilité PostgreSQL restent testables avec Docker Compose.

## 3. Configuration GitHub

Créez les environnements GitHub `dev`, `staging` et `prod`. `dev` exécute la CI sans déploiement cloud. Dans `staging` et `prod`, ajoutez `HF_SPACE_ID` et `HF_DEPLOY_ENABLED=true`. Configurez une approbation manuelle pour `prod`.

Protégez `dev`, `staging` et `prod` : pull request obligatoire, job `quality` obligatoire, fusion interdite tant que les tests échouent.

Le workflow synchronise uniquement les fichiers nécessaires à l'interface après les tests. Les fichiers GitHub, les tests, les rapports et les livrables locaux ne sont pas copiés dans le Space.

## 4. Promotion des versions

```text
branche de fonctionnalité -> dev -> staging -> prod
```

- `dev` : développement local et intégration continue;
- `staging` : démonstration et validation fonctionnelle;
- `prod` : approbation manuelle et version taguée.

Après validation de production :

```bash
git tag -a v1.0.0 -m "Première version déployable"
git push origin v1.0.0
```

Le push final et la création des secrets sont des actions manuelles du propriétaire du compte.

## 5. Vérifications après déploiement

Remplacez `$API_URL` par l'URL publique du Space :

```bash
curl "$API_URL/api/v1/health"
curl "$API_URL/openapi.json"
```

Effectuez une prédiction avec `X-API-Key`, récupérez-la par `request_id`, puis vérifiez `/api/v1/statistics`. Confirmez enfin dans PostgreSQL la présence de l'entrée, du résultat et du log.

## 6. Retour arrière

1. identifiez le dernier tag fonctionnel;
2. redéployez ce tag vers le Space;
3. ne restaurez pas une base sans sauvegarde;
4. conservez les logs d'incident et documentez la cause;
5. ne changez jamais modèle, scaler et schéma séparément.
