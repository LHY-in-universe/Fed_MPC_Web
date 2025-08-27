"""
配置文件
包含数据库连接、安全密钥等配置
"""

import os
from datetime import timedelta

class Config:
    """基础配置类"""
    
    # 基本配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fed_mpc_web_secret_key_2024'
    DEBUG = os.environ.get('DEBUG') or False
    
    # JWT配置
    JWT_SECRET_KEY = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # 数据库配置 (MySQL)
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER', 'fed_user')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'fed_password')
    DB_NAME = os.environ.get('DB_NAME', 'fed_mpc_platform')
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20
    }
    
    # 业务配置
    SUPPORTED_BUSINESS_TYPES = ['ai', 'blockchain']
    SUPPORTED_USER_TYPES = ['client', 'server']
    
    # 训练配置
    MAX_TRAINING_ROUNDS = 1000
    DEFAULT_TRAINING_ROUNDS = 100
    SUPPORTED_TRAINING_MODES = ['normal', 'mpc']
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024  # 1GB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'py', 'pkl', 'pth', 'h5', 'onnx', 'pb'}
    
    # API限流配置
    RATELIMIT_STORAGE_URL = 'memory://'
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'fed_mpc_web.log'

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    # 使用SQLite进行开发测试
    SQLALCHEMY_DATABASE_URI = 'sqlite:///fed_mpc_dev.db'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    # TODO: 生产环境数据库配置
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

class TestConfig(Config):
    """测试环境配置"""
    TESTING = True
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestConfig,
    'default': DevelopmentConfig
}