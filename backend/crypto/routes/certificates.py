"""
证书管理路由
处理数字证书的创建、管理和验证
"""

from flask import Blueprint, request, jsonify, session
import logging
from datetime import datetime, timedelta
import uuid
from shared.middleware.auth import auth_required, business_type_required
from shared.utils.helpers import success_response, error_response
from shared.utils.validators import validate_request_data, validate_certificate_type
from models.user import User

certificates_bp = Blueprint('crypto_certificates', __name__)
logger = logging.getLogger(__name__)

# 模拟证书存储
USER_CERTIFICATES = {}

@certificates_bp.route('', methods=['POST'])
@auth_required
@business_type_required(['crypto'])
def create_certificate():
    """
    创建数字证书
    
    请求参数:
    - name: 证书名称
    - subject: 证书主体信息
    - certificate_type: 证书类型
    - key_id: 关联的密钥ID
    - valid_days: 有效天数
    - extensions: 证书扩展
    """
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        current_user = User.query.get(user_id)
        
        # 验证请求数据
        required_fields = ['name', 'subject', 'certificate_type']
        if not validate_request_data(data, required_fields):
            return error_response('缺少必填字段')
        
        name = data.get('name').strip()
        subject = data.get('subject')
        cert_type = data.get('certificate_type')
        key_id = data.get('key_id')
        valid_days = data.get('valid_days', 365)
        extensions = data.get('extensions', {})
        
        # 验证证书类型
        if not validate_certificate_type(cert_type):
            return error_response('无效的证书类型')
        
        # 生成证书ID
        cert_id = f"cert_{uuid.uuid4().hex[:12]}"
        
        # 计算有效期
        created_at = datetime.now()
        expires_at = created_at + timedelta(days=valid_days)
        
        # 创建证书记录
        certificate = {
            'id': cert_id,
            'name': name,
            'subject': subject,
            'certificate_type': cert_type,
            'key_id': key_id,
            'owner_id': user_id,
            'status': 'active',
            'business_type': 'crypto',
            'created_at': created_at.isoformat(),
            'expires_at': expires_at.isoformat(),
            'serial_number': f"SN{uuid.uuid4().hex[:16].upper()}",
            'issuer': generate_issuer_info(subject, cert_type),
            'public_key': generate_mock_certificate_public_key(),
            'signature_algorithm': 'SHA256withRSA',
            'fingerprint': f"fp:{uuid.uuid4().hex[:32].upper()}",
            'extensions': extensions,
            'pem_data': generate_mock_pem_certificate(cert_id, subject),
            'usage_count': 0,
            'last_used': None
        }
        
        # 保存证书
        if user_id not in USER_CERTIFICATES:
            USER_CERTIFICATES[user_id] = []
        USER_CERTIFICATES[user_id].append(certificate)
        
        logger.info(f'证书创建成功: {name} ({cert_type}) 用户: {user_id}')
        
        return success_response(certificate, '证书创建成功')
        
    except Exception as e:
        logger.error(f'证书创建失败: {str(e)}')
        return error_response(f'证书创建失败: {str(e)}', 500)

@certificates_bp.route('', methods=['GET'])
@auth_required
@business_type_required(['crypto'])
def get_certificates():
    """获取用户的证书列表"""
    try:
        user_id = session.get('user_id')
        cert_type = request.args.get('certificate_type')
        status = request.args.get('status')
        
        user_certificates = USER_CERTIFICATES.get(user_id, [])
        
        # 应用过滤器
        filtered_certificates = user_certificates
        
        if cert_type:
            filtered_certificates = [c for c in filtered_certificates if c['certificate_type'] == cert_type]
        
        if status:
            filtered_certificates = [c for c in filtered_certificates if c['status'] == status]
        
        # 更新证书状态（检查过期）
        now = datetime.now()
        for cert in filtered_certificates:
            expires_at = datetime.fromisoformat(cert['expires_at'])
            if now > expires_at:
                cert['status'] = 'expired'
        
        # 如果没有证书，返回示例证书
        if len(user_certificates) == 0:
            example_certificates = [
                {
                    'id': 'example_cert_1',
                    'name': 'SSL服务器证书',
                    'subject': {
                        'CN': 'example.com',
                        'O': '示例组织',
                        'C': 'CN'
                    },
                    'certificate_type': 'ca_signed',
                    'status': 'active',
                    'created_at': '2024-01-15T10:00:00',
                    'expires_at': '2025-01-15T10:00:00',
                    'serial_number': 'SNA1B2C3D4E5F67890',
                    'issuer': 'CN=CA Root Certificate',
                    'signature_algorithm': 'SHA256withRSA',
                    'fingerprint': 'fp:A1B2C3D4E5F67890A1B2C3D4E5F67890',
                    'usage_count': 15,
                    'last_used': '2024-01-22T14:30:00',
                    'business_type': 'crypto'
                },
                {
                    'id': 'example_cert_2',
                    'name': '代码签名证书',
                    'subject': {
                        'CN': 'Developer Name',
                        'O': '开发公司',
                        'C': 'CN'
                    },
                    'certificate_type': 'self_signed',
                    'status': 'active',
                    'created_at': '2024-01-18T16:20:00',
                    'expires_at': '2025-01-18T16:20:00',
                    'serial_number': 'SNB2C3D4E5F6789012',
                    'issuer': 'CN=Self Signed',
                    'signature_algorithm': 'SHA256withRSA',
                    'fingerprint': 'fp:B2C3D4E5F6789012B2C3D4E5F6789012',
                    'usage_count': 3,
                    'last_used': '2024-01-21T11:15:00',
                    'business_type': 'crypto'
                }
            ]
            filtered_certificates = example_certificates
        
        # 按创建时间倒序排列
        filtered_certificates = sorted(filtered_certificates, key=lambda x: x['created_at'], reverse=True)
        
        return success_response({
            'certificates': filtered_certificates,
            'total': len(filtered_certificates)
        })
        
    except Exception as e:
        logger.error(f'获取证书列表失败: {str(e)}')
        return error_response(f'获取证书列表失败: {str(e)}', 500)

@certificates_bp.route('/<cert_id>', methods=['GET'])
@auth_required
@business_type_required(['crypto'])
def get_certificate_detail(cert_id):
    """获取证书详情"""
    try:
        user_id = session.get('user_id')
        
        # 查找证书
        certificate = None
        user_certificates = USER_CERTIFICATES.get(user_id, [])
        
        for cert in user_certificates:
            if cert['id'] == cert_id:
                certificate = cert
                break
        
        # 处理示例证书
        if not certificate and cert_id.startswith('example_cert_'):
            certificate = {
                'id': cert_id,
                'name': '示例SSL证书',
                'subject': {
                    'CN': 'example.com',
                    'O': '示例组织',
                    'OU': 'IT部门',
                    'L': '北京',
                    'ST': '北京',
                    'C': 'CN'
                },
                'certificate_type': 'ca_signed',
                'status': 'active',
                'created_at': '2024-01-15T10:00:00',
                'expires_at': '2025-01-15T10:00:00',
                'serial_number': 'SNA1B2C3D4E5F67890',
                'issuer': 'CN=Trusted CA, O=Certificate Authority, C=US',
                'signature_algorithm': 'SHA256withRSA',
                'fingerprint': 'fp:A1B2C3D4E5F67890A1B2C3D4E5F67890',
                'public_key': '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----',
                'extensions': {
                    'subjectAltName': ['DNS:example.com', 'DNS:www.example.com'],
                    'keyUsage': ['digitalSignature', 'keyEncipherment'],
                    'extendedKeyUsage': ['serverAuth'],
                    'basicConstraints': 'CA:FALSE'
                },
                'pem_data': '-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKoK/heBjcOuMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV...\n-----END CERTIFICATE-----',
                'usage_count': 15,
                'last_used': '2024-01-22T14:30:00',
                'business_type': 'crypto',
                'validation_history': [
                    {'validated_at': '2024-01-22T14:30:00', 'status': 'valid', 'validator': 'system'},
                    {'validated_at': '2024-01-20T10:15:00', 'status': 'valid', 'validator': 'manual'},
                ]
            }
        
        if not certificate:
            return error_response('证书不存在', 404)
        
        # 更新证书状态
        now = datetime.now()
        expires_at = datetime.fromisoformat(certificate['expires_at'])
        if now > expires_at:
            certificate['status'] = 'expired'
        
        return success_response(certificate)
        
    except Exception as e:
        logger.error(f'获取证书详情失败: {str(e)}')
        return error_response(f'获取证书详情失败: {str(e)}', 500)

@certificates_bp.route('/<cert_id>', methods=['PUT'])
@auth_required
@business_type_required(['crypto'])
def update_certificate(cert_id):
    """更新证书信息"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        # 查找证书
        user_certificates = USER_CERTIFICATES.get(user_id, [])
        cert_index = -1
        
        for i, cert in enumerate(user_certificates):
            if cert['id'] == cert_id:
                cert_index = i
                break
        
        if cert_index == -1:
            return error_response('证书不存在', 404)
        
        certificate = user_certificates[cert_index]
        
        # 更新允许的字段
        allowed_fields = ['name', 'status', 'extensions']
        for field in allowed_fields:
            if field in data:
                certificate[field] = data[field]
        
        certificate['updated_at'] = datetime.now().isoformat()
        
        # 保存更新
        USER_CERTIFICATES[user_id][cert_index] = certificate
        
        logger.info(f'证书更新成功: {cert_id} 用户: {user_id}')
        
        return success_response(certificate, '证书更新成功')
        
    except Exception as e:
        logger.error(f'证书更新失败: {str(e)}')
        return error_response(f'证书更新失败: {str(e)}', 500)

@certificates_bp.route('/<cert_id>/revoke', methods=['POST'])
@auth_required
@business_type_required(['crypto'])
def revoke_certificate(cert_id):
    """撤销证书"""
    try:
        user_id = session.get('user_id')
        data = request.get_json() or {}
        reason = data.get('reason', 'unspecified')
        
        # 查找证书
        user_certificates = USER_CERTIFICATES.get(user_id, [])
        cert_index = -1
        
        for i, cert in enumerate(user_certificates):
            if cert['id'] == cert_id:
                cert_index = i
                break
        
        if cert_index == -1:
            return error_response('证书不存在', 404)
        
        certificate = user_certificates[cert_index]
        
        if certificate['status'] == 'revoked':
            return error_response('证书已被撤销')
        
        # 撤销证书
        certificate['status'] = 'revoked'
        certificate['revoked_at'] = datetime.now().isoformat()
        certificate['revocation_reason'] = reason
        certificate['updated_at'] = datetime.now().isoformat()
        
        # 保存更新
        USER_CERTIFICATES[user_id][cert_index] = certificate
        
        logger.info(f'证书撤销成功: {cert_id} 原因: {reason} 用户: {user_id}')
        
        return success_response({
            'certificate_id': cert_id,
            'status': 'revoked',
            'revoked_at': certificate['revoked_at'],
            'reason': reason
        }, '证书撤销成功')
        
    except Exception as e:
        logger.error(f'证书撤销失败: {str(e)}')
        return error_response(f'证书撤销失败: {str(e)}', 500)

@certificates_bp.route('/<cert_id>/validate', methods=['POST'])
@auth_required
@business_type_required(['crypto'])
def validate_certificate(cert_id):
    """验证证书有效性"""
    try:
        user_id = session.get('user_id')
        
        # 查找证书
        certificate = None
        user_certificates = USER_CERTIFICATES.get(user_id, [])
        
        for cert in user_certificates:
            if cert['id'] == cert_id:
                certificate = cert
                break
        
        if not certificate:
            return error_response('证书不存在', 404)
        
        # 执行证书验证
        validation_result = perform_certificate_validation(certificate)
        
        # 记录验证历史
        if 'validation_history' not in certificate:
            certificate['validation_history'] = []
        
        certificate['validation_history'].append({
            'validated_at': datetime.now().isoformat(),
            'status': validation_result['status'],
            'validator': 'user',
            'details': validation_result['details']
        })
        
        logger.info(f'证书验证: {validation_result["status"]} {cert_id} 用户: {user_id}')
        
        return success_response(validation_result, '证书验证完成')
        
    except Exception as e:
        logger.error(f'证书验证失败: {str(e)}')
        return error_response(f'证书验证失败: {str(e)}', 500)

@certificates_bp.route('/<cert_id>/export', methods=['POST'])
@auth_required
@business_type_required(['crypto'])
def export_certificate(cert_id):
    """导出证书"""
    try:
        user_id = session.get('user_id')
        data = request.get_json() or {}
        export_format = data.get('format', 'PEM')
        include_chain = data.get('include_chain', False)
        
        # 查找证书
        certificate = None
        user_certificates = USER_CERTIFICATES.get(user_id, [])
        
        for cert in user_certificates:
            if cert['id'] == cert_id:
                certificate = cert
                break
        
        if not certificate:
            return error_response('证书不存在', 404)
        
        # 生成导出数据
        export_data = {
            'certificate_id': cert_id,
            'format': export_format,
            'certificate_data': certificate.get('pem_data', ''),
            'subject': certificate['subject'],
            'issuer': certificate['issuer'],
            'serial_number': certificate['serial_number'],
            'exported_at': datetime.now().isoformat(),
            'exported_by': user_id
        }
        
        if include_chain:
            export_data['certificate_chain'] = [
                certificate.get('pem_data', ''),
                # 这里可以包含证书链中的其他证书
            ]
        
        logger.info(f'证书导出成功: {cert_id} 格式: {export_format} 用户: {user_id}')
        
        return success_response(export_data, '证书导出成功')
        
    except Exception as e:
        logger.error(f'证书导出失败: {str(e)}')
        return error_response(f'证书导出失败: {str(e)}', 500)

@certificates_bp.route('/templates', methods=['GET'])
@auth_required
@business_type_required(['crypto'])
def get_certificate_templates():
    """获取证书模板列表"""
    try:
        templates = [
            {
                'id': 'ssl_server_template',
                'name': 'SSL服务器证书',
                'description': '用于HTTPS服务器的SSL证书模板',
                'certificate_type': 'ca_signed',
                'subject_template': {
                    'CN': '{{domain_name}}',
                    'O': '{{organization}}',
                    'C': '{{country}}'
                },
                'extensions': {
                    'keyUsage': ['digitalSignature', 'keyEncipherment'],
                    'extendedKeyUsage': ['serverAuth'],
                    'basicConstraints': 'CA:FALSE'
                },
                'valid_days': 365
            },
            {
                'id': 'code_signing_template',
                'name': '代码签名证书',
                'description': '用于软件代码签名的证书模板',
                'certificate_type': 'ca_signed',
                'subject_template': {
                    'CN': '{{developer_name}}',
                    'O': '{{company_name}}',
                    'C': '{{country}}'
                },
                'extensions': {
                    'keyUsage': ['digitalSignature'],
                    'extendedKeyUsage': ['codeSigning'],
                    'basicConstraints': 'CA:FALSE'
                },
                'valid_days': 1095
            },
            {
                'id': 'client_auth_template',
                'name': '客户端认证证书',
                'description': '用于客户端身份认证的证书模板',
                'certificate_type': 'ca_signed',
                'subject_template': {
                    'CN': '{{user_name}}',
                    'O': '{{organization}}',
                    'C': '{{country}}'
                },
                'extensions': {
                    'keyUsage': ['digitalSignature', 'keyAgreement'],
                    'extendedKeyUsage': ['clientAuth'],
                    'basicConstraints': 'CA:FALSE'
                },
                'valid_days': 730
            }
        ]
        
        cert_type = request.args.get('certificate_type')
        if cert_type:
            templates = [t for t in templates if t['certificate_type'] == cert_type]
        
        return success_response({
            'templates': templates,
            'total': len(templates)
        })
        
    except Exception as e:
        logger.error(f'获取证书模板失败: {str(e)}')
        return error_response(f'获取证书模板失败: {str(e)}', 500)

def generate_issuer_info(subject, cert_type):
    """生成颁发者信息"""
    if cert_type == 'self_signed':
        return f"CN={subject.get('CN', 'Self Signed')}"
    elif cert_type == 'ca_signed':
        return "CN=Trusted Root CA, O=Certificate Authority, C=US"
    else:
        return "CN=Intermediate CA, O=Certificate Authority, C=US"

def generate_mock_certificate_public_key():
    """生成模拟证书公钥"""
    return "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA" + uuid.uuid4().hex[:64] + "...\n-----END PUBLIC KEY-----"

def generate_mock_pem_certificate(cert_id, subject):
    """生成模拟PEM格式证书"""
    return f"-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJA{uuid.uuid4().hex[:16]}MA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV\n{uuid.uuid4().hex[:64]}\n-----END CERTIFICATE-----"

def perform_certificate_validation(certificate):
    """执行证书验证"""
    now = datetime.now()
    expires_at = datetime.fromisoformat(certificate['expires_at'])
    
    validation_details = {
        'signature_valid': True,
        'not_expired': now < expires_at,
        'not_revoked': certificate['status'] != 'revoked',
        'chain_valid': True,
        'usage_valid': True
    }
    
    is_valid = all(validation_details.values())
    
    return {
        'status': 'valid' if is_valid else 'invalid',
        'is_valid': is_valid,
        'details': validation_details,
        'validated_at': now.isoformat(),
        'expires_at': certificate['expires_at'],
        'days_until_expiry': (expires_at - now).days if expires_at > now else 0
    }