"""
Point d'entree principal de l'application FastAPI.
Configure l'application, les middlewares et les routes.
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.endpoints import router
from app.core.config import get_settings
from app.db.database import init_db

# Configuration du logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Recuperation des settings
settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Gestionnaire du cycle de vie de l'application.

    Initialise la base de donnees au demarrage
    et effectue le nettoyage a l'arret.
    """
    # Startup
    logger.info("Demarrage de l'application...")
    try:
        init_db()
        logger.info("Base de donnees initialisee avec succes")
    except Exception as e:
        logger.warning(f"Erreur lors de l'initialisation de la base de donnees: {e}")
        logger.warning("L'application continue sans persistance en base")

    yield

    # Shutdown
    logger.info("Arret de l'application...")


# Creation de l'application FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="""
## API de Prediction du Turnover - TechNova Partners

Cette API permet de predire le risque de depart des employes en utilisant
un modele de machine learning entraine sur les donnees historiques RH.

### Fonctionnalites principales

* **Prediction unitaire** : Soumettre les donnees d'un employe et obtenir une prediction
* **Historique** : Consulter l'historique des predictions effectuees
* **Statistiques** : Obtenir des metriques agregees sur les predictions
* **Monitoring** : Verifier l'etat de sante de l'application

### Modele de Machine Learning

Le modele utilise est un classifieur entraine sur 34 features incluant :
- Donnees demographiques (age, situation familiale)
- Donnees professionnelles (poste, departement, salaire)
- Indicateurs de satisfaction
- Historique de carriere

### Niveaux de Risque

Les predictions sont categorisees en 4 niveaux :
- **FAIBLE** : Probabilite < 30%
- **MODERE** : Probabilite entre 30% et 50%
- **ELEVE** : Probabilite entre 50% et 70%
- **TRES ELEVE** : Probabilite > 70%
    """,
    version=settings.APP_VERSION,
    openapi_tags=[
        {
            "name": "Prediction",
            "description": "Endpoints pour effectuer et consulter les predictions de turnover",
        },
        {"name": "Modele", "description": "Informations sur le modele de machine learning"},
        {"name": "Monitoring", "description": "Endpoints de monitoring et statistiques"},
    ],
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware pour logger toutes les requetes HTTP.

    Enregistre le temps de traitement et les informations de la requete.
    """
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.2f}ms"
    )

    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Gestionnaire global des exceptions non gerees.

    Capture toutes les exceptions non interceptees et retourne
    une reponse JSON formatee.
    """
    logger.error(f"Erreur non geree: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "Une erreur interne est survenue",
            "details": str(exc) if settings.DEBUG else None,
        },
    )


# Inclusion des routes
app.include_router(router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
async def root():
    """Redirection vers la documentation Swagger."""
    return {
        "message": "TechNova Partners - Turnover Prediction API",
        "documentation": "/docs",
        "version": settings.APP_VERSION,
    }
