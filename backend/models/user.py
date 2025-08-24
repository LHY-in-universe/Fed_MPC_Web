"""
用户模型
处理用户认证、权限管理等功能
"""

from .base import BaseModel, db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum

class UserType(enum.Enum):
    """用户类型枚举"""
    CLIENT = 'client'
    SERVER = 'server'

class BusinessType(enum.Enum):
    """业务类型枚举"""
    AI = 'ai'
    BLOCKCHAIN = 'blockchain'
    CRYPTO = 'crypto'

class UserStatus(enum.Enum):
    """用户状态枚举"""
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'

class User(BaseModel):
    """用户模型"""
    
    __tablename__ = 'users'
    
    # 基本信息
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100))
    full_name = db.Column(db.String(100))
    organization = db.Column(db.String(100))
    
    # 业务信息
    user_type = db.Column(db.Enum(UserType), nullable=False, index=True)
    business_type = db.Column(db.Enum(BusinessType), nullable=False, index=True)
    status = db.Column(db.Enum(UserStatus), default=UserStatus.ACTIVE)
    
    # 登录信息
    last_login = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)
    
    # 关联关系
    projects = db.relationship('Project', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    training_requests = db.relationship('TrainingRequest', 
                                      foreign_keys='TrainingRequest.client_user_id',
                                      backref='client_user', 
                                      lazy='dynamic')
    approved_requests = db.relationship('TrainingRequest', 
                                      foreign_keys='TrainingRequest.approved_by',
                                      backref='approver', 
                                      lazy='dynamic')
    
    def __init__(self, username, password, user_type, business_type, **kwargs):
        self.username = username
        self.set_password(password)
        self.user_type = user_type if isinstance(user_type, UserType) else UserType(user_type)
        self.business_type = business_type if isinstance(business_type, BusinessType) else BusinessType(business_type)
        
        # 设置其他属性
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login = datetime.utcnow()
        self.login_count += 1
        self.save()
    
    def is_client(self):
        """是否为客户端用户"""
        return self.user_type == UserType.CLIENT
    
    def is_server(self):
        """是否为服务器管理员"""
        return self.user_type == UserType.SERVER
    
    def is_active(self):
        """用户是否激活"""
        return self.status == UserStatus.ACTIVE
    
    def can_access_business_type(self, business_type):
        """是否可以访问指定业务类型"""
        if isinstance(business_type, str):
            business_type = BusinessType(business_type)
        return self.business_type == business_type
    
    def get_permissions(self):
        """获取用户权限列表"""
        base_permissions = []
        
        if self.is_client():
            if self.business_type == BusinessType.AI:
                base_permissions.extend([
                    'create_local_project',
                    'view_own_projects', 
                    'submit_training_request',
                    'view_training_progress',
                    'download_own_models',
                    'manage_datasets',
                    'view_model_metrics'
                ])
            elif self.business_type == BusinessType.BLOCKCHAIN:
                base_permissions.extend([
                    'create_transactions',
                    'view_own_transactions',
                    'manage_wallet',
                    'view_blockchain_info',
                    'participate_in_consensus'
                ])
            elif self.business_type == BusinessType.CRYPTO:
                base_permissions.extend([
                    'generate_keys',
                    'encrypt_decrypt',
                    'digital_signature',
                    'key_exchange',
                    'view_crypto_operations'
                ])
        elif self.is_server():
            if self.business_type == BusinessType.AI:
                base_permissions.extend([
                    'manage_all_clients',
                    'approve_training_requests',
                    'view_global_projects',
                    'manage_models',
                    'system_configuration',
                    'view_system_logs',
                    'monitor_training',
                    'manage_federated_learning'
                ])
            elif self.business_type == BusinessType.BLOCKCHAIN:
                base_permissions.extend([
                    'manage_blockchain_network',
                    'validate_transactions',
                    'manage_consensus',
                    'view_all_transactions',
                    'system_administration',
                    'node_management'
                ])
            elif self.business_type == BusinessType.CRYPTO:
                base_permissions.extend([
                    'manage_key_infrastructure',
                    'audit_crypto_operations',
                    'system_security_config',
                    'manage_certificates',
                    'security_monitoring',
                    'compliance_reporting'
                ])
        
        return base_permissions
    
    def to_dict(self, include_sensitive=False):
        """转换为字典，默认排除敏感信息"""
        exclude_fields = ['password_hash'] if not include_sensitive else []
        data = super().to_dict(exclude_fields=exclude_fields)
        
        # 转换枚举值
        data['user_type'] = self.user_type.value
        data['business_type'] = self.business_type.value  
        data['status'] = self.status.value
        
        # 添加权限信息
        data['permissions'] = self.get_permissions()
        
        return data
    
    @classmethod
    def find_by_username(cls, username):
        """根据用户名查找用户"""
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def find_by_email(cls, email):
        """根据邮箱查找用户"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_by_user_type(cls, user_type, business_type=None):
        """根据用户类型获取用户列表"""
        query = cls.query.filter_by(user_type=user_type)
        if business_type:
            query = query.filter_by(business_type=business_type)
        return query.all()
    
    @classmethod
    def create_user(cls, username, password, user_type, business_type, **kwargs):
        """创建新用户"""
        # 检查用户名是否已存在
        if cls.find_by_username(username):
            raise ValueError(f"用户名 '{username}' 已存在")
        
        # 检查邮箱是否已存在
        email = kwargs.get('email')
        if email and cls.find_by_email(email):
            raise ValueError(f"邮箱 '{email}' 已被使用")
        
        # 创建用户
        user = cls(username=username, password=password, 
                  user_type=user_type, business_type=business_type, **kwargs)
        user.save()
        return user
    
    def __repr__(self):
        return f'<User {self.username} ({self.user_type.value})>'