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

1. Créez un Space **public** de type **Docker**. Le Space de production prévu pour ce projet est `RoroPC/turnover-prediction-api`.
2. Si plusieurs environnements cloud sont nécessaires, choisissez ensuite des noms distincts, par exemple `turnover-api-dev`, `turnover-api-staging` et `turnover-api-prod`.
3. Ajoutez les variables/secrets du Space :
   - `DATABASE_URL` : URL PostgreSQL du fournisseur choisi;
   - `API_KEY` : clé longue et aléatoire;
   - `CORS_ORIGINS` : origines autorisées;
   - `ENVIRONMENT` : `dev`, `staging` ou `prod`.
4. N'inscrivez jamais ces valeurs dans `.env.example`, le workflow ou le README.

La disponibilité du SDK Docker dépend de l'offre et du matériel accessibles au compte Hugging Face. Si l'interface affiche Docker comme une option payante désactivée, ne choisissez pas Gradio comme remplacement automatique : le dépôt actuel expose une API FastAPI au moyen de son `Dockerfile`. Il faut soit activer une offre Docker avec l'accord du propriétaire, soit adapter explicitement l'application à un runtime Gradio.

L'interaction PostgreSQL peut rester locale pour la soutenance, conformément à la mission. Pour une API publique réellement persistante, fournissez un PostgreSQL accessible depuis le Space.

## 3. Configuration GitHub

Créez les environnements GitHub `dev`, `staging` et `prod`. Dans chaque environnement :

- ajoutez le secret `HF_TOKEN`;
- ajoutez la variable `HF_SPACE_ID` (`utilisateur/space`);
- ajoutez la variable `HF_DEPLOY_ENABLED=true`;
- configurez une approbation manuelle pour `prod`.

Protégez `dev`, `staging` et `prod` : pull request obligatoire, job `quality` obligatoire, fusion interdite tant que les tests échouent.

Le workflow officiel synchronise le contenu vers Hugging Face après les tests. `.github/` et `.git/` ne sont pas copiés dans le Space.

## 4. Promotion des versions

```text
branche de fonctionnalité -> dev -> staging -> prod
```

- `dev` : déploiement rapide d'intégration;
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
