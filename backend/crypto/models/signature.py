"""
签名记录模型
管理数字签名的创建、验证和审计记录
"""

from models.base import BaseModel, db
from datetime import datetime
import enum
import json
import hashlib
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, ec
from cryptography.hazmat.backends import default_backend
import base64

class SignatureType(enum.Enum):
    """签名类型枚举"""
    RSA_PKCS1 = 'rsa_pkcs1'           # RSA PKCS#1 v1.5
    RSA_PSS = 'rsa_pss'               # RSA PSS
    ECDSA = 'ecdsa'                   # ECDSA
    
class HashAlgorithm(enum.Enum):
    """哈希算法枚举"""
    SHA256 = 'sha256'
    SHA384 = 'sha384'
    SHA512 = 'sha512'
    SHA3_256 = 'sha3_256'
    SHA3_384 = 'sha3_384'
    SHA3_512 = 'sha3_512'

class SignatureStatus(enum.Enum):
    """签名状态枚举"""
    VALID = 'valid'                   # 有效
    INVALID = 'invalid'               # 无效
    EXPIRED = 'expired'               # 过期
    REVOKED = 'revoked'               # 吊销

class SignatureRecord(BaseModel):
    """签名记录模型"""
    
    __tablename__ = 'crypto_signatures'
    
    # 基本信息
    signature_id = db.Column(db.String(64), unique=True, nullable=False, index=True)  # 签名ID
    operation_type = db.Column(db.String(50), nullable=False)                         # 操作类型
    
    # 签名信息
    signature_type = db.Column(db.Enum(SignatureType), nullable=False)               # 签名类型
    hash_algorithm = db.Column(db.Enum(HashAlgorithm), nullable=False)               # 哈希算法
    signature_value = db.Column(db.Text, nullable=False)                             # 签名值(Base64)
    
    # 关联信息
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)       # 签名用户
    key_pair_id = db.Column(db.Integer, db.ForeignKey('crypto_key_pairs.id'))        # 签名密钥对
    certificate_id = db.Column(db.Integer, db.ForeignKey('crypto_certificates.id'))  # 签名证书
    
    # 数据信息
    original_data_hash = db.Column(db.String(128), nullable=False)                   # 原始数据哈希
    data_size = db.Column(db.BigInteger)                                             # 数据大小
    data_description = db.Column(db.String(200))                                     # 数据描述
    
    # 验证信息
    status = db.Column(db.Enum(SignatureStatus), default=SignatureStatus.VALID)     # 签名状态
    verified_count = db.Column(db.Integer, default=0)                               # 验证次数
    last_verified_at = db.Column(db.DateTime)                                       # 最后验证时间
    
    # 时间戳信息
    timestamp_authority = db.Column(db.String(100))                                 # 时间戳颁发机构
    timestamp_value = db.Column(db.Text)                                            # 时间戳值
    
    # 元数据
    metadata = db.Column(db.Text)                                                   # 其他元数据JSON
    business_context = db.Column(db.String(100))                                    # 业务上下文
    
    def __init__(self, user_id, operation_type, signature_type='rsa_pkcs1', 
                 hash_algorithm='sha256', **kwargs):
        self.user_id = user_id
        self.operation_type = operation_type
        self.signature_type = signature_type if isinstance(signature_type, SignatureType) else SignatureType(signature_type)
        self.hash_algorithm = hash_algorithm if isinstance(hash_algorithm, HashAlgorithm) else HashAlgorithm(hash_algorithm)
        
        # 生成签名ID
        import secrets
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        random_part = secrets.token_hex(8)
        self.signature_id = f"sig_{timestamp}_{random_part}"
        
        # 设置其他属性
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def sign_data(self, data, key_pair, passphrase=None):
        """对数据进行签名"""
        # 计算数据哈希
        self.original_data_hash = self._calculate_data_hash(data)
        self.data_size = len(data) if isinstance(data, (bytes, str)) else None
        
        # 获取私钥
        try:
            private_key = key_pair.get_private_key(passphrase or "")
        except Exception as e:
            raise ValueError(f"无法获取私钥: {str(e)}")
        
        # 选择哈希算法
        hash_algo = self._get_hash_algorithm()
        
        # 根据签名类型执行签名
        if self.signature_type == SignatureType.RSA_PKCS1:
            signature = private_key.sign(data, padding.PKCS1v15(), hash_algo)
        elif self.signature_type == SignatureType.RSA_PSS:
            signature = private_key.sign(
                data, 
                padding.PSS(
                    mgf=padding.MGF1(hash_algo),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hash_algo
            )
        elif self.signature_type == SignatureType.ECDSA:
            signature = private_key.sign(data, ec.ECDSA(hash_algo))
        else:
            raise ValueError(f"不支持的签名类型: {self.signature_type}")
        
        # 存储签名值
        self.signature_value = base64.b64encode(signature).decode('utf-8')
        self.key_pair_id = key_pair.id
        
        # 更新密钥使用统计
        key_pair.update_usage()
        
        return True
    
    def verify_signature(self, data, public_key=None):
        """验证签名"""
        try:
            # 验证数据哈希
            calculated_hash = self._calculate_data_hash(data)
            if calculated_hash != self.original_data_hash:
                self.status = SignatureStatus.INVALID
                self.save()
                return False, "数据已被篡改"
            
            # 获取公钥
            if public_key is None:
                if self.key_pair_id:
                    from .key_pair import KeyPair
                    key_pair = KeyPair.get_by_id(self.key_pair_id)
                    public_key = key_pair.get_public_key()
                elif self.certificate_id:
                    from .certificate import Certificate
                    certificate = Certificate.get_by_id(self.certificate_id)
                    public_key = certificate.get_certificate().public_key()
                else:
                    return False, "无法获取公钥"
            
            # 解码签名值
            signature_bytes = base64.b64decode(self.signature_value)
            
            # 选择哈希算法
            hash_algo = self._get_hash_algorithm()
            
            # 根据签名类型验证签名
            if self.signature_type == SignatureType.RSA_PKCS1:
                public_key.verify(signature_bytes, data, padding.PKCS1v15(), hash_algo)
            elif self.signature_type == SignatureType.RSA_PSS:
                public_key.verify(
                    signature_bytes, 
                    data,
                    padding.PSS(
                        mgf=padding.MGF1(hash_algo),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hash_algo
                )
            elif self.signature_type == SignatureType.ECDSA:
                public_key.verify(signature_bytes, data, ec.ECDSA(hash_algo))
            else:
                return False, f"不支持的签名类型: {self.signature_type}"
            
            # 更新验证统计
            self.verified_count += 1
            self.last_verified_at = datetime.utcnow()
            
            # 检查证书状态
            if self.certificate_id:
                from .certificate import Certificate
                certificate = Certificate.get_by_id(self.certificate_id)
                if certificate and certificate.is_expired():
                    self.status = SignatureStatus.EXPIRED
                    self.save()
                    return False, "签名证书已过期"
            
            self.save()
            return True, "签名验证成功"
            
        except Exception as e:
            self.status = SignatureStatus.INVALID
            self.save()
            return False, f"签名验证失败: {str(e)}"
    
    def _calculate_data_hash(self, data):
        """计算数据哈希"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        hash_func = {
            HashAlgorithm.SHA256: hashlib.sha256,
            HashAlgorithm.SHA384: hashlib.sha384,
            HashAlgorithm.SHA512: hashlib.sha512,
            HashAlgorithm.SHA3_256: hashlib.sha3_256,
            HashAlgorithm.SHA3_384: hashlib.sha3_384,
            HashAlgorithm.SHA3_512: hashlib.sha3_512,
        }[self.hash_algorithm]
        
        return hash_func(data).hexdigest()
    
    def _get_hash_algorithm(self):
        """获取哈希算法对象"""
        return {
            HashAlgorithm.SHA256: hashes.SHA256(),
            HashAlgorithm.SHA384: hashes.SHA384(),
            HashAlgorithm.SHA512: hashes.SHA512(),
            HashAlgorithm.SHA3_256: hashes.SHA3_256(),
            HashAlgorithm.SHA3_384: hashes.SHA3_384(),
            HashAlgorithm.SHA3_512: hashes.SHA3_512(),
        }[self.hash_algorithm]
    
    def add_timestamp(self, timestamp_authority=None, timestamp_value=None):
        """添加时间戳"""
        self.timestamp_authority = timestamp_authority or "Internal TSA"
        self.timestamp_value = timestamp_value or datetime.utcnow().isoformat()
        self.save()
    
    def revoke_signature(self, reason=None):
        """吊销签名"""
        self.status = SignatureStatus.REVOKED
        
        metadata = self.get_metadata()
        metadata['revocation_reason'] = reason or "Manual revocation"
        metadata['revoked_at'] = datetime.utcnow().isoformat()
        self.set_metadata(metadata)
        
        self.save()
    
    def get_metadata(self):
        """获取元数据"""
        if not self.metadata:
            return {}
        try:
            return json.loads(self.metadata)
        except json.JSONDecodeError:
            return {}
    
    def set_metadata(self, metadata):
        """设置元数据"""
        self.metadata = json.dumps(metadata, ensure_ascii=False)
    
    def add_metadata(self, key, value):
        """添加元数据"""
        metadata = self.get_metadata()
        metadata[key] = value
        self.set_metadata(metadata)
        self.save()
    
    def export_signature(self, format='base64'):
        """导出签名"""
        if format.lower() == 'base64':
            return self.signature_value
        elif format.lower() == 'hex':
            return base64.b64decode(self.signature_value).hex().upper()
        elif format.lower() == 'binary':
            return base64.b64decode(self.signature_value)
        else:
            raise ValueError(f"不支持的格式: {format}")
    
    def get_signature_info(self):
        """获取签名信息摘要"""
        return {
            'signature_id': self.signature_id,
            'operation_type': self.operation_type,
            'signature_type': self.signature_type.value,
            'hash_algorithm': self.hash_algorithm.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'verified_count': self.verified_count,
            'last_verified_at': self.last_verified_at.isoformat() if self.last_verified_at else None,
            'data_size': self.data_size,
            'has_timestamp': bool(self.timestamp_value)
        }
    
    def generate_signature_report(self):
        """生成签名报告"""
        report = {
            'signature_details': self.get_signature_info(),
            'technical_info': {
                'signature_algorithm': f"{self.signature_type.value}_{self.hash_algorithm.value}",
                'key_info': None,
                'certificate_info': None
            },
            'verification_history': {
                'total_verifications': self.verified_count,
                'last_verification': self.last_verified_at.isoformat() if self.last_verified_at else None
            },
            'metadata': self.get_metadata()
        }
        
        # 添加密钥信息
        if self.key_pair_id:
            from .key_pair import KeyPair
            key_pair = KeyPair.get_by_id(self.key_pair_id)
            if key_pair:
                report['technical_info']['key_info'] = key_pair.get_key_info()
        
        # 添加证书信息
        if self.certificate_id:
            from .certificate import Certificate
            certificate = Certificate.get_by_id(self.certificate_id)
            if certificate:
                report['technical_info']['certificate_info'] = certificate.get_cert_info()
        
        return report
    
    def to_dict(self):
        """转换为字典"""
        data = super().to_dict()
        
        # 转换枚举值
        data['signature_type'] = self.signature_type.value
        data['hash_algorithm'] = self.hash_algorithm.value
        data['status'] = self.status.value
        
        # 添加计算属性
        data['metadata'] = self.get_metadata()
        data['has_timestamp'] = bool(self.timestamp_value)
        
        return data
    
    @classmethod
    def get_user_signatures(cls, user_id, status=None, operation_type=None):
        """获取用户的签名记录"""
        query = cls.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        if operation_type:
            query = query.filter_by(operation_type=operation_type)
        
        return query.order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_by_signature_id(cls, signature_id):
        """根据签名ID获取签名记录"""
        return cls.query.filter_by(signature_id=signature_id).first()
    
    @classmethod
    def get_signatures_by_data_hash(cls, data_hash):
        """根据数据哈希获取签名记录"""
        return cls.query.filter_by(original_data_hash=data_hash).all()
    
    @classmethod
    def create_signature(cls, user_id, data, key_pair, operation_type='document_signing', 
                        signature_type='rsa_pkcs1', hash_algorithm='sha256', **kwargs):
        """创建新签名"""
        # 验证用户是否存在
        from models.user import User
        user = User.get_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        # 创建签名记录
        signature_record = cls(
            user_id=user_id,
            operation_type=operation_type,
            signature_type=signature_type,
            hash_algorithm=hash_algorithm,
            **kwargs
        )
        
        # 执行签名
        passphrase = kwargs.get('passphrase', '')
        signature_record.sign_data(data, key_pair, passphrase)
        
        # 保存到数据库
        signature_record.save()
        
        return signature_record
    
    @classmethod
    def verify_signature_by_id(cls, signature_id, data):
        """根据签名ID验证签名"""
        signature_record = cls.get_by_signature_id(signature_id)
        if not signature_record:
            return False, "签名记录不存在"
        
        return signature_record.verify_signature(data)
    
    def __repr__(self):
        return f'<SignatureRecord {self.signature_id} ({self.operation_type})>'