# Modèle de données PostgreSQL

```mermaid
erDiagram
    EMPLOYEE_DATA ||--o| PREDICTIONS : "produit"
    EMPLOYEE_DATA {
        int id PK
        uuid request_id UK
        timestamptz created_at
        int age
        string statut_marital
        string departement
        string poste
        int revenu_mensuel
        string heure_supplementaires
        int satisfaction_employee_equipe
    }
    PREDICTIONS {
        int id PK
        int employee_data_id FK,UK
        timestamptz created_at
        float probability
        int prediction_binary
        string risk_level
        float confidence
        float threshold_used
        string model_version
    }
    PREDICTION_LOGS {
        int id PK
        uuid request_id
        timestamptz timestamp
        string endpoint
        string method
        int status_code
        float response_time_ms
        string error_message
    }
```

## Rôles des tables

- `employee_data` stocke l'intégralité des entrées validées avant leur passage au modèle.
- `predictions` stocke exactement un résultat par entrée grâce à la contrainte `UNIQUE` sur `employee_data_id`.
- `prediction_logs` conserve la trace technique des appels, réussis ou en erreur, corrélés par `request_id`.

Les contraintes SQL contrôlent les plages essentielles et la clé étrangère est supprimée en cascade. Le script [create_db.sql](create_db.sql) et les modèles SQLAlchemy décrivent le même schéma. Le fichier `sample_inputs.csv` contient des entrées anonymisées reproductibles; `scripts/seed_database.py` les enregistre, exécute le modèle, puis persiste les sorties.
