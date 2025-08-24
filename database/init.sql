-- 联邦学习平台数据库初始化脚本
-- 创建数据库和用户

-- 创建数据库
CREATE DATABASE IF NOT EXISTS `fed_mpc_platform` 
DEFAULT CHARACTER SET utf8mb4 
DEFAULT COLLATE utf8mb4_unicode_ci;

-- 创建用户并授权
CREATE USER IF NOT EXISTS 'fed_user'@'%' IDENTIFIED BY 'fed_password';
CREATE USER IF NOT EXISTS 'fed_user'@'localhost' IDENTIFIED BY 'fed_password';

-- 授予权限
GRANT ALL PRIVILEGES ON `fed_mpc_platform`.* TO 'fed_user'@'%';
GRANT ALL PRIVILEGES ON `fed_mpc_platform`.* TO 'fed_user'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;

-- 使用数据库
USE `fed_mpc_platform`;

-- 启用外键约束
SET FOREIGN_KEY_CHECKS = 1;

-- 设置默认字符集
SET NAMES utf8mb4;

-- 创建索引优化查询性能
-- 这些表将由SQLAlchemy自动创建，但我们可以预设一些优化

-- 系统配置表的索引
-- ALTER TABLE system_config ADD INDEX idx_config_key (config_key);

-- 用户表的索引
-- ALTER TABLE users ADD INDEX idx_username (username);
-- ALTER TABLE users ADD INDEX idx_business_type (business_type);
-- ALTER TABLE users ADD INDEX idx_user_type (user_type);
-- ALTER TABLE users ADD INDEX idx_status (status);

-- 项目表的索引
-- ALTER TABLE projects ADD INDEX idx_business_type (business_type);
-- ALTER TABLE projects ADD INDEX idx_project_type (project_type);
-- ALTER TABLE projects ADD INDEX idx_status (status);
-- ALTER TABLE projects ADD INDEX idx_created_at (created_at);

-- 训练会话表的索引
-- ALTER TABLE training_sessions ADD INDEX idx_status (status);
-- ALTER TABLE training_sessions ADD INDEX idx_training_mode (training_mode);
-- ALTER TABLE training_sessions ADD INDEX idx_created_at (created_at);

-- 显示创建结果
SELECT 'Database and user setup completed successfully!' as Result;