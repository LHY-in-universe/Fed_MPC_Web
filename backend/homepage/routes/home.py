"""
首页路由
处理系统主页和公共接口
"""

from flask import Blueprint, request, jsonify
from shared.utils.helpers import success_response, error_response
from shared.services.user_service import UserService

home_bp = Blueprint('home', __name__)

@home_bp.route('/', methods=['GET'])
def index():
    """系统主页"""
    return success_response({
        'system_name': '联邦学习多方计算平台',
        'version': '1.0.0',
        'description': '支持AI、区块链、密码学三大业务模块的综合平台',
        'modules': [
            {
                'name': 'AI智能学习',
                'path': '/ai',
                'description': '本地训练、联邦学习、MPC安全训练'
            },
            {
                'name': '区块链金融',
                'path': '/blockchain', 
                'description': '交易管理、智能合约、去中心化应用'
            },
            {
                'name': '密钥加密',
                'path': '/crypto',
                'description': '密钥管理、数据加密、数字证书'
            }
        ]
    })

@home_bp.route('/stats', methods=['GET'])
def system_stats():
    """系统统计信息"""
    try:
        # 获取用户统计
        user_stats = UserService.get_user_stats()
        
        # 组合系统统计
        stats = {
            'users': user_stats,
            'system': {
                'uptime': '99.9%',
                'total_requests': 125000,
                'active_sessions': 45,
                'server_status': 'healthy'
            },
            'modules': {
                'ai': {
                    'active_trainings': 12,
                    'completed_models': 156,
                    'total_datasets': 89
                },
                'blockchain': {
                    'total_transactions': 2340,
                    'active_contracts': 18,
                    'block_height': 125678
                },
                'crypto': {
                    'managed_keys': 234,
                    'active_certificates': 67,
                    'encryption_operations': 1890
                }
            }
        }
        
        return success_response(stats)
        
    except Exception as e:
        return error_response(f'获取系统统计失败: {str(e)}', 500)