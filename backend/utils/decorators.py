"""
装饰器工具函数
提供各种常用装饰器
"""

import time
from functools import wraps
from flask import request, jsonify, g
from datetime import datetime, timedelta
import json

def require_business_type(*allowed_types):
    """要求特定业务类型的装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            if current_user.business_type.value not in allowed_types:
                return jsonify({
                    'error': 'Business Type Not Allowed',
                    'message': f'此功能仅支持 {", ".join(allowed_types)} 业务类型'
                }), 403
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator

def require_user_type(*allowed_types):
    """要求特定用户类型的装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            if current_user.user_type.value not in allowed_types:
                return jsonify({
                    'error': 'User Type Not Allowed',
                    'message': f'此功能仅限 {", ".join(allowed_types)} 用户使用'
                }), 403
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator

def log_api_call(category='api', level='info'):
    """记录API调用的装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            # 获取当前用户（如果有）
            current_user = None
            if hasattr(g, 'current_user'):
                current_user = g.current_user
            elif len(args) > 0 and hasattr(args[0], 'id'):
                current_user = args[0]
            
            try:
                # 执行函数
                result = f(*args, **kwargs)
                
                # 计算执行时间
                execution_time = (time.time() - start_time) * 1000
                
                # 记录成功调用日志
                from models.system_log import SystemLog
                SystemLog.log_api(
                    method=request.method,
                    path=request.path,
                    user_id=current_user.id if current_user else None,
                    ip_address=get_client_ip(),
                    execution_time=execution_time
                )
                
                return result
                
            except Exception as e:
                # 计算执行时间
                execution_time = (time.time() - start_time) * 1000
                
                # 记录错误日志
                from models.system_log import SystemLog
                SystemLog.log_error(
                    category=category,
                    message=f'API调用失败: {str(e)}',
                    user_id=current_user.id if current_user else None,
                    operation=f'{request.method} {request.path}',
                    ip_address=get_client_ip(),
                    execution_time=execution_time,
                    error_details=str(e)
                )
                
                # 重新抛出异常
                raise
                
        return decorated_function
    return decorator

def validate_json(*required_fields):
    """验证JSON请求体的装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'error': 'Invalid Content Type',
                    'message': '请求必须是JSON格式'
                }), 400
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'error': 'Empty Request Body',
                    'message': '请求体不能为空'
                }), 400
            
            # 检查必需字段
            missing_fields = [field for field in required_fields if field not in data or data[field] is None]
            if missing_fields:
                return jsonify({
                    'error': 'Missing Required Fields',
                    'message': f'缺少必需字段: {", ".join(missing_fields)}'
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def rate_limit(max_requests=100, window=3600, key_func=None):
    """简单的限流装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 生成限流key
            if key_func:
                key = key_func()
            else:
                key = get_client_ip()
            
            # 简单的内存限流实现（生产环境应该使用Redis）
            if not hasattr(rate_limit, 'requests'):
                rate_limit.requests = {}
            
            now = time.time()
            window_start = now - window
            
            # 清理过期记录
            if key in rate_limit.requests:
                rate_limit.requests[key] = [req_time for req_time in rate_limit.requests[key] if req_time > window_start]
            else:
                rate_limit.requests[key] = []
            
            # 检查是否超过限制
            if len(rate_limit.requests[key]) >= max_requests:
                return jsonify({
                    'error': 'Rate Limit Exceeded',
                    'message': f'请求频率过高，每{window}秒最多{max_requests}次请求'
                }), 429
            
            # 记录当前请求
            rate_limit.requests[key].append(now)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def cache_response(timeout=300, key_func=None):
    """简单的响应缓存装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 生成缓存key
            if key_func:
                cache_key = key_func()
            else:
                cache_key = f"{request.path}:{request.args}"
            
            # 简单的内存缓存实现（生产环境应该使用Redis）
            if not hasattr(cache_response, 'cache'):
                cache_response.cache = {}
            
            now = time.time()
            
            # 检查缓存
            if cache_key in cache_response.cache:
                cached_data, cached_time = cache_response.cache[cache_key]
                if now - cached_time < timeout:
                    return cached_data
            
            # 执行函数并缓存结果
            result = f(*args, **kwargs)
            cache_response.cache[cache_key] = (result, now)
            
            return result
        return decorated_function
    return decorator

def require_permissions(*permissions):
    """要求特定权限的装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            user_permissions = current_user.get_permissions()
            
            missing_permissions = []
            for permission in permissions:
                if permission not in user_permissions:
                    missing_permissions.append(permission)
            
            if missing_permissions:
                return jsonify({
                    'error': 'Insufficient Permissions',
                    'message': f'缺少权限: {", ".join(missing_permissions)}'
                }), 403
            
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator

def async_task(func):
    """异步任务装饰器（简单实现）"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        import threading
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread
    return wrapper

def retry_on_failure(max_retries=3, delay=1, exceptions=(Exception,)):
    """失败重试装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        time.sleep(delay * (attempt + 1))  # 指数退避
                        continue
                    else:
                        raise last_exception
            
        return decorated_function
    return decorator

def measure_time(func):
    """测量函数执行时间的装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            print(f"{func.__name__} 执行时间: {execution_time:.4f}秒")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"{func.__name__} 执行失败，耗时: {execution_time:.4f}秒，错误: {str(e)}")
            raise
    return wrapper

def get_client_ip():
    """获取客户端真实IP地址"""
    # 优先获取代理服务器传递的真实IP
    forwarded_ips = request.headers.get('X-Forwarded-For')
    if forwarded_ips:
        return forwarded_ips.split(',')[0].strip()
    
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    # 获取直接连接的IP
    return request.remote_addr