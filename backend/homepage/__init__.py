"""
首页模块
系统主页和通用功能
"""

from flask import Blueprint
from .routes.home import home_bp

# 创建首页模块蓝图
homepage_bp = Blueprint('homepage', __name__)

# 注册子路由
homepage_bp.register_blueprint(home_bp)