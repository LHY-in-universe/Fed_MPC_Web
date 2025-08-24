"""
生产环境配置文件
包含数据库、安全、性能等生产级配置
"""

import os
from datetime import timedelta

class ProductionConfig:
    """生产环境配置"""
    
    # 基础配置
    DEBUG = False
    TESTING = False
    
    # 安全配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-super-secret-key-change-in-production')
    
    # 数据库配置
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'fed_mpc_user')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'your_secure_password')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'fed_mpc_web')
    
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@"
        f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
        f"?charset=utf8mb4&autocommit=true"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_timeout': 20,
        'pool_recycle': 3600,
        'max_overflow': 20
    }
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # CORS配置
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'https://your-domain.com').split(',')
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/opt/fed_mpc_web/uploads')
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', '/opt/fed_mpc_web/logs/app.log')
    
    # Redis配置（如果使用）
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # 性能配置
    JSON_AS_ASCII = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    
    # 邮件配置（如果需要）
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # 监控配置
    ENABLE_METRICS = True
    METRICS_PORT = int(os.environ.get('METRICS_PORT', 9090))

class DevelopmentConfig:
    """开发环境配置"""
    DEBUG = True
    TESTING = False
    SECRET_KEY = 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///fed_mpc_dev.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)  # 开发时token有效期长一些

class TestingConfig:
    """测试环境配置"""
    DEBUG = False
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False

# 配置字典
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}