"""
业务模块包
包含AI、区块链和密钥加密签名三个业务模块
"""

from .crypto import crypto_bp as crypto_module
from .ai import ai_bp as ai_module  
from .blockchain import blockchain_bp as blockchain_module

# 模块注册表
AVAILABLE_MODULES = {
    'crypto': {
        'name': '密钥加密签名',
        'description': '提供密钥管理、数据加密和数字签名功能',
        'blueprint': crypto_module,
        'prefix': '/api/crypto',
        'icon': 'shield-check',
        'color': '#8b5cf6'
    },
    'ai': {
        'name': 'AI大模型业务',
        'description': '深度学习模型训练、自然语言处理、计算机视觉等AI应用的联邦学习',
        'blueprint': ai_module,
        'prefix': '/api/ai',
        'icon': 'lightbulb',
        'color': '#6b7280'
    },
    'blockchain': {
        'name': '金融区块链业务', 
        'description': '基于区块链的金融数据分析、风险评估、智能合约等应用的安全联邦学习',
        'blueprint': blockchain_module,
        'prefix': '/api/blockchain',
        'icon': 'currency-dollar',
        'color': '#374151'
    }
}

def register_modules(app):
    """注册所有业务模块到Flask应用"""
    for module_key, module_info in AVAILABLE_MODULES.items():
        try:
            blueprint = module_info['blueprint']
            prefix = module_info['prefix']
            app.register_blueprint(blueprint, url_prefix=prefix)
            app.logger.info(f"Successfully registered module: {module_info['name']}")
        except Exception as e:
            app.logger.error(f"Failed to register module {module_key}: {str(e)}")

def get_module_info(module_key):
    """获取模块信息"""
    return AVAILABLE_MODULES.get(module_key)

def get_all_modules():
    """获取所有可用模块"""
    return AVAILABLE_MODULES

__all__ = ['AVAILABLE_MODULES', 'register_modules', 'get_module_info', 'get_all_modules']