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
    business_type ENUM('ai', 'blockchain', 'crypto', 'homepage') NOT NULL,
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
    business_type ENUM('ai', 'blockchain', 'crypto', 'homepage') NOT NULL,
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
    business_type ENUM('ai', 'blockchain', 'crypto', 'homepage') NOT NULL,
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

-- 密钥管理表
CREATE TABLE crypto_key_pairs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    key_name VARCHAR(100) NOT NULL,
    key_type ENUM('RSA', 'AES', 'ECC', 'DSA') NOT NULL,
    key_size INT NOT NULL,
    algorithm VARCHAR(50) NOT NULL,
    public_key TEXT,
    private_key_encrypted TEXT, -- 加密存储的私钥
    key_fingerprint VARCHAR(255) UNIQUE,
    usage_purpose ENUM('encryption', 'signing', 'authentication', 'key_exchange') NOT NULL,
    status ENUM('active', 'revoked', 'expired', 'suspended') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_key_type (key_type),
    INDEX idx_status (status),
    INDEX idx_fingerprint (key_fingerprint)
);

-- 数字证书表
CREATE TABLE crypto_certificates (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    key_pair_id INT,
    cert_name VARCHAR(100) NOT NULL,
    cert_type ENUM('self_signed', 'ca_signed', 'intermediate', 'root') NOT NULL,
    subject_dn VARCHAR(500) NOT NULL, -- Distinguished Name
    issuer_dn VARCHAR(500) NOT NULL,
    serial_number VARCHAR(100) UNIQUE,
    certificate_data TEXT NOT NULL, -- PEM格式证书
    signature_algorithm VARCHAR(50),
    hash_algorithm VARCHAR(50),
    status ENUM('valid', 'revoked', 'expired', 'suspended') DEFAULT 'valid',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP NOT NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (key_pair_id) REFERENCES crypto_key_pairs(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_cert_type (cert_type),
    INDEX idx_status (status),
    INDEX idx_serial_number (serial_number)
);

-- 加密操作日志表
CREATE TABLE crypto_operations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    key_pair_id INT,
    certificate_id INT,
    operation_type ENUM('encrypt', 'decrypt', 'sign', 'verify', 'key_generate', 'cert_create', 'cert_revoke') NOT NULL,
    operation_details JSON,
    input_data_hash VARCHAR(255), -- 输入数据的哈希值
    output_data_hash VARCHAR(255), -- 输出数据的哈希值
    algorithm_used VARCHAR(50),
    status ENUM('success', 'failed', 'pending') DEFAULT 'pending',
    error_message TEXT,
    execution_time_ms INT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (key_pair_id) REFERENCES crypto_key_pairs(id) ON DELETE SET NULL,
    FOREIGN KEY (certificate_id) REFERENCES crypto_certificates(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_operation_type (operation_type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- 区块链智能合约表
CREATE TABLE blockchain_contracts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    contract_name VARCHAR(100) NOT NULL,
    contract_address VARCHAR(100) UNIQUE,
    contract_code TEXT,
    contract_abi JSON,
    compiler_version VARCHAR(50),
    deployment_hash VARCHAR(100),
    gas_used BIGINT,
    status ENUM('deployed', 'verified', 'paused', 'destroyed') DEFAULT 'deployed',
    network VARCHAR(50) DEFAULT 'private',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deployed_at TIMESTAMP NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_contract_address (contract_address),
    INDEX idx_status (status),
    INDEX idx_network (network)
);

-- 区块链交易表
CREATE TABLE blockchain_transactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    contract_id INT,
    transaction_hash VARCHAR(100) UNIQUE NOT NULL,
    from_address VARCHAR(100) NOT NULL,
    to_address VARCHAR(100),
    value DECIMAL(30,18) DEFAULT 0,
    gas_limit BIGINT,
    gas_used BIGINT,
    gas_price BIGINT,
    transaction_fee DECIMAL(30,18),
    block_number BIGINT,
    block_hash VARCHAR(100),
    transaction_index INT,
    status ENUM('pending', 'confirmed', 'failed', 'dropped') DEFAULT 'pending',
    confirmations INT DEFAULT 0,
    input_data TEXT,
    logs JSON,
    network VARCHAR(50) DEFAULT 'private',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (contract_id) REFERENCES blockchain_contracts(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_transaction_hash (transaction_hash),
    INDEX idx_from_address (from_address),
    INDEX idx_to_address (to_address),
    INDEX idx_status (status),
    INDEX idx_block_number (block_number),
    INDEX idx_network (network)
);

-- MPC计算会话表
CREATE TABLE mpc_sessions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(100) NOT NULL UNIQUE,
    initiator_user_id INT NOT NULL,
    session_name VARCHAR(200),
    computation_type ENUM('arithmetic', 'boolean', 'mixed') NOT NULL,
    participants_required INT NOT NULL,
    participants_joined INT DEFAULT 0,
    security_threshold INT NOT NULL,
    protocol VARCHAR(50), -- SPDZ, BGV, CKKS等
    status ENUM('created', 'recruiting', 'computing', 'completed', 'failed', 'cancelled') DEFAULT 'created',
    input_schema JSON,
    output_schema JSON,
    computation_result JSON,
    privacy_budget_used DECIMAL(10,6),
    computation_time_ms BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    
    FOREIGN KEY (initiator_user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_initiator_user_id (initiator_user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- MPC会话参与者表
CREATE TABLE mpc_participants (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_id INT NOT NULL,
    user_id INT NOT NULL,
    party_id INT NOT NULL,
    public_key TEXT,
    status ENUM('invited', 'joined', 'computing', 'completed', 'failed', 'left') DEFAULT 'invited',
    contribution_hash VARCHAR(255),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP NULL,
    
    FOREIGN KEY (session_id) REFERENCES mpc_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_session_user (session_id, user_id),
    UNIQUE KEY unique_session_party (session_id, party_id),
    INDEX idx_session_id (session_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);

-- 数据集管理表
CREATE TABLE datasets (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    dataset_name VARCHAR(200) NOT NULL,
    description TEXT,
    dataset_type ENUM('training', 'validation', 'testing', 'raw') NOT NULL,
    business_domain ENUM('ai', 'blockchain', 'crypto', 'general') NOT NULL,
    format VARCHAR(50), -- CSV, JSON, Image, etc.
    size_bytes BIGINT,
    records_count INT,
    columns_count INT,
    privacy_level ENUM('public', 'private', 'confidential', 'secret') DEFAULT 'private',
    encryption_status ENUM('none', 'client_side', 'server_side', 'both') DEFAULT 'none',
    storage_path VARCHAR(500),
    checksum VARCHAR(255),
    tags JSON,
    metadata JSON,
    status ENUM('uploaded', 'validated', 'processed', 'error', 'deleted') DEFAULT 'uploaded',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_dataset_type (dataset_type),
    INDEX idx_business_domain (business_domain),
    INDEX idx_privacy_level (privacy_level),
    INDEX idx_status (status)
);

-- 插入默认配置
INSERT INTO system_config (config_key, config_value, description) VALUES
('platform_name', '联邦学习平台', '平台名称'),
('max_training_rounds', '1000', '最大训练轮数'),
('session_timeout', '3600', '会话超时时间（秒）'),
('heartbeat_interval', '30', '心跳间隔（秒）'),
('max_participants', '100', '最大参与方数量'),
('supported_business_types', '["ai", "blockchain", "crypto", "homepage"]', '支持的业务类型'),
('supported_training_modes', '["normal", "mpc"]', '支持的训练模式');

-- 创建默认管理员用户 (密码需要在应用中hash)
-- 默认密码: admin123 (需要在应用中修改)
INSERT INTO users (username, password_hash, user_type, business_type, full_name, organization, email) VALUES 
('admin', '$2b$12$placeholder_hash_here', 'server', 'homepage', '系统管理员', '联邦学习平台', 'admin@federated.com'),
('ai-admin', '$2b$12$placeholder_hash_here', 'server', 'ai', 'AI模块管理员', '联邦学习平台', 'ai-admin@federated.com'),
('blockchain-admin', '$2b$12$placeholder_hash_here', 'server', 'blockchain', '区块链管理员', '联邦学习平台', 'blockchain-admin@federated.com'),
('crypto-admin', '$2b$12$placeholder_hash_here', 'server', 'crypto', '密钥管理员', '联邦学习平台', 'crypto-admin@federated.com');