"""
密钥加密签名模块
提供密钥管理、数据加密和数字签名功能
"""

from flask import Blueprint
from .routes import key_routes, crypto_routes

# 创建crypto模块蓝图
crypto_bp = Blueprint('crypto', __name__)

# 注册路由
crypto_bp.register_blueprint(key_routes.bp, url_prefix='/keys')
crypto_bp.register_blueprint(crypto_routes.bp, url_prefix='/operations')

__all__ = ['crypto_bp']