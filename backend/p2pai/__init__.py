"""
P2P AI模块
点对点人工智能训练和模型管理
"""

from flask import Blueprint
from .routes.training import training_bp
from .routes.projects import projects_bp
from .routes.models import models_bp
from .routes.datasets import datasets_bp

# 创建P2P AI模块蓝图
p2pai_bp = Blueprint('p2pai', __name__)

# 注册子路由
p2pai_bp.register_blueprint(training_bp, url_prefix='/training')
p2pai_bp.register_blueprint(projects_bp, url_prefix='/projects')
p2pai_bp.register_blueprint(models_bp, url_prefix='/models')
p2pai_bp.register_blueprint(datasets_bp, url_prefix='/datasets')