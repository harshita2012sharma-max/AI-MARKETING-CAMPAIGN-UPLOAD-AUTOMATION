-- AdPulse MySQL Schema
-- Run this via migrations.py on startup
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(100) NOT NULL UNIQUE,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          ENUM('admin','manager','viewer') NOT NULL DEFAULT 'viewer',
    is_active     TINYINT(1) NOT NULL DEFAULT 1,
    created_at    DATETIME NOT NULL DEFAULT NOW(),
    last_login    DATETIME NULL
);

CREATE TABLE IF NOT EXISTS campaigns (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    external_id     VARCHAR(50) NOT NULL,
    name            VARCHAR(255) NOT NULL,
    platform        ENUM('google','meta','bing') NOT NULL,
    status          ENUM('active','paused','ended','draft') NOT NULL DEFAULT 'draft',
    objective       VARCHAR(100) NOT NULL DEFAULT 'awareness',
    daily_budget    DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    total_budget    DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    spent_total     DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    start_date      DATE NOT NULL,
    end_date        DATE NULL,
    target_audience TEXT NULL,
    keywords        TEXT NULL,
    health_score    DECIMAL(5,2) DEFAULT 0.00,
    created_by      INT NOT NULL,
    created_at      DATETIME NOT NULL DEFAULT NOW(),
    updated_at      DATETIME NOT NULL DEFAULT NOW() ON UPDATE NOW(),
    FOREIGN KEY (created_by) REFERENCES users(id),
    KEY idx_campaigns_platform (platform),
    KEY idx_campaigns_status (status)
);

CREATE TABLE IF NOT EXISTS daily_metrics (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    campaign_id   INT NOT NULL,
    date          DATE NOT NULL,
    impressions   INT NOT NULL DEFAULT 0,
    clicks        INT NOT NULL DEFAULT 0,
    conversions   INT NOT NULL DEFAULT 0,
    spend         DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    revenue       DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    ctr           DECIMAL(8,4) NOT NULL DEFAULT 0.0000,
    cpc           DECIMAL(8,4) NOT NULL DEFAULT 0.0000,
    cpa           DECIMAL(8,4) NOT NULL DEFAULT 0.0000,
    roi           DECIMAL(8,4) NOT NULL DEFAULT 0.0000,
    UNIQUE KEY uq_campaign_date (campaign_id, date),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    KEY idx_metrics_campaign_date (campaign_id, date)
);

CREATE TABLE IF NOT EXISTS ai_decisions (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    campaign_id      INT NULL,
    decision_type    VARCHAR(50) NOT NULL,
    title            VARCHAR(255) NOT NULL,
    reason           TEXT NOT NULL,
    suggested_action TEXT NOT NULL,
    expected_impact  TEXT NOT NULL,
    confidence       DECIMAL(4,2) NOT NULL DEFAULT 0.00,
    was_applied      TINYINT(1) NOT NULL DEFAULT 0,
    created_at       DATETIME NOT NULL DEFAULT NOW(),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NULL,
    action      VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NULL,
    entity_id   INT NULL,
    description TEXT NOT NULL,
    ip_address  VARCHAR(50) NULL,
    created_at  DATETIME NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS notifications (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    title       VARCHAR(255) NOT NULL,
    message     TEXT NOT NULL,
    type        ENUM('info','warning','error','success') NOT NULL DEFAULT 'info',
    is_read     TINYINT(1) NOT NULL DEFAULT 0,
    related_id  INT NULL,
    created_at  DATETIME NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reports (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    title        VARCHAR(255) NOT NULL,
    report_type  VARCHAR(50) NOT NULL,
    format       ENUM('pdf','csv') NOT NULL DEFAULT 'pdf',
    file_path    VARCHAR(500) NOT NULL,
    generated_by INT NULL,
    generated_at DATETIME NOT NULL DEFAULT NOW(),
    FOREIGN KEY (generated_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS scheduler_jobs (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    job_name    VARCHAR(100) NOT NULL,
    status      ENUM('pending','running','success','failed') NOT NULL DEFAULT 'pending',
    started_at  DATETIME NULL,
    finished_at DATETIME NULL,
    message     TEXT NULL,
    created_at  DATETIME NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS settings (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    `key`       VARCHAR(100) NOT NULL UNIQUE,
    value       TEXT NOT NULL,
    description TEXT NULL,
    updated_at  DATETIME NOT NULL DEFAULT NOW() ON UPDATE NOW()
);

CREATE TABLE IF NOT EXISTS campaign_platforms (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    campaign_id   INT NOT NULL,
    platform      ENUM('google','meta','bing') NOT NULL,
    external_id   VARCHAR(100) NOT NULL,
    status        ENUM('created','active','paused','failed','syncing') NOT NULL DEFAULT 'created',
    synced_at     DATETIME NOT NULL DEFAULT NOW(),
    error_message TEXT NULL,
    UNIQUE KEY uq_campaign_platform (campaign_id, platform),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);

SET FOREIGN_KEY_CHECKS = 1;

INSERT IGNORE INTO settings (`key`, value, description) VALUES
    ('app_name',              'AdPulse',    'Application display name'),
    ('weekly_report_day',     'Monday',     'Day to auto-generate weekly reports'),
    ('anomaly_ctr_threshold', '25',         'CTR drop percent that triggers anomaly alert'),
    ('anomaly_spend_threshold','30',        'Spend spike percent that triggers anomaly alert'),
    ('health_score_weights',  '{"ctr":0.3,"roi":0.4,"cpc":0.3}', 'AI scoring weights'),
    ('sync_interval_minutes', '30',         'How often to sync platform data');