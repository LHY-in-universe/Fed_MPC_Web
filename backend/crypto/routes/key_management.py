"""
密钥管理路由
处理密钥生成、存储、检索等功能
"""

from flask import Blueprint, request, jsonify, session
import logging
from datetime import datetime
import uuid
from shared.middleware.auth import auth_required, business_type_required
from shared.utils.helpers import success_response, error_response
from shared.utils.validators import validate_request_data

keys_bp = Blueprint('crypto_keys', __name__)
logger = logging.getLogger(__name__)

# 模拟密钥存储
USER_KEYS = {}

@keys_bp.route('', methods=['POST'])
@auth_required
@business_type_required(['crypto'])
def generate_key():
    """
    生成密钥对
    
    请求参数:
    - key_type: 密钥类型 (RSA, AES, ECC, DSA)
    - key_size: 密钥长度
    - name: 密钥名称
    - description: 密钥描述
    - usage_purpose: 使用目的
    """
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        # 验证请求数据
        required_fields = ['key_type', 'key_size', 'name']
        if not validate_request_data(data, required_fields):
            return error_response('缺少必填字段')
        
        key_type = data.get('key_type').upper()
        key_size = data.get('key_size')
        name = data.get('name').strip()
        description = data.get('description', '').strip()
        usage_purpose = data.get('usage_purpose', 'general')
        
        # 验证密钥类型
        valid_key_types = ['RSA', 'AES', 'ECC', 'ECDSA', 'DSA']
        if key_type not in valid_key_types:
            return error_response(f'无效的密钥类型，支持的类型: {", ".join(valid_key_types)}')
        
        # 生成密钥ID
        key_id = f"key_{uuid.uuid4().hex[:12]}"
        
        # 模拟密钥生成过程
        crypto_key = {
            'id': key_id,
            'name': name,
            'description': description,
            'key_type': key_type,
            'key_size': key_size,
            'usage_purpose': usage_purpose,
            'owner_id': user_id,
            'status': 'active',
            'business_type': 'crypto',
            'created_at': datetime.now().isoformat(),
            'expires_at': None,  # 可以设置过期时间
            'public_key': generate_mock_public_key(key_type, key_size),
            'private_key_hash': f"hash_{uuid.uuid4().hex[:16]}",  # 私钥哈希（不存储实际私钥）
            'fingerprint': f"fp:{uuid.uuid4().hex[:16].upper()}",
            'algorithm_parameters': get_algorithm_parameters(key_type, key_size),
            'usage_count': 0,
            'last_used': None
        }
        
        # 保存密钥
        if user_id not in USER_KEYS:
            USER_KEYS[user_id] = []
        USER_KEYS[user_id].append(crypto_key)
        
        # 记录密钥生成日志
        logger.info(f'密钥生成成功: {name} ({key_type}-{key_size}) 用户: {user_id}')
        
        # 返回响应（不包含私钥）
        response_key = {k: v for k, v in crypto_key.items() if k != 'private_key_hash'}
        
        return success_response(response_key, '密钥生成成功')
        
    except Exception as e:
        logger.error(f'密钥生成失败: {str(e)}')
        return error_response(f'密钥生成失败: {str(e)}', 500)

@keys_bp.route('', methods=['GET'])
@auth_required
@business_type_required(['crypto'])
def get_keys():
    """获取用户的密钥列表"""
    try:
        user_id = session.get('user_id')
        key_type = request.args.get('key_type')
        status = request.args.get('status')
        
        user_keys = USER_KEYS.get(user_id, [])
        
        # 应用过滤器
        filtered_keys = user_keys
        
        if key_type:
            filtered_keys = [k for k in filtered_keys if k['key_type'] == key_type.upper()]
        
        if status:
            filtered_keys = [k for k in filtered_keys if k['status'] == status]
        
        # 如果没有密钥，返回示例密钥
        if len(user_keys) == 0:
            example_keys = [
                {
                    'id': 'example_key_1',
                    'name': '主RSA密钥',
                    'description': '用于文档签名和加密的主要RSA密钥对',
                    'key_type': 'RSA',
                    'key_size': 2048,
                    'usage_purpose': 'signing',
                    'status': 'active',
                    'created_at': '2024-01-15T10:00:00',
                    'fingerprint': 'fp:A1B2C3D4E5F67890',
                    'usage_count': 25,
                    'last_used': '2024-01-22T14:30:00',
                    'business_type': 'crypto'
                },
                {
                    'id': 'example_key_2', 
                    'name': 'AES数据加密密钥',
                    'description': '用于敏感数据加密的AES密钥',
                    'key_type': 'AES',
                    'key_size': 256,
                    'usage_purpose': 'encryption',
                    'status': 'active',
                    'created_at': '2024-01-18T16:20:00',
                    'fingerprint': 'fp:B2C3D4E5F6789012',
                    'usage_count': 8,
                    'last_used': '2024-01-21T11:15:00',
                    'business_type': 'crypto'
                }
            ]
            filtered_keys = example_keys
        
        # 排序（按创建时间倒序）
        filtered_keys = sorted(filtered_keys, key=lambda x: x['created_at'], reverse=True)
        
        return success_response({
            'keys': filtered_keys,
            'total': len(filtered_keys)
        })
        
    except Exception as e:
        logger.error(f'获取密钥列表失败: {str(e)}')
        return error_response(f'获取密钥列表失败: {str(e)}', 500)

@keys_bp.route('/<key_id>', methods=['GET'])
@auth_required
@business_type_required(['crypto'])
def get_key_detail(key_id):
    """获取密钥详情"""
    try:
        user_id = session.get('user_id')
        
        # 查找密钥
        key = None
        user_keys = USER_KEYS.get(user_id, [])
        
        for k in user_keys:
            if k['id'] == key_id:
                key = k
                break
        
        # 处理示例密钥
        if not key and key_id.startswith('example_key_'):
            key = {
                'id': key_id,
                'name': '示例RSA密钥',
                'description': '这是一个示例RSA密钥，用于演示密钥管理功能',
                'key_type': 'RSA',
                'key_size': 2048,
                'usage_purpose': 'signing',
                'status': 'active',
                'created_at': '2024-01-15T10:00:00',
                'public_key': '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----',
                'fingerprint': 'fp:A1B2C3D4E5F67890',
                'algorithm_parameters': {
                    'padding': 'PKCS1v15',
                    'hash_algorithm': 'SHA256'
                },
                'usage_count': 25,
                'last_used': '2024-01-22T14:30:00',
                'business_type': 'crypto',
                'usage_history': [
                    {'operation': 'sign', 'timestamp': '2024-01-22T14:30:00', 'status': 'success'},
                    {'operation': 'verify', 'timestamp': '2024-01-22T14:25:00', 'status': 'success'},
                    {'operation': 'encrypt', 'timestamp': '2024-01-22T14:20:00', 'status': 'success'}
                ]
            }
        
        if not key:
            return error_response('密钥不存在', 404)
        
        return success_response(key)
        
    except Exception as e:
        logger.error(f'获取密钥详情失败: {str(e)}')
        return error_response(f'获取密钥详情失败: {str(e)}', 500)

@keys_bp.route('/<key_id>', methods=['PUT'])
@auth_required
@business_type_required(['crypto'])
def update_key(key_id):
    """更新密钥信息"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        # 查找密钥
        user_keys = USER_KEYS.get(user_id, [])
        key_index = -1
        
        for i, k in enumerate(user_keys):
            if k['id'] == key_id:
                key_index = i
                break
        
        if key_index == -1:
            return error_response('密钥不存在', 404)
        
        key = user_keys[key_index]
        
        # 更新允许的字段
        allowed_fields = ['name', 'description', 'status']
        for field in allowed_fields:
            if field in data:
                key[field] = data[field]
        
        key['updated_at'] = datetime.now().isoformat()
        
        # 保存更新
        USER_KEYS[user_id][key_index] = key
        
        logger.info(f'密钥更新成功: {key_id} 用户: {user_id}')
        
        return success_response(key, '密钥更新成功')
        
    except Exception as e:
        logger.error(f'密钥更新失败: {str(e)}')
        return error_response(f'密钥更新失败: {str(e)}', 500)

@keys_bp.route('/<key_id>', methods=['DELETE'])
@auth_required
@business_type_required(['crypto'])
def delete_key(key_id):
    """删除密钥"""
    try:
        user_id = session.get('user_id')
        
        # 查找密钥
        user_keys = USER_KEYS.get(user_id, [])
        key_index = -1
        
        for i, k in enumerate(user_keys):
            if k['id'] == key_id:
                key_index = i
                break
        
        if key_index == -1:
            return error_response('密钥不存在', 404)
        
        # 检查密钥是否可以删除
        key = user_keys[key_index]
        if key['status'] == 'active' and key.get('usage_count', 0) > 0:
            # 可以添加更严格的删除策略
            pass
        
        # 删除密钥
        del USER_KEYS[user_id][key_index]
        
        logger.info(f'密钥删除成功: {key_id} 用户: {user_id}')
        
        return success_response(None, '密钥删除成功')
        
    except Exception as e:
        logger.error(f'密钥删除失败: {str(e)}')
        return error_response(f'密钥删除失败: {str(e)}', 500)

@keys_bp.route('/<key_id>/export', methods=['POST'])
@auth_required
@business_type_required(['crypto'])
def export_key(key_id):
    """导出密钥（公钥）"""
    try:
        user_id = session.get('user_id')
        data = request.get_json() or {}
        export_format = data.get('format', 'PEM')
        
        # 查找密钥
        key = None
        user_keys = USER_KEYS.get(user_id, [])
        
        for k in user_keys:
            if k['id'] == key_id:
                key = k
                break
        
        if not key:
            return error_response('密钥不存在', 404)
        
        # 生成导出数据
        export_data = {
            'key_id': key_id,
            'key_type': key['key_type'],
            'key_size': key['key_size'],
            'format': export_format,
            'public_key': key.get('public_key', ''),
            'fingerprint': key['fingerprint'],
            'exported_at': datetime.now().isoformat(),
            'exported_by': user_id
        }
        
        logger.info(f'密钥导出成功: {key_id} 用户: {user_id}')
        
        return success_response(export_data, '密钥导出成功')
        
    except Exception as e:
        logger.error(f'密钥导出失败: {str(e)}')
        return error_response(f'密钥导出失败: {str(e)}', 500)

@keys_bp.route('/import', methods=['POST'])
@auth_required
@business_type_required(['crypto'])
def import_key():
    """导入密钥"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        # 验证请求数据
        required_fields = ['name', 'key_data', 'key_type']
        if not validate_request_data(data, required_fields):
            return error_response('缺少必填字段')
        
        name = data.get('name').strip()
        key_data = data.get('key_data')
        key_type = data.get('key_type').upper()
        description = data.get('description', '').strip()
        
        # 验证密钥格式
        if not key_data or not isinstance(key_data, str):
            return error_response('无效的密钥数据')
        
        # 生成密钥ID
        key_id = f"imported_key_{uuid.uuid4().hex[:12]}"
        
        # 创建导入的密钥记录
        imported_key = {
            'id': key_id,
            'name': name,
            'description': description,
            'key_type': key_type,
            'key_size': extract_key_size_from_data(key_data),  # 从密钥数据中提取
            'usage_purpose': 'general',
            'owner_id': user_id,
            'status': 'active',
            'business_type': 'crypto',
            'created_at': datetime.now().isoformat(),
            'imported_at': datetime.now().isoformat(),
            'public_key': key_data if 'PUBLIC KEY' in key_data else None,
            'fingerprint': f"fp:{uuid.uuid4().hex[:16].upper()}",
            'usage_count': 0,
            'last_used': None
        }
        
        # 保存密钥
        if user_id not in USER_KEYS:
            USER_KEYS[user_id] = []
        USER_KEYS[user_id].append(imported_key)
        
        logger.info(f'密钥导入成功: {name} 用户: {user_id}')
        
        return success_response(imported_key, '密钥导入成功')
        
    except Exception as e:
        logger.error(f'密钥导入失败: {str(e)}')
        return error_response(f'密钥导入失败: {str(e)}', 500)

def generate_mock_public_key(key_type, key_size):
    """生成模拟公钥"""
    if key_type == 'RSA':
        return f"-----BEGIN RSA PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA{uuid.uuid4().hex[:64]}...\n-----END RSA PUBLIC KEY-----"
    elif key_type == 'ECC':
        return f"-----BEGIN EC PUBLIC KEY-----\nMHYwEAYHKoZIzj0CAQYFK4EEACIDYgAE{uuid.uuid4().hex[:48]}...\n-----END EC PUBLIC KEY-----"
    elif key_type == 'AES':
        return "AES密钥 (对称密钥，无公钥)"
    else:
        return f"-----BEGIN {key_type} PUBLIC KEY-----\n{uuid.uuid4().hex[:64]}...\n-----END {key_type} PUBLIC KEY-----"

def get_algorithm_parameters(key_type, key_size):
    """获取算法参数"""
    if key_type == 'RSA':
        return {
            'padding': 'OAEP',
            'hash_algorithm': 'SHA256',
            'mgf': 'MGF1'
        }
    elif key_type == 'ECC':
        return {
            'curve': 'secp256r1' if key_size == 256 else 'secp384r1',
            'point_format': 'uncompressed'
        }
    elif key_type == 'AES':
        return {
            'mode': 'GCM',
            'key_derivation': 'PBKDF2',
            'iterations': 100000
        }
    else:
        return {}

def extract_key_size_from_data(key_data):
    """从密钥数据中提取密钥长度"""
    # 这里应该实际解析密钥数据，现在返回默认值
    if 'RSA' in key_data:
        return 2048
    elif 'EC' in key_data or 'ECC' in key_data:
        return 256
    else:
        return 256