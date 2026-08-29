# Sécurité

## Authentification

Définissez `API_KEY` en staging et en production. Les routes de prédiction, d'historique et de statistiques exigent alors l'en-tête `X-API-Key`. Les routes de santé et d'information du modèle restent publiques pour le monitoring.

## Secrets

- stockez `API_KEY`, `DATABASE_URL`, `HF_TOKEN` et toute clé fournisseur dans le gestionnaire de secrets de la plateforme;
- ne commitez jamais `.env`;
- utilisez des jetons à droits minimaux et faites-les tourner régulièrement;
- protégez l'environnement GitHub `prod` par approbation manuelle.

## Données RH

Les données RH sont personnelles et potentiellement sensibles. En production : chiffrez les flux TLS, limitez les accès par rôle, définissez une durée de conservation, pseudonymisez les identifiants et journalisez les consultations. Ne stockez pas d'adresse IP si elle n'est pas nécessaire à la sécurité.

## Limites du POC

L'authentification par clé d'API convient à un POC et à des intégrations serveur-à-serveur simples. Une production multi-utilisateurs devrait employer OAuth2/OIDC, des rôles, un gestionnaire de secrets et une politique d'audit dédiée.

## Signalement

Ne publiez pas une vulnérabilité contenant des données réelles ou un secret. Révoquez d'abord le secret concerné, puis ouvrez un canal privé avec le responsable du dépôt.
