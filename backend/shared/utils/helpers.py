"""
辅助工具函数
提供通用的响应格式化、数据处理等功能
"""

from datetime import datetime
from flask import jsonify


def success_response(data=None, message="操作成功", code=200):
    """成功响应格式"""
    response = {
        'success': True,
        'code': code,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    return jsonify(response), code


def error_response(message="操作失败", code=400, details=None):
    """错误响应格式"""
    response = {
        'success': False,
        'code': code,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    
    if details:
        response['details'] = details
    
    return jsonify(response), code


def paginate_response(query, page, per_page, error_out=False):
    """分页响应"""
    try:
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=error_out
        )
        
        return {
            'items': [item.to_dict() if hasattr(item, 'to_dict') else item for item in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next,
                'prev_num': pagination.prev_num,
                'next_num': pagination.next_num
            }
        }
    except Exception as e:
        raise e


def format_datetime(dt):
    """格式化日期时间"""
    if dt is None:
        return None
    return dt.isoformat()


def safe_int(value, default=0):
    """安全转换为整数"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0):
    """安全转换为浮点数"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def generate_filename(original_filename, user_id):
    """生成安全的文件名"""
    import os
    import uuid
    
    # 获取文件扩展名
    ext = os.path.splitext(original_filename)[1]
    
    # 生成新文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    
    return f"{user_id}_{timestamp}_{unique_id}{ext}"


def calculate_file_hash(file_path):
    """计算文件哈希值"""
    import hashlib
    
    hash_sha256 = hashlib.sha256()
    
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        raise e


def format_file_size(size_bytes):
    """格式化文件大小"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"


def is_valid_business_type(business_type):
    """验证业务类型是否有效"""
    valid_types = ['homepage', 'ai', 'blockchain', 'crypto']
    return business_type in valid_types


def is_valid_user_type(user_type):
    """验证用户类型是否有效"""
    valid_types = ['client', 'server']
    return user_type in valid_types


def sanitize_input(text, max_length=None):
    """清理用户输入"""
    if not isinstance(text, str):
        return ""
    
    # 去除首尾空格
    text = text.strip()
    
    # 限制长度
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    # 简单的HTML标签清理（可以使用bleach库进行更严格的清理）
    import re
    text = re.sub(r'<[^>]+>', '', text)
    
    return text


def generate_session_id():
    """生成会话ID"""
    import uuid
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    unique_id = str(uuid.uuid4()).replace('-', '')[:12]
    return f"session_{timestamp}_{unique_id}"


def validate_email(email):
    """验证邮箱格式"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def mask_sensitive_data(data, fields_to_mask):
    """脱敏敏感数据"""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if key in fields_to_mask:
                if isinstance(value, str) and len(value) > 4:
                    result[key] = value[:2] + '*' * (len(value) - 4) + value[-2:]
                else:
                    result[key] = '***'
            else:
                result[key] = mask_sensitive_data(value, fields_to_mask)
        return result
    elif isinstance(data, list):
        return [mask_sensitive_data(item, fields_to_mask) for item in data]
    else:
        return data