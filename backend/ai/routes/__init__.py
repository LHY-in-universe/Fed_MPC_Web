"""
AI模块路由初始化
"""

from flask import Blueprint
from .training import training_bp
from .projects import projects_bp
from .models import models_bp
from .datasets import datasets_bp

# 创建AI模块蓝图
ai_bp = Blueprint('ai', __name__)

# 注册子路由
ai_bp.register_blueprint(training_bp, url_prefix='/training')
ai_bp.register_blueprint(projects_bp, url_prefix='/projects')
ai_bp.register_blueprint(models_bp, url_prefix='/models')
ai_bp.register_blueprint(datasets_bp, url_prefix='/datasets')