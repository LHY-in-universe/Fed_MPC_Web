"""
简化版Flask应用 - 用于前后端连接测试
只包含核心API接口，不依赖复杂的数据库模型
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta
import logging

# 创建Flask应用
app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = 'fed-mpc-web-secret-key-2025'
app.config['DEBUG'] = True

# CORS设置
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:*", "http://127.0.0.1:*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-User-Type", "X-Business-Type"]
    }
})

# 日志配置
logging.basicConfig(level=logging.INFO)

# 模拟用户数据
MOCK_USERS = {
    'client': {
        # AI模块客户端
        'client1': {'password': '123456', 'business_type': 'ai', 'full_name': '客户端1'},
        'client2': {'password': '123456', 'business_type': 'ai', 'full_name': '客户端2'},
        '上海一厂': {'password': 'password123', 'business_type': 'ai', 'full_name': '上海第一工厂'},
        '武汉二厂': {'password': 'password123', 'business_type': 'ai', 'full_name': '武汉第二工厂'},
        '西安三厂': {'password': 'password123', 'business_type': 'ai', 'full_name': '西安第三工厂'},
        '广州四厂': {'password': 'password123', 'business_type': 'ai', 'full_name': '广州第四工厂'},
        
        # 区块链模块客户端
        'user': {'password': 'user123', 'business_type': 'blockchain', 'full_name': '普通用户'},
        'dev': {'password': 'dev123', 'business_type': 'blockchain', 'full_name': '开发用户'},
        'test': {'password': 'test123', 'business_type': 'blockchain', 'full_name': '测试用户'},
        
        # 密码学模块客户端
        'cryptographer': {'password': 'crypto123', 'business_type': 'crypto', 'full_name': '密码学专家'},
        'security': {'password': 'security123', 'business_type': 'crypto', 'full_name': '安全工程师'},
        'audit': {'password': 'audit123', 'business_type': 'crypto', 'full_name': '审计专员'},
    },
    'server': {
        # AI模块服务器
        'server': {'password': 'admin123', 'business_type': 'ai', 'full_name': 'AI服务器管理员'},
        'admin': {'password': 'admin123', 'business_type': 'ai', 'full_name': 'AI系统管理员'},
        
        # 区块链模块服务器
        'admin': {'password': 'admin123', 'business_type': 'blockchain', 'full_name': '区块链管理员'},
        
        # 密码学模块服务器
        'crypto-admin': {'password': 'crypto123', 'business_type': 'crypto', 'full_name': '密码学管理员'},
    }
}

# 健康检查接口
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# 认证API
@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录接口"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据为空'}), 400
        
        user_type = data.get('userType')
        business_type = data.get('businessType')
        password = data.get('password')
        
        # 获取用户标识
        if user_type == 'client':
            username = data.get('username')
            if not username:
                return jsonify({'error': '用户名不能为空'}), 400
            user_id = username
        else:  # server
            admin_id = data.get('adminId')
            if not admin_id:
                return jsonify({'error': '管理员ID不能为空'}), 400
            user_id = admin_id
        
        # 验证用户
        user_data = MOCK_USERS.get(user_type, {}).get(user_id)
        if not user_data:
            return jsonify({'error': '用户不存在'}), 401
        
        # 验证密码
        if user_data['password'] != password:
            return jsonify({'error': '密码错误'}), 401
        
        # 验证业务类型
        if user_data['business_type'] != business_type:
            return jsonify({'error': '业务类型不匹配'}), 401
        
        # 生成token
        token_payload = {
            'user_id': user_id,
            'user_type': user_type,
            'business_type': business_type,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')
        
        response_data = {
            'success': True,
            'token': token,
            'user': {
                'id': user_id,
                'type': user_type,
                'businessType': business_type,
                'fullName': user_data.get('full_name', user_id)
            }
        }
        
        app.logger.info(f'用户登录成功: {user_id} ({user_type})')
        return jsonify(response_data), 200
        
    except Exception as e:
        app.logger.error(f'登录错误: {str(e)}')
        return jsonify({'error': '登录失败，请稍后重试'}), 500

@app.route('/api/auth/verify', methods=['GET'])
def verify_token():
    """验证token有效性"""
    try:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token缺失'}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            
            return jsonify({
                'valid': True,
                'user': {
                    'id': payload['user_id'],
                    'type': payload['user_type'],
                    'businessType': payload['business_type']
                }
            }), 200
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token无效'}), 401
            
    except Exception as e:
        app.logger.error(f'Token验证错误: {str(e)}')
        return jsonify({'error': '验证失败'}), 500

# AI模块API
@app.route('/api/ai/dashboard', methods=['GET'])
def ai_dashboard():
    """AI仪表盘数据"""
    return jsonify({
        'stats': {
            'trainingProjects': 23,
            'activeClients': 8,
            'pendingRequests': 3,
            'trainingTasks': 12
        },
        'recentTraining': [
            {'name': '图像分类模型', 'accuracy': 94.2, 'status': 'completed'},
            {'name': '文本分析模型', 'accuracy': 91.8, 'status': 'training'},
            {'name': '回归预测模型', 'rmse': 0.023, 'status': 'completed'}
        ]
    })

# 区块链模块API
@app.route('/api/blockchain/dashboard', methods=['GET'])
def blockchain_dashboard():
    """区块链仪表盘数据"""
    return jsonify({
        'stats': {
            'smartContracts': 12,
            'activeTransactions': 2847,
            'mpcTasks': 8,
            'networkTPS': 1256
        },
        'recentContracts': [
            {'name': '银行间信用评估联邦学习', 'status': 'active', 'participants': 4},
            {'name': '多方安全计算合约', 'status': 'waiting', 'participants': 3}
        ]
    })

# 密钥加密模块API
@app.route('/api/crypto/dashboard', methods=['GET'])
def crypto_dashboard():
    """密钥加密仪表盘数据"""
    return jsonify({
        'stats': {
            'totalKeys': 24,
            'activeKeys': 18,
            'certificates': 12,
            'expiringSoon': 3
        },
        'recentKeys': [
            {'name': '联邦学习主密钥', 'status': 'active', 'usage': 156},
            {'name': '数据传输加密密钥', 'status': 'active', 'usage': 1024},
            {'name': '临时签名密钥', 'status': 'expired', 'needsRenewal': True}
        ]
    })

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': '接口不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '服务器内部错误'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)