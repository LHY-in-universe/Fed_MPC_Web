"""
数字证书模型
管理X.509数字证书的创建、验证和生命周期
"""

from models.base import BaseModel, db
from datetime import datetime, timedelta
import enum
import json
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import ipaddress

class CertificateType(enum.Enum):
    """证书类型枚举"""
    ROOT_CA = 'root_ca'           # 根证书颁发机构
    INTERMEDIATE_CA = 'intermediate_ca'  # 中间证书颁发机构
    END_ENTITY = 'end_entity'     # 终端实体证书
    CODE_SIGNING = 'code_signing' # 代码签名证书

class CertificateStatus(enum.Enum):
    """证书状态枚举"""
    VALID = 'valid'               # 有效
    EXPIRED = 'expired'           # 过期
    REVOKED = 'revoked'           # 吊销
    SUSPENDED = 'suspended'       # 暂停

class Certificate(BaseModel):
    """数字证书模型"""
    
    __tablename__ = 'crypto_certificates'
    
    # 基本信息
    cert_id = db.Column(db.String(64), unique=True, nullable=False, index=True)  # 证书ID
    serial_number = db.Column(db.String(40), unique=True, nullable=False)        # 序列号
    subject_dn = db.Column(db.String(500), nullable=False)                       # 主题DN
    issuer_dn = db.Column(db.String(500), nullable=False)                        # 颁发者DN
    
    # 证书属性
    cert_type = db.Column(db.Enum(CertificateType), nullable=False)              # 证书类型
    status = db.Column(db.Enum(CertificateStatus), default=CertificateStatus.VALID)  # 状态
    
    # 关联信息
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)   # 所属用户
    key_pair_id = db.Column(db.Integer, db.ForeignKey('crypto_key_pairs.id'))    # 关联密钥对
    parent_cert_id = db.Column(db.Integer, db.ForeignKey('crypto_certificates.id'))  # 父证书
    
    # 证书数据
    certificate_pem = db.Column(db.Text, nullable=False)                         # 证书PEM
    
    # 时间信息
    valid_from = db.Column(db.DateTime, nullable=False)                          # 生效时间
    valid_until = db.Column(db.DateTime, nullable=False)                         # 失效时间
    
    # 扩展信息
    key_usage = db.Column(db.String(200))                                        # 密钥用法
    extended_key_usage = db.Column(db.String(200))                               # 扩展密钥用法
    subject_alt_names = db.Column(db.Text)                                       # 主题备用名称
    
    # 吊销信息
    revocation_reason = db.Column(db.String(100))                                # 吊销原因
    revoked_at = db.Column(db.DateTime)                                          # 吊销时间
    
    # 元数据
    fingerprint_sha1 = db.Column(db.String(40))                                  # SHA1指纹
    fingerprint_sha256 = db.Column(db.String(64))                                # SHA256指纹
    extensions = db.Column(db.Text)                                              # 其他扩展信息
    
    # 关联关系
    children = db.relationship('Certificate', backref=db.backref('parent', remote_side='Certificate.id'))
    
    def __init__(self, user_id, subject_dn, cert_type='end_entity', **kwargs):
        self.user_id = user_id
        self.subject_dn = subject_dn
        self.cert_type = cert_type if isinstance(cert_type, CertificateType) else CertificateType(cert_type)
        
        # 设置其他属性
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def generate_certificate(self, issuer_cert=None, issuer_key=None, 
                           validity_days=365, **cert_params):
        """生成证书"""
        from .key_pair import KeyPair
        
        # 获取密钥对
        if not self.key_pair_id:
            raise ValueError("必须关联密钥对才能生成证书")
        
        key_pair = KeyPair.get_by_id(self.key_pair_id)
        if not key_pair:
            raise ValueError("关联的密钥对不存在")
        
        # 获取私钥（需要密码）
        passphrase = cert_params.get('passphrase', '')
        try:
            private_key = key_pair.get_private_key(passphrase)
            public_key = key_pair.get_public_key()
        except Exception as e:
            raise ValueError(f"无法获取密钥: {str(e)}")
        
        # 设置证书有效期
        self.valid_from = datetime.utcnow()
        self.valid_until = self.valid_from + timedelta(days=validity_days)
        
        # 创建证书构建器
        builder = x509.CertificateBuilder()
        
        # 设置序列号
        import secrets
        self.serial_number = hex(secrets.randbits(128))[2:].upper()
        builder = builder.serial_number(int(self.serial_number, 16))
        
        # 设置主题
        subject = self._parse_dn(self.subject_dn)
        builder = builder.subject_name(subject)
        
        # 设置颁发者
        if issuer_cert:
            issuer = issuer_cert.get_certificate().subject
            self.issuer_dn = self._format_dn(issuer)
            self.parent_cert_id = issuer_cert.id
        else:
            # 自签名证书
            issuer = subject
            self.issuer_dn = self.subject_dn
        
        builder = builder.issuer_name(issuer)
        
        # 设置公钥
        builder = builder.public_key(public_key)
        
        # 设置有效期
        builder = builder.not_valid_before(self.valid_from)
        builder = builder.not_valid_after(self.valid_until)
        
        # 添加扩展
        builder = self._add_extensions(builder, cert_params)
        
        # 签名
        signing_key = issuer_key if issuer_key else private_key
        certificate = builder.sign(signing_key, hashes.SHA256(), default_backend())
        
        # 存储证书PEM
        self.certificate_pem = certificate.public_bytes(
            serialization.Encoding.PEM
        ).decode('utf-8')
        
        # 生成指纹
        self._generate_fingerprints(certificate)
        
        # 生成证书ID
        self.cert_id = f"cert_{self.serial_number[:16]}"
        
        return True
    
    def _parse_dn(self, dn_string):
        """解析DN字符串"""
        attributes = []
        
        # 简单的DN解析，支持常见属性
        dn_mapping = {
            'CN': NameOID.COMMON_NAME,
            'O': NameOID.ORGANIZATION_NAME,
            'OU': NameOID.ORGANIZATIONAL_UNIT_NAME,
            'C': NameOID.COUNTRY_NAME,
            'ST': NameOID.STATE_OR_PROVINCE_NAME,
            'L': NameOID.LOCALITY_NAME,
            'EMAIL': NameOID.EMAIL_ADDRESS
        }
        
        for part in dn_string.split(','):
            part = part.strip()
            if '=' in part:
                key, value = part.split('=', 1)
                key = key.strip().upper()
                value = value.strip()
                
                if key in dn_mapping:
                    attributes.append(x509.NameAttribute(dn_mapping[key], value))
        
        return x509.Name(attributes)
    
    def _format_dn(self, name):
        """格式化DN"""
        parts = []
        for attribute in name:
            oid_name = {
                NameOID.COMMON_NAME: 'CN',
                NameOID.ORGANIZATION_NAME: 'O',
                NameOID.ORGANIZATIONAL_UNIT_NAME: 'OU',
                NameOID.COUNTRY_NAME: 'C',
                NameOID.STATE_OR_PROVINCE_NAME: 'ST',
                NameOID.LOCALITY_NAME: 'L',
                NameOID.EMAIL_ADDRESS: 'EMAIL'
            }.get(attribute.oid, str(attribute.oid))
            
            parts.append(f"{oid_name}={attribute.value}")
        
        return ', '.join(parts)
    
    def _add_extensions(self, builder, cert_params):
        """添加证书扩展"""
        # 基本约束
        if self.cert_type in [CertificateType.ROOT_CA, CertificateType.INTERMEDIATE_CA]:
            builder = builder.add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True
            )
        else:
            builder = builder.add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True
            )
        
        # 密钥用法
        key_usage_flags = {
            'digital_signature': True,
            'key_encipherment': True,
            'data_encipherment': False,
            'key_agreement': False,
            'key_cert_sign': self.cert_type in [CertificateType.ROOT_CA, CertificateType.INTERMEDIATE_CA],
            'crl_sign': self.cert_type in [CertificateType.ROOT_CA, CertificateType.INTERMEDIATE_CA],
            'content_commitment': False,
            'encipher_only': False,
            'decipher_only': False
        }
        
        # 允许参数覆盖
        key_usage_flags.update(cert_params.get('key_usage', {}))
        
        builder = builder.add_extension(
            x509.KeyUsage(**key_usage_flags),
            critical=True
        )
        
        # 扩展密钥用法
        if self.cert_type == CertificateType.CODE_SIGNING:
            builder = builder.add_extension(
                x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CODE_SIGNING]),
                critical=True
            )
        elif self.cert_type == CertificateType.END_ENTITY:
            builder = builder.add_extension(
                x509.ExtendedKeyUsage([
                    ExtendedKeyUsageOID.CLIENT_AUTH,
                    ExtendedKeyUsageOID.SERVER_AUTH
                ]),
                critical=False
            )
        
        # 主题密钥标识符
        builder = builder.add_extension(
            x509.SubjectKeyIdentifier.from_public_key(
                self._get_public_key_from_key_pair()
            ),
            critical=False
        )
        
        # 主题备用名称
        san_list = cert_params.get('subject_alt_names', [])
        if san_list:
            san_names = []
            for san in san_list:
                if san.startswith('DNS:'):
                    san_names.append(x509.DNSName(san[4:]))
                elif san.startswith('IP:'):
                    san_names.append(x509.IPAddress(ipaddress.ip_address(san[3:])))
                elif san.startswith('EMAIL:'):
                    san_names.append(x509.RFC822Name(san[6:]))
            
            if san_names:
                builder = builder.add_extension(
                    x509.SubjectAlternativeName(san_names),
                    critical=False
                )
                self.subject_alt_names = json.dumps([str(san) for san in san_list])
        
        return builder
    
    def _get_public_key_from_key_pair(self):
        """从关联的密钥对获取公钥"""
        from .key_pair import KeyPair
        key_pair = KeyPair.get_by_id(self.key_pair_id)
        return key_pair.get_public_key()
    
    def _generate_fingerprints(self, certificate):
        """生成证书指纹"""
        cert_bytes = certificate.public_bytes(serialization.Encoding.DER)
        
        import hashlib
        self.fingerprint_sha1 = hashlib.sha1(cert_bytes).hexdigest().upper()
        self.fingerprint_sha256 = hashlib.sha256(cert_bytes).hexdigest().upper()
    
    def get_certificate(self):
        """获取证书对象"""
        try:
            return x509.load_pem_x509_certificate(
                self.certificate_pem.encode('utf-8'),
                default_backend()
            )
        except Exception as e:
            raise ValueError(f"无法加载证书: {str(e)}")
    
    def verify_certificate(self, issuer_cert=None):
        """验证证书"""
        try:
            cert = self.get_certificate()
            
            # 检查有效期
            now = datetime.utcnow()
            if now < cert.not_valid_before or now > cert.not_valid_after:
                return False, "证书已过期或尚未生效"
            
            # 如果提供了颁发者证书，验证签名
            if issuer_cert:
                issuer_cert_obj = issuer_cert.get_certificate()
                issuer_public_key = issuer_cert_obj.public_key()
                
                try:
                    issuer_public_key.verify(
                        cert.signature,
                        cert.tbs_certificate_bytes,
                        cert.signature_algorithm_oid
                    )
                except Exception:
                    return False, "证书签名验证失败"
            
            return True, "证书有效"
            
        except Exception as e:
            return False, f"证书验证错误: {str(e)}"
    
    def is_expired(self):
        """检查是否过期"""
        return datetime.utcnow() > self.valid_until
    
    def days_until_expiry(self):
        """距离过期的天数"""
        if self.is_expired():
            return 0
        return (self.valid_until - datetime.utcnow()).days
    
    def revoke(self, reason='unspecified'):
        """吊销证书"""
        self.status = CertificateStatus.REVOKED
        self.revocation_reason = reason
        self.revoked_at = datetime.utcnow()
        self.save()
    
    def suspend(self):
        """暂停证书"""
        self.status = CertificateStatus.SUSPENDED
        self.save()
    
    def reactivate(self):
        """重新激活证书"""
        if not self.is_expired():
            self.status = CertificateStatus.VALID
            self.save()
    
    def get_subject_alt_names(self):
        """获取主题备用名称列表"""
        if not self.subject_alt_names:
            return []
        try:
            return json.loads(self.subject_alt_names)
        except json.JSONDecodeError:
            return []
    
    def export_certificate(self, format='PEM'):
        """导出证书"""
        if format.upper() == 'PEM':
            return self.certificate_pem
        elif format.upper() == 'DER':
            cert = self.get_certificate()
            return cert.public_bytes(serialization.Encoding.DER)
        else:
            raise ValueError(f"不支持的格式: {format}")
    
    def get_cert_info(self):
        """获取证书信息摘要"""
        return {
            'cert_id': self.cert_id,
            'serial_number': self.serial_number,
            'subject_dn': self.subject_dn,
            'issuer_dn': self.issuer_dn,
            'cert_type': self.cert_type.value,
            'status': self.status.value,
            'valid_from': self.valid_from.isoformat(),
            'valid_until': self.valid_until.isoformat(),
            'is_expired': self.is_expired(),
            'days_until_expiry': self.days_until_expiry(),
            'fingerprint_sha256': self.fingerprint_sha256
        }
    
    def to_dict(self):
        """转换为字典"""
        data = super().to_dict()
        
        # 转换枚举值
        data['cert_type'] = self.cert_type.value
        data['status'] = self.status.value
        
        # 添加计算属性
        data['is_expired'] = self.is_expired()
        data['days_until_expiry'] = self.days_until_expiry()
        data['subject_alt_names'] = self.get_subject_alt_names()
        
        return data
    
    @classmethod
    def get_user_certificates(cls, user_id, status=None, cert_type=None):
        """获取用户的证书列表"""
        query = cls.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        if cert_type:
            query = query.filter_by(cert_type=cert_type)
        
        return query.order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_by_serial_number(cls, serial_number):
        """根据序列号获取证书"""
        return cls.query.filter_by(serial_number=serial_number).first()
    
    @classmethod
    def get_expiring_soon(cls, days=30):
        """获取即将过期的证书"""
        expiry_threshold = datetime.utcnow() + timedelta(days=days)
        return cls.query.filter(
            cls.valid_until <= expiry_threshold,
            cls.status == CertificateStatus.VALID
        ).all()
    
    @classmethod
    def create_certificate(cls, user_id, subject_dn, key_pair_id, cert_type='end_entity', **kwargs):
        """创建新证书"""
        # 验证用户是否存在
        from models.user import User
        user = User.get_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        # 验证密钥对是否存在
        from .key_pair import KeyPair
        key_pair = KeyPair.get_by_id(key_pair_id)
        if not key_pair:
            raise ValueError("关联的密钥对不存在")
        
        # 创建证书实例
        certificate = cls(user_id=user_id, subject_dn=subject_dn, 
                         cert_type=cert_type, key_pair_id=key_pair_id, **kwargs)
        
        # 生成证书
        certificate.generate_certificate(**kwargs)
        
        # 保存到数据库
        certificate.save()
        
        return certificate
    
    def __repr__(self):
        return f'<Certificate {self.cert_id} ({self.cert_type.value if self.cert_type else "unknown"})>'