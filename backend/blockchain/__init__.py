"""
区块链模块
区块链交易和智能合约管理
"""

from flask import Blueprint
from .routes.transactions import transactions_bp
from .routes.contracts import contracts_bp

# 创建区块链模块蓝图
blockchain_bp = Blueprint('blockchain', __name__)

# 注册子路由
blockchain_bp.register_blueprint(transactions_bp, url_prefix='/transactions')
blockchain_bp.register_blueprint(contracts_bp, url_prefix='/contracts')