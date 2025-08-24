"""
AI模块
人工智能训练和模型管理
"""

from flask import Blueprint
from .routes.training import training_bp
from .routes.projects import projects_bp
from .routes.models import models_bp
from .routes.datasets import datasets_bp

# 创建AI模块蓝图
ai_bp = Blueprint('ai', __name__)

# 注册子路由
ai_bp.register_blueprint(training_bp, url_prefix='/training')
ai_bp.register_blueprint(projects_bp, url_prefix='/projects')
ai_bp.register_blueprint(models_bp, url_prefix='/models')
ai_bp.register_blueprint(datasets_bp, url_prefix='/datasets')