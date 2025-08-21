-- 联邦学习平台数据库设计
-- Database: fed_mpc_platform
-- Version: 1.0.0

CREATE DATABASE IF NOT EXISTS fed_mpc_platform 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE fed_mpc_platform;

-- 用户表
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    user_type ENUM('client', 'server') NOT NULL,
    business_type ENUM('ai', 'blockchain') NOT NULL,
    email VARCHAR(100),
    full_name VARCHAR(100),
    organization VARCHAR(100),
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    
    INDEX idx_username (username),
    INDEX idx_user_type (user_type),
    INDEX idx_business_type (business_type)
);

-- 项目表
CREATE TABLE projects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    project_type ENUM('local', 'federated') NOT NULL,
    training_mode ENUM('normal', 'mpc') NOT NULL,
    business_type ENUM('ai', 'blockchain') NOT NULL,
    status ENUM('created', 'running', 'paused', 'completed', 'waiting_approval', 'approved', 'rejected', 'stopped') DEFAULT 'created',
    model_type VARCHAR(50),
    accuracy DECIMAL(5,4) DEFAULT 0.0000,
    loss DECIMAL(8,6) DEFAULT 0.000000,
    current_round INT DEFAULT 0,
    total_rounds INT DEFAULT 100,
    nodes_online INT DEFAULT 0,
    nodes_total INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_project_type (project_type),
    INDEX idx_business_type (business_type)
);

-- 训练会话表
CREATE TABLE training_sessions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL,
    session_id VARCHAR(100) NOT NULL UNIQUE,
    training_mode ENUM('normal', 'mpc') NOT NULL,
    model_type VARCHAR(50),
    total_rounds INT NOT NULL,
    current_round INT DEFAULT 0,
    status ENUM('created', 'running', 'paused', 'completed', 'failed') DEFAULT 'created',
    accuracy DECIMAL(5,4) DEFAULT 0.0000,
    loss DECIMAL(8,6) DEFAULT 0.000000,
    participants_count INT DEFAULT 0,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project_id (project_id),
    INDEX idx_session_id (session_id),
    INDEX idx_status (status)
);

-- 训练参与者表
CREATE TABLE session_participants (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_id INT NOT NULL,
    user_id INT NOT NULL,
    node_name VARCHAR(100),
    node_address VARCHAR(255),
    status ENUM('online', 'offline', 'training', 'waiting', 'error') DEFAULT 'offline',
    data_size BIGINT DEFAULT 0,
    last_heartbeat TIMESTAMP NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES training_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_session_user (session_id, user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);

-- 训练轮次记录表
CREATE TABLE training_rounds (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_id INT NOT NULL,
    round_number INT NOT NULL,
    participants JSON, -- 参与节点列表
    global_accuracy DECIMAL(5,4),
    global_loss DECIMAL(8,6),
    aggregation_method VARCHAR(50),
    weights_hash VARCHAR(255), -- 权重哈希值（MPC模式）
    weights_data JSON, -- 权重数据（普通模式）
    metrics JSON, -- 其他训练指标
    status ENUM('in_progress', 'completed', 'failed') DEFAULT 'in_progress',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    
    FOREIGN KEY (session_id) REFERENCES training_sessions(id) ON DELETE CASCADE,
    UNIQUE KEY unique_session_round (session_id, round_number),
    INDEX idx_session_id (session_id),
    INDEX idx_round_number (round_number)
);

-- 训练申请表
CREATE TABLE training_requests (
    id INT PRIMARY KEY AUTO_INCREMENT,
    client_user_id INT NOT NULL,
    project_name VARCHAR(200) NOT NULL,
    data_description TEXT,
    training_plan TEXT,
    expected_partners INT DEFAULT 3,
    current_partners INT DEFAULT 1,
    training_mode ENUM('normal', 'mpc') NOT NULL,
    business_type ENUM('ai', 'blockchain') NOT NULL,
    status ENUM('pending', 'approved', 'rejected', 'cancelled') DEFAULT 'pending',
    approved_by INT NULL,
    approved_at TIMESTAMP NULL,
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (client_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_client_user_id (client_user_id),
    INDEX idx_status (status),
    INDEX idx_business_type (business_type)
);

-- 系统日志表
CREATE TABLE system_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NULL,
    session_id INT NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INT,
    details JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (session_id) REFERENCES training_sessions(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at)
);

-- 系统配置表
CREATE TABLE system_config (
    id INT PRIMARY KEY AUTO_INCREMENT,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_config_key (config_key)
);

-- 插入默认配置
INSERT INTO system_config (config_key, config_value, description) VALUES
('platform_name', '联邦学习平台', '平台名称'),
('max_training_rounds', '1000', '最大训练轮数'),
('session_timeout', '3600', '会话超时时间（秒）'),
('heartbeat_interval', '30', '心跳间隔（秒）'),
('max_participants', '100', '最大参与方数量'),
('supported_business_types', '["ai", "blockchain"]', '支持的业务类型'),
('supported_training_modes', '["normal", "mpc"]', '支持的训练模式');

-- 创建默认管理员用户 (密码需要在应用中hash)
-- 默认密码: admin123 (需要在应用中修改)
INSERT INTO users (username, password_hash, user_type, business_type, full_name, organization, email) VALUES 
('admin', '$2b$12$placeholder_hash_here', 'server', 'ai', '系统管理员', '联邦学习平台', 'admin@federated.com'),
('blockchain-admin', '$2b$12$placeholder_hash_here', 'server', 'blockchain', '区块链管理员', '联邦学习平台', 'blockchain-admin@federated.com');