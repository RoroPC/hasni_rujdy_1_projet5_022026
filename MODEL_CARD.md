# Model Card - Turnover Prediction

## Résumé

Le modèle estime la probabilité qu'un employé quitte l'entreprise. Il s'agit d'un `RandomForestClassifier` de 200 arbres, entraîné avec pondération des classes et `random_state=42`.

## Entrées et preprocessing

Le modèle reçoit 34 features dans un ordre strict :

- 18 variables numériques ou binaires;
- 12 indicateurs one-hot pour le statut marital, le département et le poste;
- 4 variables dérivées : salaire par âge, stagnation dans le poste, promotion récente et longue distance domicile-travail.

Les libellés sont normalisés vers le vocabulaire d'entraînement. Les catégories inconnues provoquent une erreur explicite; elles ne sont jamais ramenées silencieusement à la catégorie de référence.

## Sorties

- `probability` : probabilité estimée de la classe départ;
- `prediction_binary` : 1 si la probabilité est supérieure ou égale à 0.36, sinon 0;
- `risk_level` : faible, modéré, élevé ou très élevé;
- `confidence` : distance absolue entre la probabilité et le seuil.

## Métriques

Le dépôt ne contient pas le jeu de validation ni le rapport d'entraînement du projet source. Aucune métrique prédictive (F1, rappel, ROC-AUC) n'est donc affirmée ici sans preuve reproductible. La couverture de code mesure la robustesse logicielle, pas la performance statistique du modèle.

## Usage prévu

- preuve de concept et aide à l'analyse RH;
- triage de cas à examiner par un professionnel;
- démonstration d'un déploiement ML traçable.

## Usages interdits ou déconseillés

- décision automatique de licenciement, sanction, recrutement ou rémunération;
- interprétation individuelle sans revue humaine;
- usage sur une population très différente de celle d'entraînement;
- traitement de données personnelles sans base légale, information et contrôle d'accès.

## Limites et risques

- biais potentiels présents dans les données historiques;
- dérive des distributions et des pratiques RH;
- probabilités non garanties comme parfaitement calibrées;
- catégories limitées au vocabulaire d'entraînement;
- seuil 0.36 dépendant du compromis métier retenu lors du projet source.

## Maintenance

Surveiller les distributions d'entrée, les taux de classes, les erreurs de validation et la dérive de performance. Réévaluer périodiquement le seuil sur un jeu annoté, versionner ensemble modèle/scaler/schéma, et documenter chaque changement dans un tag Git.
