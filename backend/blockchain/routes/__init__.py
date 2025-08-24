"""
区块链模块路由包
"""

from flask import Blueprint
from .transactions import transactions_bp
from .contracts import contracts_bp

# 创建区块链模块蓝图
blockchain_bp = Blueprint('blockchain', __name__)

# 注册子路由
blockchain_bp.register_blueprint(transactions_bp, url_prefix='/transactions')
blockchain_bp.register_blueprint(contracts_bp, url_prefix='/contracts')