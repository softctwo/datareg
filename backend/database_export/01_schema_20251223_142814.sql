-- ============================================
-- 数据库结构脚本（DDL）
-- 导出时间: 2025-12-23 14:28:14
-- ============================================


-- 表: asset_tag_association
DROP TABLE IF EXISTS asset_tag_association CASCADE;

CREATE TABLE asset_tag_association (
    asset_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL
);


-- 表: audit_logs
DROP TABLE IF EXISTS audit_logs CASCADE;

CREATE TABLE audit_logs (
    id INTEGER NOT NULL DEFAULT nextval('audit_logs_id_seq'::regclass),
    action VARCHAR(11) NOT NULL,
    resource_type VARCHAR(50) NULL,
    resource_id INTEGER NULL,
    user_id INTEGER NOT NULL,
    username VARCHAR(50) NULL,
    ip_address VARCHAR(50) NULL,
    user_agent VARCHAR(500) NULL,
    operation_details JSON NULL,
    before_data JSON NULL,
    after_data JSON NULL,
    transfer_volume NUMERIC(20, 0) NULL,
    destination_country VARCHAR(100) NULL,
    transfer_status VARCHAR(50) NULL,
    is_anomaly BOOLEAN NULL,
    anomaly_type VARCHAR(50) NULL,
    anomaly_reason TEXT NULL,
    created_at TIMESTAMP NULL DEFAULT 'now()'
);


-- 表: cross_border_scenarios
DROP TABLE IF EXISTS cross_border_scenarios CASCADE;

CREATE TABLE cross_border_scenarios (
    id INTEGER NOT NULL DEFAULT nextval('cross_border_scenarios_id_seq'::regclass),
    scenario_name VARCHAR(200) NOT NULL,
    scenario_code VARCHAR(100) NOT NULL,
    business_type VARCHAR(100) NULL,
    recipient_name VARCHAR(200) NOT NULL,
    recipient_country VARCHAR(100) NOT NULL,
    recipient_type VARCHAR(50) NULL,
    data_purpose TEXT NOT NULL,
    storage_duration INTEGER NULL,
    transfer_frequency VARCHAR(50) NULL,
    security_level VARCHAR(50) NULL,
    encryption_method VARCHAR(100) NULL,
    data_scope TEXT NULL,
    estimated_volume NUMERIC(20, 0) NULL,
    status VARCHAR(9) NULL,
    approver_id INTEGER NULL,
    approved_at TIMESTAMP NULL,
    expiry_date TIMESTAMP NULL,
    description TEXT NULL,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP NULL DEFAULT 'now()',
    updated_at TIMESTAMP NULL
);


-- 表: data_assets
DROP TABLE IF EXISTS data_assets CASCADE;

CREATE TABLE data_assets (
    id INTEGER NOT NULL DEFAULT nextval('data_assets_id_seq'::regclass),
    asset_name VARCHAR(200) NOT NULL,
    asset_code VARCHAR(100) NOT NULL,
    asset_type VARCHAR(50) NULL,
    source_system VARCHAR(100) NULL,
    schema_name VARCHAR(100) NULL,
    table_name VARCHAR(200) NULL,
    data_level VARCHAR(9) NOT NULL,
    classification_id INTEGER NULL,
    description TEXT NULL,
    field_count INTEGER NULL,
    record_count INTEGER NULL,
    upstream_assets TEXT NULL,
    downstream_assets TEXT NULL,
    is_active BOOLEAN NULL,
    last_scan_time TIMESTAMP NULL,
    created_at TIMESTAMP NULL DEFAULT 'now()',
    updated_at TIMESTAMP NULL
);


-- 表: data_classifications
DROP TABLE IF EXISTS data_classifications CASCADE;

CREATE TABLE data_classifications (
    id INTEGER NOT NULL DEFAULT nextval('data_classifications_id_seq'::regclass),
    category_name VARCHAR(100) NOT NULL,
    category_code VARCHAR(50) NOT NULL,
    parent_id INTEGER NULL,
    level INTEGER NULL,
    description TEXT NULL,
    created_at TIMESTAMP NULL DEFAULT 'now()'
);


-- 表: notifications
DROP TABLE IF EXISTS notifications CASCADE;

CREATE TABLE notifications (
    id INTEGER NOT NULL DEFAULT nextval('notifications_id_seq'::regclass),
    user_id INTEGER NOT NULL,
    type VARCHAR(17) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NULL,
    status VARCHAR(8) NULL,
    resource_type VARCHAR(50) NULL,
    resource_id INTEGER NULL,
    action_url VARCHAR(500) NULL,
    priority INTEGER NULL,
    is_read BOOLEAN NULL,
    read_at TIMESTAMP NULL,
    created_at TIMESTAMP NULL DEFAULT 'now()',
    updated_at TIMESTAMP NULL
);


-- 表: risk_assessments
DROP TABLE IF EXISTS risk_assessments CASCADE;

CREATE TABLE risk_assessments (
    id INTEGER NOT NULL DEFAULT nextval('risk_assessments_id_seq'::regclass),
    assessment_name VARCHAR(200) NOT NULL,
    assessment_code VARCHAR(100) NOT NULL,
    assessment_type VARCHAR(50) NULL,
    scenario_id INTEGER NOT NULL,
    legal_environment_score NUMERIC(5, 2) NULL,
    data_volume_score NUMERIC(5, 2) NULL,
    security_measures_score NUMERIC(5, 2) NULL,
    data_sensitivity_score NUMERIC(5, 2) NULL,
    personal_info_count NUMERIC(20, 0) NULL,
    sensitive_info_count NUMERIC(20, 0) NULL,
    exceeds_personal_threshold BOOLEAN NULL,
    exceeds_sensitive_threshold BOOLEAN NULL,
    overall_risk_level VARCHAR(8) NULL,
    overall_score NUMERIC(5, 2) NULL,
    risk_factors JSON NULL,
    mitigation_measures TEXT NULL,
    assessment_result TEXT NULL,
    requires_regulatory_approval BOOLEAN NULL,
    recommendation TEXT NULL,
    status VARCHAR(11) NULL,
    assessor_id INTEGER NULL,
    reviewed_by INTEGER NULL,
    created_at TIMESTAMP NULL DEFAULT 'now()',
    updated_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL
);


-- 表: roles
DROP TABLE IF EXISTS roles CASCADE;

CREATE TABLE roles (
    id INTEGER NOT NULL DEFAULT nextval('roles_id_seq'::regclass),
    name VARCHAR(50) NOT NULL,
    description VARCHAR(255) NULL,
    permissions VARCHAR(1000) NULL,
    created_at TIMESTAMP NULL DEFAULT 'now()'
);


-- 表: sensitive_tags
DROP TABLE IF EXISTS sensitive_tags CASCADE;

CREATE TABLE sensitive_tags (
    id INTEGER NOT NULL DEFAULT nextval('sensitive_tags_id_seq'::regclass),
    tag_name VARCHAR(100) NOT NULL,
    tag_code VARCHAR(50) NOT NULL,
    tag_type VARCHAR(50) NULL,
    detection_rule TEXT NULL,
    risk_level VARCHAR(20) NULL,
    description TEXT NULL,
    is_active BOOLEAN NULL,
    created_at TIMESTAMP NULL DEFAULT 'now()',
    updated_at TIMESTAMP NULL
);


-- 表: system_configs
DROP TABLE IF EXISTS system_configs CASCADE;

CREATE TABLE system_configs (
    id INTEGER NOT NULL DEFAULT nextval('system_configs_id_seq'::regclass),
    config_key VARCHAR(100) NOT NULL,
    config_name VARCHAR(200) NOT NULL,
    config_value TEXT NOT NULL,
    config_type VARCHAR(7) NULL,
    category VARCHAR(15) NOT NULL,
    description TEXT NULL,
    is_encrypted BOOLEAN NULL,
    is_editable BOOLEAN NULL,
    is_public BOOLEAN NULL,
    validation_rule TEXT NULL,
    default_value TEXT NULL,
    created_at TIMESTAMP NULL DEFAULT 'now()',
    updated_at TIMESTAMP NULL,
    updated_by INTEGER NULL
);


-- 表: transfer_approvals
DROP TABLE IF EXISTS transfer_approvals CASCADE;

CREATE TABLE transfer_approvals (
    id INTEGER NOT NULL DEFAULT nextval('transfer_approvals_id_seq'::regclass),
    scenario_id INTEGER NOT NULL,
    approval_status VARCHAR(9) NULL,
    applicant_id INTEGER NOT NULL,
    approver_id INTEGER NULL,
    transfer_type VARCHAR(50) NULL,
    data_assets TEXT NULL,
    transfer_start_time TIMESTAMP NULL,
    transfer_end_time TIMESTAMP NULL,
    actual_volume NUMERIC(20, 0) NULL,
    approval_comment TEXT NULL,
    approved_at TIMESTAMP NULL,
    rejected_reason TEXT NULL,
    created_at TIMESTAMP NULL DEFAULT 'now()',
    updated_at TIMESTAMP NULL
);


-- 表: user_role
DROP TABLE IF EXISTS user_role CASCADE;

CREATE TABLE user_role (
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL
);


-- 表: users
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    id INTEGER NOT NULL DEFAULT nextval('users_id_seq'::regclass),
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NULL,
    is_active BOOLEAN NULL,
    is_superuser BOOLEAN NULL,
    created_at TIMESTAMP NULL DEFAULT 'now()',
    updated_at TIMESTAMP NULL
);

