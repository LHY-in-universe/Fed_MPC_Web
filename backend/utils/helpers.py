"""
助手工具函数
提供各种常用的辅助功能
"""

import hashlib
import secrets
import string
from datetime import datetime, timedelta
import uuid
import os
import json
from werkzeug.security import generate_password_hash
from flask import request

def generate_session_id(length=32):
    """生成会话ID"""
    return secrets.token_urlsafe(length)

def generate_api_key(length=32):
    """生成API密钥"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_random_string(length=16, include_special=False):
    """生成随机字符串"""
    alphabet = string.ascii_letters + string.digits
    if include_special:
        alphabet += "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_uuid():
    """生成UUID"""
    return str(uuid.uuid4())

def hash_password(password, salt=None):
    """哈希密码（使用Werkzeug）"""
    return generate_password_hash(password)

def hash_string(text, algorithm='sha256'):
    """计算字符串哈希值"""
    if algorithm == 'md5':
        return hashlib.md5(text.encode()).hexdigest()
    elif algorithm == 'sha1':
        return hashlib.sha1(text.encode()).hexdigest()
    elif algorithm == 'sha256':
        return hashlib.sha256(text.encode()).hexdigest()
    else:
        raise ValueError(f"不支持的哈希算法: {algorithm}")

def format_file_size(size_bytes):
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.2f} {size_names[i]}"

def format_duration(seconds):
    """格式化时长"""
    if seconds < 0:
        return "0秒"
    
    if seconds < 60:
        return f"{int(seconds)}秒"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}分{secs}秒" if secs > 0 else f"{minutes}分钟"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}小时{minutes}分钟" if minutes > 0 else f"{hours}小时"
    else:
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        return f"{days}天{hours}小时" if hours > 0 else f"{days}天"

def format_timestamp(timestamp, format_str='%Y-%m-%d %H:%M:%S'):
    """格式化时间戳"""
    if isinstance(timestamp, (int, float)):
        dt = datetime.fromtimestamp(timestamp)
    elif isinstance(timestamp, datetime):
        dt = timestamp
    else:
        return str(timestamp)
    
    return dt.strftime(format_str)

def parse_datetime(date_string, format_str='%Y-%m-%d %H:%M:%S'):
    """解析日期时间字符串"""
    try:
        return datetime.strptime(date_string, format_str)
    except ValueError:
        # 尝试ISO格式
        try:
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except ValueError:
            return None

def get_client_ip():
    """获取客户端IP地址"""
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0].split(',')[0]
    return request.remote_addr

def get_user_agent():
    """获取用户代理字符串"""
    return request.headers.get('User-Agent', '')

def safe_json_loads(json_str, default=None):
    """安全的JSON解析"""
    if not json_str:
        return default
    
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(obj, ensure_ascii=False):
    """安全的JSON序列化"""
    try:
        return json.dumps(obj, ensure_ascii=ensure_ascii, default=str)
    except (TypeError, ValueError):
        return "{}"

def sanitize_filename(filename):
    """清理文件名，移除不安全字符"""
    # 移除路径分隔符和其他危险字符
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # 移除首尾空白
    filename = filename.strip()
    
    # 如果文件名为空，生成一个默认名
    if not filename:
        filename = f"file_{generate_random_string(8)}"
    
    return filename

def create_directory_if_not_exists(directory_path):
    """如果目录不存在则创建"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)
        return True
    return False

def is_safe_path(basedir, path):
    """检查路径是否安全（防止路径遍历攻击）"""
    # 获取规范化的绝对路径
    basedir = os.path.abspath(basedir)
    path = os.path.abspath(path)
    
    # 检查路径是否在基目录内
    return os.path.commonpath([basedir, path]) == basedir

def calculate_pagination_info(total_items, page, page_size):
    """计算分页信息"""
    total_pages = (total_items + page_size - 1) // page_size
    has_prev = page > 1
    has_next = page < total_pages
    start_index = (page - 1) * page_size
    end_index = min(start_index + page_size, total_items)
    
    return {
        'total_items': total_items,
        'total_pages': total_pages,
        'current_page': page,
        'page_size': page_size,
        'has_prev': has_prev,
        'has_next': has_next,
        'prev_page': page - 1 if has_prev else None,
        'next_page': page + 1 if has_next else None,
        'start_index': start_index + 1,  # 1-based for display
        'end_index': end_index
    }

def generate_verification_code(length=6, digits_only=True):
    """生成验证码"""
    if digits_only:
        alphabet = string.digits
    else:
        alphabet = string.ascii_uppercase + string.digits
    
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def mask_sensitive_data(data, fields_to_mask=None):
    """遮蔽敏感数据"""
    if fields_to_mask is None:
        fields_to_mask = ['password', 'token', 'secret', 'key', 'credential']
    
    if isinstance(data, dict):
        masked_data = {}
        for key, value in data.items():
            if any(sensitive_field in key.lower() for sensitive_field in fields_to_mask):
                masked_data[key] = "***"
            elif isinstance(value, (dict, list)):
                masked_data[key] = mask_sensitive_data(value, fields_to_mask)
            else:
                masked_data[key] = value
        return masked_data
    elif isinstance(data, list):
        return [mask_sensitive_data(item, fields_to_mask) for item in data]
    else:
        return data

def truncate_string(text, max_length=100, suffix="..."):
    """截断字符串"""
    if not text:
        return text
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def deep_merge_dict(dict1, dict2):
    """深度合并字典"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dict(result[key], value)
        else:
            result[key] = value
    
    return result

def validate_and_convert_number(value, data_type=int, min_value=None, max_value=None):
    """验证并转换数字"""
    try:
        converted_value = data_type(value)
        
        if min_value is not None and converted_value < min_value:
            raise ValueError(f"值不能小于 {min_value}")
        
        if max_value is not None and converted_value > max_value:
            raise ValueError(f"值不能大于 {max_value}")
        
        return converted_value, None
    except (ValueError, TypeError) as e:
        return None, str(e)

def get_file_extension(filename):
    """获取文件扩展名"""
    if not filename or '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[1].lower()

def is_valid_file_type(filename, allowed_extensions):
    """检查文件类型是否有效"""
    if not allowed_extensions:
        return True
    
    ext = get_file_extension(filename)
    return ext in [e.lower() for e in allowed_extensions]

def generate_download_token(user_id, resource_id, expires_in=3600):
    """生成下载令牌"""
    import jwt
    from flask import current_app
    
    payload = {
        'user_id': user_id,
        'resource_id': resource_id,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'type': 'download'
    }
    
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def verify_download_token(token):
    """验证下载令牌"""
    import jwt
    from flask import current_app
    
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        if payload.get('type') != 'download':
            return None, "Invalid token type"
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "Token has expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"

def create_response_dict(success=True, message=None, data=None, **kwargs):
    """创建标准响应字典"""
    response = {
        'success': success,
        'timestamp': datetime.utcnow().isoformat(),
    }
    
    if message:
        response['message'] = message
    
    if data is not None:
        response['data'] = data
    
    # 添加其他参数
    response.update(kwargs)
    
    return response