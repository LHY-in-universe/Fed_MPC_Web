"""
加密解密路由
处理数据加密、解密和数字签名功能
"""

from flask import Blueprint, request, jsonify, session
import logging
from datetime import datetime
import uuid
import base64
from shared.middleware.auth import auth_required, business_type_required
from shared.utils.helpers import success_response, error_response
from shared.utils.validators import validate_request_data
from models.user import User

encryption_bp = Blueprint('crypto_encryption', __name__)
logger = logging.getLogger(__name__)

# 模拟加密操作记录
USER_OPERATIONS = {}

@encryption_bp.route('/encrypt', methods=['POST'])
@auth_required
@business_type_required(['crypto'])
def encrypt_data():
    """
    数据加密
    
    请求参数:
    - data: 待加密数据
    - key_id: 密钥ID
    - algorithm: 加密算法 (可选)
    - encoding: 输出编码格式 (base64/hex)
    """
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        current_user = User.query.get(user_id)
        
        # 验证请求数据
        required_fields = ['data', 'key_id']
        if not validate_request_data(data, required_fields):
            return error_response('缺少必填字段')
        
        plaintext = data.get('data')
        key_id = data.get('key_id')
        algorithm = data.get('algorithm', 'auto')
        encoding = data.get('encoding', 'base64')
        
        if not plaintext:
            return error_response('待加密数据不能为空')
        
        # 模拟加密过程
        operation_id = f"enc_{uuid.uuid4().hex[:12]}"
        
        # 生成模拟加密结果
        encrypted_data = simulate_encryption(plaintext, key_id, algorithm)
        
        # 记录加密操作
        operation_record = {
            'id': operation_id,
            'operation_type': 'encrypt',
            'key_id': key_id,
            'algorithm': algorithm,
            'data_size': len(plaintext),
            'owner_id': user_id,
            'status': 'success',
            'business_type': 'crypto',
            'created_at': datetime.now().isoformat(),
            'metadata': {
                'encoding': encoding,
                'plaintext_hash': f"hash_{uuid.uuid4().hex[:16]}",
                'encrypted_size': len(encrypted_data)
            }
        }
        
        # 保存操作记录
        if user_id not in USER_OPERATIONS:
            USER_OPERATIONS[user_id] = []
        USER_OPERATIONS[user_id].append(operation_record)
        
        logger.info(f'数据加密成功: 密钥{key_id} 用户{user_id}')
        
        return success_response({
            'operation_id': operation_id,
            'encrypted_data': encrypted_data,
            'algorithm': algorithm,
            'encoding': encoding,
            'key_id': key_id,
            'data_size': len(plaintext),
            'encrypted_at': datetime.now().isoformat()
        }, '数据加密成功')
        
    except Exception as e:
        logger.error(f'数据加密失败: {str(e)}')
        return error_response(f'数据加密失败: {str(e)}', 500)

@encryption_bp.route('/decrypt', methods=['POST'])
@auth_required
@business_type_required(['crypto'])
def decrypt_data():
    """
    数据解密
    
    请求参数:
    - encrypted_data: 加密数据
    - key_id: 密钥ID
    - algorithm: 解密算法 (可选)
    - encoding: 输入编码格式 (base64/hex)
    """
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        current_user = User.query.get(user_id)
        
        # 验证请求数据
        required_fields = ['encrypted_data', 'key_id']
        if not validate_request_data(data, required_fields):
            return error_response('缺少必填字段')
        
        encrypted_data = data.get('encrypted_data')
        key_id = data.get('key_id')
        algorithm = data.get('algorithm', 'auto')
        encoding = data.get('encoding', 'base64')
        
        if not encrypted_data:
            return error_response('加密数据不能为空')
        
        # 模拟解密过程
        operation_id = f"dec_{uuid.uuid4().hex[:12]}"
        
        # 生成模拟解密结果
        decrypted_data = simulate_decryption(encrypted_data, key_id, algorithm)
        
        # 记录解密操作
        operation_record = {
            'id': operation_id,
            'operation_type': 'decrypt',
            'key_id': key_id,
            'algorithm': algorithm,
            'data_size': len(encrypted_data),
            'owner_id': user_id,
            'status': 'success',
            'business_type': 'crypto',
            'created_at': datetime.now().isoformat(),
            'metadata': {
                'encoding': encoding,
                'encrypted_hash': f"hash_{uuid.uuid4().hex[:16]}",
                'decrypted_size': len(decrypted_data)
            }
        }
        
        # 保存操作记录
        if user_id not in USER_OPERATIONS:
            USER_OPERATIONS[user_id] = []
        USER_OPERATIONS[user_id].append(operation_record)
        
        logger.info(f'数据解密成功: 密钥{key_id} 用户{user_id}')
        
        return success_response({
            'operation_id': operation_id,
            'decrypted_data': decrypted_data,
            'algorithm': algorithm,
            'encoding': encoding,
            'key_id': key_id,
            'data_size': len(encrypted_data),
            'decrypted_at': datetime.now().isoformat()
        }, '数据解密成功')
        
    except Exception as e:
        logger.error(f'数据解密失败: {str(e)}')
        return error_response(f'数据解密失败: {str(e)}', 500)

@encryption_bp.route('/sign', methods=['POST'])
@auth_required
@business_type_required(['crypto'])
def sign_data():
    """
    数字签名
    
    请求参数:
    - data: 待签名数据
    - key_id: 签名密钥ID
    - hash_algorithm: 哈希算法 (SHA256/SHA512)
    - encoding: 输出编码格式
    """
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        current_user = User.query.get(user_id)
        
        # 验证请求数据
        required_fields = ['data', 'key_id']
        if not validate_request_data(data, required_fields):
            return error_response('缺少必填字段')
        
        message = data.get('data')
        key_id = data.get('key_id')
        hash_algorithm = data.get('hash_algorithm', 'SHA256')
        encoding = data.get('encoding', 'base64')
        
        if not message:
            return error_response('待签名数据不能为空')
        
        # 模拟签名过程
        operation_id = f"sign_{uuid.uuid4().hex[:12]}"
        
        # 生成模拟签名
        signature = simulate_signing(message, key_id, hash_algorithm)
        
        # 记录签名操作
        operation_record = {
            'id': operation_id,
            'operation_type': 'sign',
            'key_id': key_id,
            'algorithm': f"RSA-{hash_algorithm}",  # 假设使用RSA签名
            'data_size': len(message),
            'owner_id': user_id,
            'status': 'success',
            'business_type': 'crypto',
            'created_at': datetime.now().isoformat(),
            'metadata': {
                'hash_algorithm': hash_algorithm,
                'encoding': encoding,
                'message_hash': f"hash_{uuid.uuid4().hex[:16]}",
                'signature_size': len(signature)
            }
        }
        
        # 保存操作记录
        if user_id not in USER_OPERATIONS:
            USER_OPERATIONS[user_id] = []
        USER_OPERATIONS[user_id].append(operation_record)
        
        logger.info(f'数据签名成功: 密钥{key_id} 用户{user_id}')
        
        return success_response({
            'operation_id': operation_id,
            'signature': signature,
            'hash_algorithm': hash_algorithm,
            'encoding': encoding,
            'key_id': key_id,
            'data_size': len(message),
            'signed_at': datetime.now().isoformat()
        }, '数据签名成功')
        
    except Exception as e:
        logger.error(f'数据签名失败: {str(e)}')
        return error_response(f'数据签名失败: {str(e)}', 500)

@encryption_bp.route('/verify', methods=['POST'])
@auth_required
@business_type_required(['crypto'])
def verify_signature():
    """
    验证数字签名
    
    请求参数:
    - data: 原始数据
    - signature: 数字签名
    - key_id: 验证密钥ID (公钥)
    - hash_algorithm: 哈希算法
    - encoding: 签名编码格式
    """
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        current_user = User.query.get(user_id)
        
        # 验证请求数据
        required_fields = ['data', 'signature', 'key_id']
        if not validate_request_data(data, required_fields):
            return error_response('缺少必填字段')
        
        message = data.get('data')
        signature = data.get('signature')
        key_id = data.get('key_id')
        hash_algorithm = data.get('hash_algorithm', 'SHA256')
        encoding = data.get('encoding', 'base64')
        
        if not message or not signature:
            return error_response('数据和签名不能为空')
        
        # 模拟签名验证过程
        operation_id = f"verify_{uuid.uuid4().hex[:12]}"
        
        # 生成模拟验证结果
        is_valid = simulate_signature_verification(message, signature, key_id, hash_algorithm)
        
        # 记录验证操作
        operation_record = {
            'id': operation_id,
            'operation_type': 'verify',
            'key_id': key_id,
            'algorithm': f"RSA-{hash_algorithm}",
            'data_size': len(message),
            'owner_id': user_id,
            'status': 'success',
            'business_type': 'crypto',
            'created_at': datetime.now().isoformat(),
            'metadata': {
                'hash_algorithm': hash_algorithm,
                'encoding': encoding,
                'verification_result': is_valid,
                'signature_size': len(signature)
            }
        }
        
        # 保存操作记录
        if user_id not in USER_OPERATIONS:
            USER_OPERATIONS[user_id] = []
        USER_OPERATIONS[user_id].append(operation_record)
        
        result_message = '签名验证成功' if is_valid else '签名验证失败'
        logger.info(f'签名验证: {result_message} 密钥{key_id} 用户{user_id}')
        
        return success_response({
            'operation_id': operation_id,
            'is_valid': is_valid,
            'hash_algorithm': hash_algorithm,
            'encoding': encoding,
            'key_id': key_id,
            'data_size': len(message),
            'verified_at': datetime.now().isoformat()
        }, result_message)
        
    except Exception as e:
        logger.error(f'签名验证失败: {str(e)}')
        return error_response(f'签名验证失败: {str(e)}', 500)

@encryption_bp.route('/operations', methods=['GET'])
@auth_required
@business_type_required(['crypto'])
def get_operations():
    """获取加密操作记录"""
    try:
        user_id = session.get('user_id')
        operation_type = request.args.get('operation_type')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        user_operations = USER_OPERATIONS.get(user_id, [])
        
        # 应用过滤器
        filtered_operations = user_operations
        
        if operation_type:
            filtered_operations = [op for op in filtered_operations if op['operation_type'] == operation_type]
        
        # 如果没有操作记录，返回示例记录
        if len(user_operations) == 0:
            example_operations = [
                {
                    'id': 'example_op_1',
                    'operation_type': 'encrypt',
                    'key_id': 'example_key_1',
                    'algorithm': 'RSA-OAEP',
                    'data_size': 256,
                    'status': 'success',
                    'created_at': '2024-01-22T10:30:00',
                    'metadata': {
                        'encoding': 'base64',
                        'encrypted_size': 344
                    }
                },
                {
                    'id': 'example_op_2',
                    'operation_type': 'sign',
                    'key_id': 'example_key_1',
                    'algorithm': 'RSA-SHA256',
                    'data_size': 128,
                    'status': 'success',
                    'created_at': '2024-01-22T14:15:00',
                    'metadata': {
                        'hash_algorithm': 'SHA256',
                        'signature_size': 256
                    }
                }
            ]
            filtered_operations = example_operations
        
        # 按时间倒序排列
        filtered_operations = sorted(filtered_operations, key=lambda x: x['created_at'], reverse=True)
        
        # 分页
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_operations = filtered_operations[start_idx:end_idx]
        
        return success_response({
            'operations': paginated_operations,
            'total': len(filtered_operations),
            'page': page,
            'per_page': per_page,
            'total_pages': (len(filtered_operations) + per_page - 1) // per_page
        })
        
    except Exception as e:
        logger.error(f'获取操作记录失败: {str(e)}')
        return error_response(f'获取操作记录失败: {str(e)}', 500)

@encryption_bp.route('/hash', methods=['POST'])
@auth_required
@business_type_required(['crypto'])
def hash_data():
    """
    数据哈希计算
    
    请求参数:
    - data: 待哈希数据
    - algorithm: 哈希算法 (SHA256/SHA512/MD5)
    - encoding: 输出编码格式
    """
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        # 验证请求数据
        required_fields = ['data']
        if not validate_request_data(data, required_fields):
            return error_response('缺少必填字段')
        
        message = data.get('data')
        algorithm = data.get('algorithm', 'SHA256')
        encoding = data.get('encoding', 'hex')
        
        if not message:
            return error_response('待哈希数据不能为空')
        
        # 模拟哈希计算
        operation_id = f"hash_{uuid.uuid4().hex[:12]}"
        hash_result = simulate_hashing(message, algorithm)
        
        # 记录哈希操作
        operation_record = {
            'id': operation_id,
            'operation_type': 'hash',
            'algorithm': algorithm,
            'data_size': len(message),
            'owner_id': user_id,
            'status': 'success',
            'business_type': 'crypto',
            'created_at': datetime.now().isoformat(),
            'metadata': {
                'encoding': encoding,
                'hash_length': len(hash_result)
            }
        }
        
        # 保存操作记录
        if user_id not in USER_OPERATIONS:
            USER_OPERATIONS[user_id] = []
        USER_OPERATIONS[user_id].append(operation_record)
        
        logger.info(f'数据哈希计算成功: {algorithm} 用户{user_id}')
        
        return success_response({
            'operation_id': operation_id,
            'hash': hash_result,
            'algorithm': algorithm,
            'encoding': encoding,
            'data_size': len(message),
            'computed_at': datetime.now().isoformat()
        }, '哈希计算成功')
        
    except Exception as e:
        logger.error(f'哈希计算失败: {str(e)}')
        return error_response(f'哈希计算失败: {str(e)}', 500)

def simulate_encryption(plaintext, key_id, algorithm):
    """模拟加密过程"""
    # 简单的base64编码作为模拟加密
    encrypted = base64.b64encode(plaintext.encode()).decode()
    return f"ENC:{algorithm}:{key_id}:{encrypted}"

def simulate_decryption(encrypted_data, key_id, algorithm):
    """模拟解密过程"""
    # 尝试解析加密数据格式
    if encrypted_data.startswith(f"ENC:{algorithm}:{key_id}:"):
        encoded_part = encrypted_data.split(':', 3)[-1]
        try:
            decrypted = base64.b64decode(encoded_part.encode()).decode()
            return decrypted
        except:
            pass
    
    # 返回模拟解密结果
    return "这是解密后的数据内容"

def simulate_signing(message, key_id, hash_algorithm):
    """模拟数字签名"""
    # 生成模拟签名
    signature_data = f"{message}:{key_id}:{hash_algorithm}:{uuid.uuid4().hex}"
    signature = base64.b64encode(signature_data.encode()).decode()
    return signature

def simulate_signature_verification(message, signature, key_id, hash_algorithm):
    """模拟签名验证"""
    # 简单的模拟验证逻辑
    try:
        decoded_sig = base64.b64decode(signature.encode()).decode()
        return f"{message}:{key_id}:{hash_algorithm}" in decoded_sig
    except:
        # 大部分情况下返回验证成功
        import random
        return random.random() > 0.1  # 90%概率验证成功

def simulate_hashing(message, algorithm):
    """模拟哈希计算"""
    import hashlib
    
    if algorithm == 'SHA256':
        return hashlib.sha256(message.encode()).hexdigest()
    elif algorithm == 'SHA512':
        return hashlib.sha512(message.encode()).hexdigest()
    elif algorithm == 'MD5':
        return hashlib.md5(message.encode()).hexdigest()
    else:
        return hashlib.sha256(message.encode()).hexdigest()