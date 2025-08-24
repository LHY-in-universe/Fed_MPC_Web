"""
认证中间件
提供统一的身份认证和授权功能
"""

import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, jsonify, session
from werkzeug.security import check_password_hash


def generate_token(user_id, business_type, expires_in=24*60*60):
    """生成JWT令牌"""
    try:
        payload = {
            'user_id': user_id,
            'business_type': business_type,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(
            payload, 
            current_app.config['SECRET_KEY'], 
            algorithm='HS256'
        )
        
        return token
    except Exception as e:
        current_app.logger.error(f"Token generation failed: {str(e)}")
        return None


def verify_token():
    """验证JWT令牌"""
    token = None
    auth_header = request.headers.get('Authorization')
    
    if auth_header:
        try:
            # Bearer <token>
            token = auth_header.split(" ")[1]
        except IndexError:
            return False
    
    if not token:
        return False
    
    try:
        data = jwt.decode(
            token, 
            current_app.config['SECRET_KEY'], 
            algorithms=['HS256']
        )
        
        # 将用户信息保存到session中
        session['user_id'] = data['user_id']
        session['business_type'] = data['business_type']
        
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False
    except Exception:
        return False


def auth_required(f):
    """认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not verify_token():
            return jsonify({'error': '未授权访问', 'code': 401}), 401
        return f(*args, **kwargs)
    return decorated_function


def business_type_required(allowed_types):
    """业务类型限制装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not verify_token():
                return jsonify({'error': '未授权访问', 'code': 401}), 401
                
            user_business_type = session.get('business_type')
            if user_business_type not in allowed_types:
                return jsonify({
                    'error': f'权限不足，需要以下业务类型之一: {", ".join(allowed_types)}',
                    'code': 403
                }), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not verify_token():
            return jsonify({'error': '未授权访问', 'code': 401}), 401
            
        # 这里可以添加管理员权限检查逻辑
        user_id = session.get('user_id')
        from shared.services.user_service import UserService
        user = UserService.get_user_by_id(user_id)
        
        if not user or user.user_type != 'server':
            return jsonify({'error': '需要管理员权限', 'code': 403}), 403
            
        return f(*args, **kwargs)
    return decorated_function