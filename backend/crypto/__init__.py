"""
密码学模块
密钥管理和加密服务
"""

from flask import Blueprint
from .routes.key_management import keys_bp
from .routes.encryption import encryption_bp
from .routes.certificates import certificates_bp

# 创建密码学模块蓝图
crypto_bp = Blueprint('crypto', __name__)

# 注册子路由
crypto_bp.register_blueprint(keys_bp, url_prefix='/keys')
crypto_bp.register_blueprint(encryption_bp, url_prefix='/encryption')
crypto_bp.register_blueprint(certificates_bp, url_prefix='/certificates')