"""
验证工具函数
提供各种数据验证功能
"""

import re
import ipaddress
from urllib.parse import urlparse
from functools import wraps
from flask import request, jsonify

def validate_email(email):
    """验证邮箱格式"""
    if not email:
        return False, "邮箱不能为空"
    
    email_pattern = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    if not email_pattern.match(email):
        return False, "邮箱格式不正确"
    
    if len(email) > 100:
        return False, "邮箱长度不能超过100个字符"
    
    return True, None

def validate_username(username):
    """验证用户名格式"""
    if not username:
        return False, "用户名不能为空"
    
    if len(username) < 2:
        return False, "用户名长度不能少于2个字符"
    
    if len(username) > 50:
        return False, "用户名长度不能超过50个字符"
    
    # 允许字母、数字、中文、下划线、短横线
    username_pattern = re.compile(r'^[a-zA-Z0-9\u4e00-\u9fa5_-]+$')
    if not username_pattern.match(username):
        return False, "用户名只能包含字母、数字、中文、下划线和短横线"
    
    return True, None

def validate_password(password):
    """验证密码强度"""
    if not password:
        return False, "密码不能为空"
    
    if len(password) < 6:
        return False, "密码长度不能少于6个字符"
    
    if len(password) > 128:
        return False, "密码长度不能超过128个字符"
    
    # 检查是否包含空白字符
    if re.search(r'\s', password):
        return False, "密码不能包含空白字符"
    
    return True, None

def validate_strong_password(password):
    """验证强密码（更严格的要求）"""
    basic_valid, basic_msg = validate_password(password)
    if not basic_valid:
        return False, basic_msg
    
    # 至少包含一个字母
    if not re.search(r'[a-zA-Z]', password):
        return False, "密码必须包含至少一个字母"
    
    # 至少包含一个数字
    if not re.search(r'[0-9]', password):
        return False, "密码必须包含至少一个数字"
    
    # 如果长度小于8，要求包含特殊字符
    if len(password) < 8:
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "密码长度小于8位时必须包含特殊字符"
    
    return True, None

def validate_project_name(name):
    """验证项目名称"""
    if not name:
        return False, "项目名称不能为空"
    
    if len(name) < 1:
        return False, "项目名称不能为空"
    
    if len(name) > 100:
        return False, "项目名称长度不能超过100个字符"
    
    # 不允许特殊字符
    if re.search(r'[<>:"/\\|?*]', name):
        return False, "项目名称不能包含特殊字符 < > : \" / \\ | ? *"
    
    return True, None

def validate_ip_address(ip):
    """验证IP地址格式"""
    if not ip:
        return False, "IP地址不能为空"
    
    try:
        ipaddress.ip_address(ip)
        return True, None
    except ValueError:
        return False, "IP地址格式不正确"

def validate_url(url):
    """验证URL格式"""
    if not url:
        return False, "URL不能为空"
    
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return False, "URL格式不正确"
        
        if result.scheme not in ['http', 'https']:
            return False, "URL必须使用http或https协议"
        
        return True, None
    except Exception:
        return False, "URL格式不正确"

def validate_phone_number(phone):
    """验证手机号码格式（中国大陆）"""
    if not phone:
        return False, "手机号码不能为空"
    
    # 中国大陆手机号格式
    phone_pattern = re.compile(r'^1[3-9]\d{9}$')
    if not phone_pattern.match(phone):
        return False, "手机号码格式不正确"
    
    return True, None

def validate_business_type(business_type):
    """验证业务类型"""
    valid_types = ['ai', 'blockchain']
    if business_type not in valid_types:
        return False, f"业务类型必须是 {', '.join(valid_types)} 之一"
    
    return True, None

def validate_user_type(user_type):
    """验证用户类型"""
    valid_types = ['client', 'server']
    if user_type not in valid_types:
        return False, f"用户类型必须是 {', '.join(valid_types)} 之一"
    
    return True, None

def validate_training_mode(training_mode):
    """验证训练模式"""
    valid_modes = ['normal', 'mpc']
    if training_mode not in valid_modes:
        return False, f"训练模式必须是 {', '.join(valid_modes)} 之一"
    
    return True, None

def validate_json_fields(data, required_fields, optional_fields=None):
    """验证JSON数据包含必需字段"""
    if not isinstance(data, dict):
        return False, "数据必须是JSON对象"
    
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"缺少必需字段: {', '.join(missing_fields)}"
    
    # 检查是否有无效字段
    if optional_fields is not None:
        all_valid_fields = set(required_fields + optional_fields)
        invalid_fields = set(data.keys()) - all_valid_fields
        if invalid_fields:
            return False, f"包含无效字段: {', '.join(invalid_fields)}"
    
    return True, None

def validate_pagination_params(page=1, page_size=20, max_page_size=100):
    """验证分页参数"""
    try:
        page = int(page)
        page_size = int(page_size)
    except (TypeError, ValueError):
        return False, "分页参数必须是整数", None, None
    
    if page < 1:
        return False, "页码必须大于0", None, None
    
    if page_size < 1:
        return False, "每页大小必须大于0", None, None
    
    if page_size > max_page_size:
        return False, f"每页大小不能超过{max_page_size}", None, None
    
    return True, None, page, page_size

def validate_file_upload(file, allowed_extensions=None, max_size=None):
    """验证文件上传"""
    if not file:
        return False, "没有选择文件"
    
    if not file.filename:
        return False, "文件名不能为空"
    
    # 检查文件扩展名
    if allowed_extensions:
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if ext not in allowed_extensions:
            return False, f"不支持的文件类型，允许的类型: {', '.join(allowed_extensions)}"
    
    # 检查文件大小
    if max_size:
        file.seek(0, 2)  # 移动到文件末尾
        size = file.tell()
        file.seek(0)  # 重置到文件开始
        
        if size > max_size:
            return False, f"文件大小超过限制，最大允许: {max_size / (1024*1024):.1f}MB"
    
    return True, None

def validate_training_config(config):
    """验证训练配置"""
    if not isinstance(config, dict):
        return False, "训练配置必须是JSON对象"
    
    # 验证轮数
    total_rounds = config.get('total_rounds')
    if total_rounds is not None:
        if not isinstance(total_rounds, int) or total_rounds <= 0:
            return False, "训练轮数必须是正整数"
        if total_rounds > 10000:
            return False, "训练轮数不能超过10000"
    
    # 验证学习率
    learning_rate = config.get('learning_rate')
    if learning_rate is not None:
        if not isinstance(learning_rate, (int, float)) or learning_rate <= 0:
            return False, "学习率必须是正数"
        if learning_rate > 1:
            return False, "学习率不能大于1"
    
    # 验证批次大小
    batch_size = config.get('batch_size')
    if batch_size is not None:
        if not isinstance(batch_size, int) or batch_size <= 0:
            return False, "批次大小必须是正整数"
        if batch_size > 10000:
            return False, "批次大小不能超过10000"
    
    return True, None

# 装饰器形式的验证函数
def validate_json_request(required_fields, optional_fields=None):
    """装饰器：验证JSON请求"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'error': 'Invalid Content Type',
                    'message': '请求必须是JSON格式'
                }), 400
            
            data = request.get_json()
            valid, message = validate_json_fields(data, required_fields, optional_fields)
            
            if not valid:
                return jsonify({
                    'error': 'Validation Error',
                    'message': message
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_user_access(resource_user_id_field='user_id'):
    """装饰器：验证用户只能访问自己的资源"""
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            # 服务器管理员可以访问所有资源
            if current_user.is_server():
                return f(current_user, *args, **kwargs)
            
            # 客户端用户只能访问自己的资源
            data = request.get_json() if request.is_json else {}
            
            # 从请求数据或URL参数中获取资源的用户ID
            resource_user_id = data.get(resource_user_id_field) or request.args.get(resource_user_id_field)
            
            if resource_user_id and int(resource_user_id) != current_user.id:
                return jsonify({
                    'error': 'Access Denied',
                    'message': '您只能访问自己的资源'
                }), 403
            
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator