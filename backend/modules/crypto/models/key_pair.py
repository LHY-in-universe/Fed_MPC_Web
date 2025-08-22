"""
密钥对模型
管理RSA、ECC等密钥对的生成、存储和使用
"""

from models.base import BaseModel, db
from datetime import datetime, timedelta
import enum
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.backends import default_backend
import secrets

class KeyType(enum.Enum):
    """密钥类型枚举"""
    RSA = 'rsa'
    ECC = 'ecc'
    
class KeyUsage(enum.Enum):
    """密钥用途枚举"""
    ENCRYPTION = 'encryption'    # 加密
    SIGNING = 'signing'         # 签名
    BOTH = 'both'              # 加密和签名

class KeyStatus(enum.Enum):
    """密钥状态枚举"""
    ACTIVE = 'active'          # 活跃
    EXPIRED = 'expired'        # 过期
    REVOKED = 'revoked'        # 吊销
    ARCHIVED = 'archived'      # 归档

class KeyPair(BaseModel):
    """密钥对模型"""
    
    __tablename__ = 'crypto_key_pairs'
    
    # 基本信息
    key_id = db.Column(db.String(64), unique=True, nullable=False, index=True)  # 密钥ID
    name = db.Column(db.String(100), nullable=False)                             # 密钥名称
    description = db.Column(db.Text)                                            # 描述
    
    # 密钥属性
    key_type = db.Column(db.Enum(KeyType), nullable=False)                      # 密钥类型
    key_size = db.Column(db.Integer, nullable=False)                            # 密钥长度
    key_usage = db.Column(db.Enum(KeyUsage), nullable=False)                    # 密钥用途
    status = db.Column(db.Enum(KeyStatus), default=KeyStatus.ACTIVE)            # 密钥状态
    
    # 所属信息
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 所属用户
    business_type = db.Column(db.String(20), nullable=False)                    # 业务类型
    
    # 密钥数据（加密存储）
    public_key_pem = db.Column(db.Text, nullable=False)                         # 公钥PEM
    private_key_encrypted = db.Column(db.Text, nullable=False)                  # 加密的私钥
    salt = db.Column(db.String(64), nullable=False)                            # 加密盐值
    
    # 时间管理
    expires_at = db.Column(db.DateTime)                                         # 过期时间
    last_used_at = db.Column(db.DateTime)                                       # 最后使用时间
    
    # 使用统计
    usage_count = db.Column(db.Integer, default=0)                             # 使用次数
    
    # 元数据
    algorithm_params = db.Column(db.Text)                                       # 算法参数JSON
    fingerprint = db.Column(db.String(64), unique=True, nullable=False)        # 指纹
    
    def __init__(self, user_id, name, key_type='rsa', key_size=2048, 
                 key_usage='both', business_type='crypto', **kwargs):
        self.user_id = user_id
        self.name = name
        self.key_type = key_type if isinstance(key_type, KeyType) else KeyType(key_type)
        self.key_size = key_size
        self.key_usage = key_usage if isinstance(key_usage, KeyUsage) else KeyUsage(key_usage)
        self.business_type = business_type
        
        # 生成唯一密钥ID
        self.key_id = self._generate_key_id()
        
        # 设置其他属性
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def _generate_key_id(self):
        """生成唯一密钥ID"""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        random_part = secrets.token_hex(8)
        return f"{self.key_type.value}_{timestamp}_{random_part}"
    
    def generate_key_pair(self, passphrase=None):
        """生成密钥对"""
        if self.key_type == KeyType.RSA:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self.key_size,
                backend=default_backend()
            )
        elif self.key_type == KeyType.ECC:
            # 根据密钥大小选择曲线
            if self.key_size == 256:
                curve = ec.SECP256R1()
            elif self.key_size == 384:
                curve = ec.SECP384R1()
            elif self.key_size == 521:
                curve = ec.SECP521R1()
            else:
                curve = ec.SECP256R1()  # 默认
            
            private_key = ec.generate_private_key(curve, default_backend())
        else:
            raise ValueError(f"不支持的密钥类型: {self.key_type}")
        
        # 生成公钥PEM
        public_key = private_key.public_key()
        self.public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        # 加密并存储私钥
        self._encrypt_and_store_private_key(private_key, passphrase)
        
        # 生成指纹
        self.fingerprint = self._generate_fingerprint()
        
        return True
    
    def _encrypt_and_store_private_key(self, private_key, passphrase=None):
        """加密并存储私钥"""
        # 生成随机盐值
        self.salt = secrets.token_hex(32)
        
        # 如果没有提供密码，生成一个随机密码
        if passphrase is None:
            passphrase = secrets.token_urlsafe(32)
        
        # 序列化私钥并加密
        encryption_algorithm = serialization.BestAvailableEncryption(passphrase.encode())
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        )
        
        # 存储加密的私钥
        self.private_key_encrypted = private_pem.decode('utf-8')
        
        # 存储密码哈希（用于验证，但不存储明文密码）
        import hashlib
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                          passphrase.encode(), 
                                          self.salt.encode(), 
                                          100000)
        
        # 将密码哈希存储在算法参数中
        params = self.get_algorithm_params()
        params['password_hash'] = password_hash.hex()
        self.set_algorithm_params(params)
    
    def _generate_fingerprint(self):
        """生成密钥指纹"""
        import hashlib
        public_key_bytes = self.public_key_pem.encode('utf-8')
        return hashlib.sha256(public_key_bytes).hexdigest()[:32]
    
    def get_public_key(self):
        """获取公钥对象"""
        try:
            return serialization.load_pem_public_key(
                self.public_key_pem.encode('utf-8'),
                backend=default_backend()
            )
        except Exception as e:
            raise ValueError(f"无法加载公钥: {str(e)}")
    
    def get_private_key(self, passphrase):
        """获取私钥对象"""
        try:
            return serialization.load_pem_private_key(
                self.private_key_encrypted.encode('utf-8'),
                password=passphrase.encode('utf-8'),
                backend=default_backend()
            )
        except Exception as e:
            raise ValueError(f"无法加载私钥，请检查密码: {str(e)}")
    
    def verify_passphrase(self, passphrase):
        """验证密码"""
        import hashlib
        
        params = self.get_algorithm_params()
        stored_hash = params.get('password_hash', '')
        
        computed_hash = hashlib.pbkdf2_hmac('sha256',
                                          passphrase.encode(),
                                          self.salt.encode(),
                                          100000)
        
        return computed_hash.hex() == stored_hash
    
    def update_usage(self):
        """更新使用统计"""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()
        self.save()
    
    def is_expired(self):
        """检查是否过期"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def revoke(self, reason=None):
        """吊销密钥"""
        self.status = KeyStatus.REVOKED
        
        params = self.get_algorithm_params()
        params['revocation_reason'] = reason or "Manual revocation"
        params['revoked_at'] = datetime.utcnow().isoformat()
        self.set_algorithm_params(params)
        
        self.save()
    
    def archive(self):
        """归档密钥"""
        self.status = KeyStatus.ARCHIVED
        self.save()
    
    def extend_expiry(self, days=365):
        """延长过期时间"""
        if self.expires_at:
            self.expires_at += timedelta(days=days)
        else:
            self.expires_at = datetime.utcnow() + timedelta(days=days)
        self.save()
    
    def get_algorithm_params(self):
        """获取算法参数"""
        if not self.algorithm_params:
            return {}
        try:
            return json.loads(self.algorithm_params)
        except json.JSONDecodeError:
            return {}
    
    def set_algorithm_params(self, params):
        """设置算法参数"""
        self.algorithm_params = json.dumps(params, ensure_ascii=False)
    
    def export_public_key(self, format='PEM'):
        """导出公钥"""
        if format.upper() == 'PEM':
            return self.public_key_pem
        elif format.upper() == 'DER':
            public_key = self.get_public_key()
            return public_key.public_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        else:
            raise ValueError(f"不支持的格式: {format}")
    
    def get_key_info(self):
        """获取密钥信息摘要"""
        return {
            'key_id': self.key_id,
            'name': self.name,
            'key_type': self.key_type.value,
            'key_size': self.key_size,
            'key_usage': self.key_usage.value,
            'status': self.status.value,
            'fingerprint': self.fingerprint,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'usage_count': self.usage_count,
            'is_expired': self.is_expired()
        }
    
    def to_dict(self, include_private=False):
        """转换为字典"""
        data = super().to_dict()
        
        # 转换枚举值
        data['key_type'] = self.key_type.value
        data['key_usage'] = self.key_usage.value
        data['status'] = self.status.value
        
        # 添加计算属性
        data['is_expired'] = self.is_expired()
        data['algorithm_params'] = self.get_algorithm_params()
        
        # 默认不包含私钥
        if not include_private:
            data.pop('private_key_encrypted', None)
            data.pop('salt', None)
        
        return data
    
    @classmethod
    def get_user_keys(cls, user_id, status=None, key_type=None):
        """获取用户的密钥列表"""
        query = cls.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        if key_type:
            query = query.filter_by(key_type=key_type)
        
        return query.order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_by_key_id(cls, key_id):
        """根据密钥ID获取密钥"""
        return cls.query.filter_by(key_id=key_id).first()
    
    @classmethod
    def get_active_keys(cls, user_id=None):
        """获取活跃密钥"""
        query = cls.query.filter_by(status=KeyStatus.ACTIVE)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        return query.all()
    
    @classmethod
    def create_key_pair(cls, user_id, name, key_type='rsa', key_size=2048, 
                       passphrase=None, **kwargs):
        """创建新密钥对"""
        # 验证用户是否存在
        from models.user import User
        user = User.get_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        # 创建密钥对实例
        key_pair = cls(user_id=user_id, name=name, key_type=key_type, 
                      key_size=key_size, **kwargs)
        
        # 生成密钥对
        key_pair.generate_key_pair(passphrase)
        
        # 保存到数据库
        key_pair.save()
        
        return key_pair
    
    def __repr__(self):
        return f'<KeyPair {self.key_id} ({self.key_type.value if self.key_type else "unknown"})>'