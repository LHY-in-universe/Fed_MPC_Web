"""
数据验证工具
提供各种数据验证和清理功能
"""

import re
import json
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


def validate_request_data(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """验证请求数据是否包含必填字段"""
    if not isinstance(data, dict):
        return False
    
    for field in required_fields:
        if field not in data or data[field] is None:
            return False
        
        # 检查字符串字段是否为空
        if isinstance(data[field], str) and not data[field].strip():
            return False
    
    return True


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    if not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def validate_username(username: str) -> bool:
    """验证用户名格式"""
    if not isinstance(username, str):
        return False
    
    username = username.strip()
    
    # 用户名长度3-20位，只能包含字母、数字、下划线
    if len(username) < 3 or len(username) > 20:
        return False
    
    pattern = r'^[a-zA-Z0-9_]+$'
    return bool(re.match(pattern, username))


def validate_password(password: str) -> Dict[str, Union[bool, str]]:
    """验证密码强度"""
    if not isinstance(password, str):
        return {'valid': False, 'message': '密码必须是字符串'}
    
    if len(password) < 6:
        return {'valid': False, 'message': '密码长度至少6位'}
    
    if len(password) > 128:
        return {'valid': False, 'message': '密码长度不能超过128位'}
    
    # 检查是否包含字母和数字
    has_letter = bool(re.search(r'[a-zA-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    
    if not (has_letter and has_digit):
        return {'valid': False, 'message': '密码必须包含字母和数字'}
    
    return {'valid': True, 'message': '密码格式正确'}


def validate_business_type(business_type: str) -> bool:
    """验证业务类型"""
    valid_types = ['homepage', 'ai', 'blockchain', 'crypto']
    return business_type in valid_types


def validate_user_type(user_type: str) -> bool:
    """验证用户类型"""
    valid_types = ['client', 'server']
    return user_type in valid_types


def validate_training_mode(training_mode: str) -> bool:
    """验证训练模式"""
    valid_modes = ['normal', 'mpc']
    return training_mode in valid_modes


def validate_project_type(project_type: str) -> bool:
    """验证项目类型"""
    valid_types = ['local', 'federated']
    return project_type in valid_types


def validate_model_type(model_type: str) -> bool:
    """验证模型类型"""
    valid_types = ['cnn', 'rnn', 'lstm', 'transformer', 'mlp', 'resnet', 'bert']
    return model_type.lower() in valid_types


def validate_json_data(data: str) -> Dict[str, Union[bool, Any, str]]:
    """验证JSON数据格式"""
    try:
        parsed_data = json.loads(data)
        return {'valid': True, 'data': parsed_data, 'message': 'JSON格式正确'}
    except json.JSONDecodeError as e:
        return {'valid': False, 'data': None, 'message': f'JSON格式错误: {str(e)}'}


def validate_numeric_range(value: Union[int, float], min_val: Optional[Union[int, float]] = None, 
                          max_val: Optional[Union[int, float]] = None) -> bool:
    """验证数值范围"""
    if not isinstance(value, (int, float)):
        return False
    
    if min_val is not None and value < min_val:
        return False
    
    if max_val is not None and value > max_val:
        return False
    
    return True


def validate_learning_rate(learning_rate: Union[int, float]) -> bool:
    """验证学习率"""
    return validate_numeric_range(learning_rate, 0.0001, 1.0)


def validate_epochs(epochs: int) -> bool:
    """验证训练轮数"""
    return isinstance(epochs, int) and validate_numeric_range(epochs, 1, 10000)


def validate_batch_size(batch_size: int) -> bool:
    """验证批次大小"""
    return isinstance(batch_size, int) and validate_numeric_range(batch_size, 1, 1024)


def validate_key_type(key_type: str) -> bool:
    """验证密钥类型"""
    valid_types = ['RSA', 'AES', 'ECC', 'DSA']
    return key_type.upper() in valid_types


def validate_key_size(key_type: str, key_size: int) -> bool:
    """验证密钥长度"""
    key_type = key_type.upper()
    
    valid_sizes = {
        'RSA': [1024, 2048, 3072, 4096],
        'AES': [128, 192, 256],
        'ECC': [256, 384, 521],
        'DSA': [1024, 2048, 3072]
    }
    
    return key_type in valid_sizes and key_size in valid_sizes[key_type]


def validate_certificate_type(cert_type: str) -> bool:
    """验证证书类型"""
    valid_types = ['self_signed', 'ca_signed', 'intermediate', 'root']
    return cert_type in valid_types


def validate_operation_type(operation_type: str) -> bool:
    """验证操作类型"""
    valid_types = ['encrypt', 'decrypt', 'sign', 'verify', 'key_generate', 'cert_create', 'cert_revoke']
    return operation_type in valid_types


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """验证文件扩展名"""
    if not isinstance(filename, str) or '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in [ext.lower() for ext in allowed_extensions]


def validate_file_size(file_size: int, max_size_mb: int = 100) -> bool:
    """验证文件大小"""
    max_size_bytes = max_size_mb * 1024 * 1024
    return isinstance(file_size, int) and 0 < file_size <= max_size_bytes


def sanitize_string(text: str, max_length: int = 255) -> str:
    """清理字符串输入"""
    if not isinstance(text, str):
        return ""
    
    # 去除首尾空格
    text = text.strip()
    
    # 限制长度
    if len(text) > max_length:
        text = text[:max_length]
    
    # 移除危险字符
    dangerous_chars = ['<', '>', '"', "'", '&', '\0', '\n', '\r', '\t']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text


def validate_ip_address(ip: str) -> bool:
    """验证IP地址格式"""
    if not isinstance(ip, str):
        return False
    
    # IPv4格式验证
    ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    if re.match(ipv4_pattern, ip):
        return True
    
    # IPv6格式验证（简化）
    ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    if re.match(ipv6_pattern, ip):
        return True
    
    return False


def validate_port(port: Union[int, str]) -> bool:
    """验证端口号"""
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except (ValueError, TypeError):
        return False


def validate_datetime_string(datetime_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> bool:
    """验证日期时间字符串格式"""
    try:
        datetime.strptime(datetime_str, format_str)
        return True
    except (ValueError, TypeError):
        return False


def validate_pagination_params(page: Union[int, str], per_page: Union[int, str]) -> Dict[str, Union[bool, int, str]]:
    """验证分页参数"""
    try:
        page_num = int(page)
        per_page_num = int(per_page)
        
        if page_num < 1:
            return {'valid': False, 'message': '页码必须大于0'}
        
        if per_page_num < 1 or per_page_num > 100:
            return {'valid': False, 'message': '每页条数必须在1-100之间'}
        
        return {'valid': True, 'page': page_num, 'per_page': per_page_num}
    except (ValueError, TypeError):
        return {'valid': False, 'message': '分页参数必须是数字'}


class ValidationError(Exception):
    """验证错误异常"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


def validate_or_raise(condition: bool, message: str, field: str = None):
    """验证条件，不满足则抛出异常"""
    if not condition:
        raise ValidationError(message, field)


def validate_training_config(config: Dict[str, Any]) -> Dict[str, Union[bool, str]]:
    """验证训练配置"""
    try:
        # 验证必填字段
        required_fields = ['model_type', 'learning_rate', 'epochs', 'batch_size']
        if not validate_request_data(config, required_fields):
            return {'valid': False, 'message': '缺少必填字段'}
        
        # 验证模型类型
        if not validate_model_type(config['model_type']):
            return {'valid': False, 'message': '无效的模型类型'}
        
        # 验证学习率
        if not validate_learning_rate(config['learning_rate']):
            return {'valid': False, 'message': '学习率必须在0.0001-1.0之间'}
        
        # 验证训练轮数
        if not validate_epochs(config['epochs']):
            return {'valid': False, 'message': '训练轮数必须在1-10000之间'}
        
        # 验证批次大小
        if not validate_batch_size(config['batch_size']):
            return {'valid': False, 'message': '批次大小必须在1-1024之间'}
        
        return {'valid': True, 'message': '配置验证通过'}
    
    except Exception as e:
        return {'valid': False, 'message': f'配置验证失败: {str(e)}'}


def validate_crypto_config(config: Dict[str, Any]) -> Dict[str, Union[bool, str]]:
    """验证加密配置"""
    try:
        # 验证必填字段
        required_fields = ['key_type', 'key_size', 'usage_purpose']
        if not validate_request_data(config, required_fields):
            return {'valid': False, 'message': '缺少必填字段'}
        
        # 验证密钥类型
        if not validate_key_type(config['key_type']):
            return {'valid': False, 'message': '无效的密钥类型'}
        
        # 验证密钥长度
        if not validate_key_size(config['key_type'], config['key_size']):
            return {'valid': False, 'message': '无效的密钥长度'}
        
        # 验证使用目的
        valid_purposes = ['encryption', 'signing', 'authentication', 'key_exchange']
        if config['usage_purpose'] not in valid_purposes:
            return {'valid': False, 'message': '无效的使用目的'}
        
        return {'valid': True, 'message': '配置验证通过'}
    
    except Exception as e:
        return {'valid': False, 'message': f'配置验证失败: {str(e)}'}