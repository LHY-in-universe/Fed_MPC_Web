"""
密码学模块路由包
"""

from flask import Blueprint
from .key_management import keys_bp
from .encryption import encryption_bp
from .certificates import certificates_bp

# 创建密码学模块蓝图
crypto_bp = Blueprint('crypto', __name__)

# 注册子路由
crypto_bp.register_blueprint(keys_bp, url_prefix='/keys')
crypto_bp.register_blueprint(encryption_bp, url_prefix='/encryption')
crypto_bp.register_blueprint(certificates_bp, url_prefix='/certificates')