-- ============================================
-- 数据库结构脚本（DDL）
-- 导出时间: 2025-12-23 14:23:14
-- ============================================


-- 表: data_classifications
DROP TABLE IF EXISTS data_classifications CASCADE;
CREATE TABLE data_classifications (id INTEGER NOT NULL DEFAULT nextval('data_classifications_id_seq'::regclass), category_name VARCHAR(100) NOT NULL, category_code VARCHAR(50) NOT NULL, parent_id INTEGER, level INTEGER, description TEXT, created_at TIMESTAMP WITH TIME ZONE DEFAULT now());
