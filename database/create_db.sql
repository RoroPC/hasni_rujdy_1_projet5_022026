BEGIN;

CREATE TABLE IF NOT EXISTS employee_data (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    request_id VARCHAR(36) NOT NULL UNIQUE,
    age INTEGER NOT NULL CHECK (age BETWEEN 18 AND 70),
    statut_marital VARCHAR(50) NOT NULL,
    ayant_enfants VARCHAR(10),
    distance_domicile_travail INTEGER NOT NULL CHECK (distance_domicile_travail >= 0),
    departement VARCHAR(100) NOT NULL,
    poste VARCHAR(100) NOT NULL,
    niveau_hierarchique_poste INTEGER NOT NULL CHECK (niveau_hierarchique_poste BETWEEN 1 AND 5),
    revenu_mensuel INTEGER NOT NULL CHECK (revenu_mensuel >= 0),
    heure_supplementaires VARCHAR(10) NOT NULL,
    annee_experience_totale INTEGER NOT NULL CHECK (annee_experience_totale >= 0),
    annees_dans_le_poste_actuel INTEGER NOT NULL CHECK (annees_dans_le_poste_actuel >= 0),
    annees_dans_l_entreprise INTEGER NOT NULL CHECK (annees_dans_l_entreprise >= 0),
    annes_sous_responsable_actuel INTEGER NOT NULL CHECK (annes_sous_responsable_actuel >= 0),
    nombre_experiences_precedentes INTEGER NOT NULL CHECK (nombre_experiences_precedentes >= 0),
    annees_depuis_la_derniere_promotion INTEGER NOT NULL CHECK (annees_depuis_la_derniere_promotion >= 0),
    nb_formations_suivies INTEGER NOT NULL CHECK (nb_formations_suivies >= 0),
    note_evaluation_precedente INTEGER NOT NULL CHECK (note_evaluation_precedente BETWEEN 1 AND 4),
    nombre_participation_pee INTEGER NOT NULL CHECK (nombre_participation_pee >= 0),
    satisfaction_employee_nature_travail INTEGER NOT NULL CHECK (satisfaction_employee_nature_travail BETWEEN 1 AND 4),
    satisfaction_employee_environnement INTEGER NOT NULL CHECK (satisfaction_employee_environnement BETWEEN 1 AND 4),
    satisfaction_employee_equilibre_pro_perso INTEGER NOT NULL CHECK (satisfaction_employee_equilibre_pro_perso BETWEEN 1 AND 4),
    satisfaction_employee_equipe INTEGER NOT NULL CHECK (satisfaction_employee_equipe BETWEEN 1 AND 4)
);

CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    employee_data_id INTEGER NOT NULL UNIQUE REFERENCES employee_data(id) ON DELETE CASCADE,
    probability DOUBLE PRECISION NOT NULL CHECK (probability BETWEEN 0 AND 1),
    prediction_binary INTEGER NOT NULL CHECK (prediction_binary IN (0, 1)),
    risk_level VARCHAR(20) NOT NULL,
    confidence DOUBLE PRECISION NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    threshold_used DOUBLE PRECISION NOT NULL CHECK (threshold_used BETWEEN 0 AND 1),
    model_version VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS prediction_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    request_id VARCHAR(36) NOT NULL,
    endpoint VARCHAR(100) NOT NULL,
    method VARCHAR(10) NOT NULL,
    client_ip VARCHAR(45),
    status_code INTEGER NOT NULL,
    response_time_ms DOUBLE PRECISION,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS ix_employee_data_request_id ON employee_data(request_id);
CREATE INDEX IF NOT EXISTS ix_prediction_logs_request_id ON prediction_logs(request_id);

COMMIT;
