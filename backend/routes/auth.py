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

# 模拟用户数据库（实际应用中应使用数据库）
MOCK_USERS = {
    'client': {
        '上海一厂': {'password': 'password123', 'address': 'http://shanghai.client.com', 'business_type': 'ai'},
        '武汉二厂': {'password': 'password123', 'address': 'http://wuhan.client.com', 'business_type': 'ai'},
        '西安三厂': {'password': 'password123', 'address': 'http://xian.client.com', 'business_type': 'ai'},
        '广州四厂': {'password': 'password123', 'address': 'http://guangzhou.client.com', 'business_type': 'ai'},
        '工商银行': {'password': 'password123', 'address': 'http://icbc.bank.com', 'business_type': 'blockchain'},
        '建设银行': {'password': 'password123', 'address': 'http://ccb.bank.com', 'business_type': 'blockchain'},
        '招商银行': {'password': 'password123', 'address': 'http://cmb.bank.com', 'business_type': 'blockchain'},
    },
    'server': {
        'admin': {'password': 'admin123', 'business_type': 'ai'},
        'blockchain-admin': {'password': 'admin123', 'business_type': 'blockchain'},
        'demo-admin': {'password': 'demo123', 'business_type': 'ai'},
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
        
        if business_type not in ['ai', 'blockchain']:
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
        
        # TODO: 使用实际的SECRET_KEY
        token = jwt.encode(token_payload, 'secret_key', algorithm='HS256')
        
        # 构建响应数据
        response_data = {
            'success': True,
            'token': token,
            'user': {
                'id': user_id,
                'type': user_type,
                'businessType': business_type
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
            # TODO: 使用实际的SECRET_KEY
            payload = jwt.decode(token, 'secret_key', algorithms=['HS256'])
            
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
            # TODO: 使用实际的SECRET_KEY
            payload = jwt.decode(token, 'secret_key', algorithms=['HS256'])
            
            # 生成新token
            new_payload = {
                'user_id': payload['user_id'],
                'user_type': payload['user_type'],
                'business_type': payload['business_type'],
                'exp': datetime.utcnow() + timedelta(hours=24)
            }
            
            new_token = jwt.encode(new_payload, 'secret_key', algorithm='HS256')
            
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