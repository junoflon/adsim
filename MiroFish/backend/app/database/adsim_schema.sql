-- AdSim SQLite Schema

CREATE TABLE IF NOT EXISTS adsim_projects (
    project_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_projects_created ON adsim_projects(created_at);

CREATE TABLE IF NOT EXISTS adsim_seed_materials (
    seed_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    type TEXT NOT NULL,
    content TEXT,
    file_path TEXT,
    file_size INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES adsim_projects(project_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_seeds_project ON adsim_seed_materials(project_id);

CREATE TABLE IF NOT EXISTS adsim_persona_configs (
    persona_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    age_range TEXT NOT NULL,
    gender TEXT,
    interests TEXT,
    consumption_habits TEXT,
    agent_count INTEGER NOT NULL DEFAULT 30,
    is_preset INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES adsim_projects(project_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_personas_project ON adsim_persona_configs(project_id);

CREATE TABLE IF NOT EXISTS adsim_simulations (
    simulation_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    persona_config_id TEXT NOT NULL,
    seed_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    total_rounds INTEGER NOT NULL DEFAULT 30,
    current_round INTEGER NOT NULL DEFAULT 0,
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES adsim_projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY(persona_config_id) REFERENCES adsim_persona_configs(persona_id),
    FOREIGN KEY(seed_id) REFERENCES adsim_seed_materials(seed_id)
);
CREATE INDEX IF NOT EXISTS idx_sims_project ON adsim_simulations(project_id);
CREATE INDEX IF NOT EXISTS idx_sims_status ON adsim_simulations(status);

CREATE TABLE IF NOT EXISTS adsim_agent_responses (
    response_id TEXT PRIMARY KEY,
    simulation_id TEXT NOT NULL,
    agent_id INTEGER NOT NULL,
    agent_name TEXT NOT NULL,
    agent_persona TEXT NOT NULL,
    sentiment TEXT NOT NULL,
    sentiment_score REAL NOT NULL,
    key_reactions TEXT NOT NULL,
    conversation_log TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(simulation_id) REFERENCES adsim_simulations(simulation_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_responses_sim ON adsim_agent_responses(simulation_id);

CREATE TABLE IF NOT EXISTS adsim_simulation_rounds (
    round_id TEXT PRIMARY KEY,
    simulation_id TEXT NOT NULL,
    round_number INTEGER NOT NULL,
    summary TEXT,
    sentiment_snapshot TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(simulation_id) REFERENCES adsim_simulations(simulation_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_rounds_sim ON adsim_simulation_rounds(simulation_id);

CREATE TABLE IF NOT EXISTS adsim_reports (
    report_id TEXT PRIMARY KEY,
    simulation_id TEXT NOT NULL UNIQUE,
    overall_sentiment TEXT NOT NULL,
    key_insights TEXT NOT NULL,
    concerns TEXT NOT NULL,
    recommendations TEXT NOT NULL,
    full_report_text TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(simulation_id) REFERENCES adsim_simulations(simulation_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_reports_sim ON adsim_reports(simulation_id);

CREATE TABLE IF NOT EXISTS adsim_ab_comparisons (
    comparison_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    persona_config_id TEXT NOT NULL,
    seed_a_id TEXT NOT NULL,
    seed_b_id TEXT NOT NULL,
    simulation_a_id TEXT,
    simulation_b_id TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    comparison_result TEXT,
    created_at TEXT NOT NULL,
    completed_at TEXT,
    FOREIGN KEY(project_id) REFERENCES adsim_projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY(persona_config_id) REFERENCES adsim_persona_configs(persona_id),
    FOREIGN KEY(seed_a_id) REFERENCES adsim_seed_materials(seed_id),
    FOREIGN KEY(seed_b_id) REFERENCES adsim_seed_materials(seed_id)
);
CREATE INDEX IF NOT EXISTS idx_comparisons_project ON adsim_ab_comparisons(project_id);
CREATE INDEX IF NOT EXISTS idx_comparisons_status ON adsim_ab_comparisons(status);
