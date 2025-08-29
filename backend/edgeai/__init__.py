"""
EdgeAI模块
边缘人工智能节点管理与可视化
"""

from flask import Blueprint
from .routes.projects import projects_bp
from .routes.nodes import nodes_bp
from .routes.visualization import visualization_bp

# 创建EdgeAI模块蓝图
edgeai_bp = Blueprint('edgeai', __name__)

# 注册子路由
edgeai_bp.register_blueprint(projects_bp, url_prefix='/projects')
edgeai_bp.register_blueprint(nodes_bp, url_prefix='/nodes')
edgeai_bp.register_blueprint(visualization_bp, url_prefix='/visualization')