"""
认证相关路由
处理用户登录、登出、token验证等功能
"""

from flask import Blueprint, request, jsonify, session
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import logging

auth_bp = Blueprint('auth', __name__)

def get_user_permissions(user_type, business_type):
    """根据用户类型和业务类型获取权限列表"""
    permissions = []
    
    if user_type == 'client':
        if business_type == 'ai':
            permissions = [
                'create_local_project',
                'view_own_projects',
                'submit_training_request', 
                'view_training_progress',
                'download_own_models',
                'manage_datasets',
                'view_model_metrics'
            ]
        elif business_type == 'blockchain':
            permissions = [
                'create_transactions',
                'view_own_transactions',
                'manage_wallet',
                'view_blockchain_info',
                'participate_in_consensus'
            ]
        elif business_type == 'crypto':
            permissions = [
                'generate_keys',
                'encrypt_decrypt',
                'digital_signature',
                'key_exchange',
                'view_crypto_operations'
            ]
    elif user_type == 'server':
        if business_type == 'ai':
            permissions = [
                'manage_all_clients',
                'approve_training_requests',
                'view_global_projects',
                'manage_models',
                'system_configuration',
                'view_system_logs',
                'monitor_training',
                'manage_federated_learning'
            ]
        elif business_type == 'blockchain':
            permissions = [
                'manage_blockchain_network',
                'validate_transactions',
                'manage_consensus',
                'view_all_transactions',
                'system_administration',
                'node_management'
            ]
        elif business_type == 'crypto':
            permissions = [
                'manage_key_infrastructure',
                'audit_crypto_operations',
                'system_security_config',
                'manage_certificates',
                'security_monitoring',
                'compliance_reporting'
            ]
    
    return permissions

# 模拟用户数据库（实际应用中应使用数据库）
MOCK_USERS = {
    'client': {
        # AI模块客户端
        'client1': {'password': '123456', 'address': 'http://client1.ai.com', 'business_type': 'ai', 'full_name': '客户端1', 'organization': 'AI科技公司'},
        'client2': {'password': '123456', 'address': 'http://client2.ai.com', 'business_type': 'ai', 'full_name': '客户端2', 'organization': 'AI研发中心'},
        '上海一厂': {'password': 'password123', 'address': 'http://shanghai.client.com', 'business_type': 'ai', 'full_name': '上海第一工厂', 'organization': '上海制造集团'},
        '武汉二厂': {'password': 'password123', 'address': 'http://wuhan.client.com', 'business_type': 'ai', 'full_name': '武汉第二工厂', 'organization': '武汉工业园'},
        '西安三厂': {'password': 'password123', 'address': 'http://xian.client.com', 'business_type': 'ai', 'full_name': '西安第三工厂', 'organization': '西安高新区'},
        '广州四厂': {'password': 'password123', 'address': 'http://guangzhou.client.com', 'business_type': 'ai', 'full_name': '广州第四工厂', 'organization': '广州科技园'},
        
        # 区块链模块客户端
        'user': {'password': 'user123', 'address': 'http://user.blockchain.com', 'business_type': 'blockchain', 'full_name': '普通用户', 'organization': '金融用户'},
        'dev': {'password': 'dev123', 'address': 'http://dev.blockchain.com', 'business_type': 'blockchain', 'full_name': '开发用户', 'organization': '技术开发部'},
        'test': {'password': 'test123', 'address': 'http://test.blockchain.com', 'business_type': 'blockchain', 'full_name': '测试用户', 'organization': '测试部门'},
        '工商银行': {'password': 'password123', 'address': 'http://icbc.bank.com', 'business_type': 'blockchain', 'full_name': '中国工商银行', 'organization': '国有大型银行'},
        '建设银行': {'password': 'password123', 'address': 'http://ccb.bank.com', 'business_type': 'blockchain', 'full_name': '中国建设银行', 'organization': '国有大型银行'},
        '招商银行': {'password': 'password123', 'address': 'http://cmb.bank.com', 'business_type': 'blockchain', 'full_name': '招商银行', 'organization': '股份制银行'},
        
        # 密码学模块客户端
        'cryptographer': {'password': 'crypto123', 'address': 'http://crypto.secure.com', 'business_type': 'crypto', 'full_name': '密码学专家', 'organization': '密码学研究院'},
        'security': {'password': 'security123', 'address': 'http://security.secure.com', 'business_type': 'crypto', 'full_name': '安全工程师', 'organization': '网络安全部'},
        'audit': {'password': 'audit123', 'address': 'http://audit.secure.com', 'business_type': 'crypto', 'full_name': '审计专员', 'organization': '安全审计部'},
    },
    'server': {
        # AI模块服务器
        'server': {'password': 'admin123', 'business_type': 'ai', 'full_name': 'AI服务器管理员', 'organization': 'AI平台管理'},
        'admin': {'password': 'admin123', 'business_type': 'ai', 'full_name': 'AI系统管理员', 'organization': 'AI平台管理'},
        'demo-admin': {'password': 'demo123', 'business_type': 'ai', 'full_name': 'AI演示管理员', 'organization': 'AI演示平台'},
        
        # 区块链模块服务器
        'admin': {'password': 'admin123', 'business_type': 'blockchain', 'full_name': '区块链管理员', 'organization': '区块链平台管理'},
        'blockchain-admin': {'password': 'admin123', 'business_type': 'blockchain', 'full_name': '区块链系统管理员', 'organization': '区块链平台管理'},
        'dev': {'password': 'dev123', 'business_type': 'blockchain', 'full_name': '区块链开发管理员', 'organization': '区块链开发团队'},
        
        # 密码学模块服务器
        'crypto-admin': {'password': 'crypto123', 'business_type': 'crypto', 'full_name': '密码学管理员', 'organization': '密码学平台管理'},
        'security-admin': {'password': 'security123', 'business_type': 'crypto', 'full_name': '安全管理员', 'organization': '安全管理部门'},
        'dev': {'password': 'dev123', 'business_type': 'crypto', 'full_name': '密码学开发管理员', 'organization': '密码学开发团队'},
    }
}

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录接口
    
    请求参数:
    - username/adminId: 用户名或管理员ID
    - password: 密码
    - userType: 用户类型 (client/server)
    - businessType: 业务类型 (ai/blockchain)
    - clientAddress/serverAddress: 客户端或服务器地址
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据为空'}), 400
        
        user_type = data.get('userType')
        business_type = data.get('businessType')
        password = data.get('password')
        
        if user_type not in ['client', 'server']:
            return jsonify({'error': '无效的用户类型'}), 400
        
        if business_type not in ['ai', 'blockchain', 'crypto']:
            return jsonify({'error': '无效的业务类型'}), 400
        
        # 获取用户标识
        if user_type == 'client':
            username = data.get('username')
            client_address = data.get('clientAddress')
            if not username or not client_address:
                return jsonify({'error': '用户名和客户端地址不能为空'}), 400
            user_id = username
        else:  # server
            admin_id = data.get('adminId')
            server_address = data.get('serverAddress')
            if not admin_id or not server_address:
                return jsonify({'error': '管理员ID和服务器地址不能为空'}), 400
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
        
        # 使用配置文件中的SECRET_KEY
        from flask import current_app
        token = jwt.encode(token_payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        # 构建响应数据
        response_data = {
            'success': True,
            'token': token,
            'user': {
                'id': user_id,
                'type': user_type,
                'businessType': business_type,
                'fullName': user_data.get('full_name', user_id),
                'organization': user_data.get('organization', ''),
                'permissions': get_user_permissions(user_type, business_type)
            }
        }
        
        if user_type == 'client':
            response_data['user']['clientAddress'] = data.get('clientAddress')
        else:
            response_data['user']['serverAddress'] = data.get('serverAddress')
        
        logging.info(f'用户登录成功: {user_id} ({user_type})')
        return jsonify(response_data), 200
        
    except Exception as e:
        logging.error(f'登录错误: {str(e)}')
        return jsonify({'error': '登录失败，请稍后重试'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    用户登出接口
    """
    try:
        # 清除会话
        session.clear()
        
        return jsonify({
            'success': True,
            'message': '登出成功'
        }), 200
        
    except Exception as e:
        logging.error(f'登出错误: {str(e)}')
        return jsonify({'error': '登出失败'}), 500

@auth_bp.route('/verify', methods=['GET'])
def verify_token():
    """
    验证token有效性
    """
    try:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token缺失'}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            # 使用配置文件中的SECRET_KEY
            from flask import current_app
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            
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
        logging.error(f'Token验证错误: {str(e)}')
        return jsonify({'error': '验证失败'}), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """
    刷新token
    """
    try:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token缺失'}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            # 使用配置文件中的SECRET_KEY
            from flask import current_app
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            
            # 生成新token
            new_payload = {
                'user_id': payload['user_id'],
                'user_type': payload['user_type'],
                'business_type': payload['business_type'],
                'exp': datetime.utcnow() + timedelta(hours=24)
            }
            
            new_token = jwt.encode(new_payload, current_app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({
                'success': True,
                'token': new_token
            }), 200
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token已过期，请重新登录'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token无效'}), 401
            
    except Exception as e:
        logging.error(f'Token刷新错误: {str(e)}')
        return jsonify({'error': '刷新失败'}), 500

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """
    修改密码接口
    TODO: 后续实现
    """
    return jsonify({
        'error': '此功能暂未实现',
        'message': '请联系管理员修改密码'
    }), 501

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册接口
    TODO: 后续实现
    """
    return jsonify({
        'error': '此功能暂未实现',
        'message': '请联系管理员创建账号'
    }), 501