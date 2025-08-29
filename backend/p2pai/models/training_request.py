"""
训练申请模型
管理联邦学习训练申请的审批流程
"""

from .base import BaseModel, db
from datetime import datetime
import enum
import json

class RequestStatus(enum.Enum):
    """申请状态枚举"""
    PENDING = 'pending'           # 待审核
    APPROVED = 'approved'         # 已批准
    REJECTED = 'rejected'         # 已拒绝
    CANCELLED = 'cancelled'       # 已取消
    EXPIRED = 'expired'           # 已过期

class RequestType(enum.Enum):
    """申请类型枚举"""
    FEDERATED_TRAINING = 'federated_training'  # 联邦训练申请
    DATA_SHARING = 'data_sharing'              # 数据共享申请
    MODEL_ACCESS = 'model_access'              # 模型访问申请

class TrainingRequest(BaseModel):
    """训练申请模型"""
    
    __tablename__ = 'training_requests'
    
    # 基本信息
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    request_type = db.Column(db.Enum(RequestType), nullable=False, default=RequestType.FEDERATED_TRAINING)
    status = db.Column(db.Enum(RequestStatus), default=RequestStatus.PENDING, index=True)
    
    # 申请方信息
    client_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    client_organization = db.Column(db.String(100))
    
    # 关联项目
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), index=True)
    
    # 训练参数
    training_mode = db.Column(db.String(20))  # normal, mpc
    business_type = db.Column(db.String(20))  # ai, blockchain
    model_type = db.Column(db.String(100))
    expected_participants = db.Column(db.Integer, default=1)
    max_rounds = db.Column(db.Integer, default=100)
    
    # 数据信息
    data_description = db.Column(db.Text)
    data_size = db.Column(db.BigInteger)  # 数据大小（字节）
    data_samples = db.Column(db.Integer)  # 样本数量
    data_features = db.Column(db.Text)    # JSON格式的数据特征描述
    
    # 安全和隐私要求
    privacy_level = db.Column(db.String(20), default='medium')  # low, medium, high
    encryption_required = db.Column(db.Boolean, default=False)
    audit_required = db.Column(db.Boolean, default=False)
    
    # 时间要求
    expected_start_time = db.Column(db.DateTime)
    expected_duration = db.Column(db.Integer)  # 预期持续时间（小时）
    deadline = db.Column(db.DateTime)
    
    # 审批信息
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approval_time = db.Column(db.DateTime)
    approval_notes = db.Column(db.Text)
    rejection_reason = db.Column(db.Text)
    
    # 附加信息
    requirements = db.Column(db.Text)  # JSON格式的具体需求
    contact_info = db.Column(db.Text)  # 联系信息
    priority = db.Column(db.Integer, default=0)  # 优先级（0-10）
    
    def __init__(self, client_user_id, title, request_type='federated_training', **kwargs):
        self.client_user_id = client_user_id
        self.title = title
        self.request_type = request_type if isinstance(request_type, RequestType) else RequestType(request_type)
        
        # 设置其他属性
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def approve(self, approver_user_id, notes=None):
        """批准申请"""
        if self.status != RequestStatus.PENDING:
            raise ValueError(f"申请状态 '{self.status.value}' 无法批准")
        
        self.status = RequestStatus.APPROVED
        self.approved_by = approver_user_id
        self.approval_time = datetime.utcnow()
        self.approval_notes = notes
        self.save()
        
        # 如果有关联项目，更新项目状态
        if self.project_id:
            from .project import Project, ProjectStatus
            project = Project.get_by_id(self.project_id)
            if project and project.status == ProjectStatus.WAITING_APPROVAL:
                project.status = ProjectStatus.APPROVED
                project.save()
    
    def reject(self, approver_user_id, reason, notes=None):
        """拒绝申请"""
        if self.status != RequestStatus.PENDING:
            raise ValueError(f"申请状态 '{self.status.value}' 无法拒绝")
        
        self.status = RequestStatus.REJECTED
        self.approved_by = approver_user_id
        self.approval_time = datetime.utcnow()
        self.rejection_reason = reason
        self.approval_notes = notes
        self.save()
        
        # 如果有关联项目，更新项目状态
        if self.project_id:
            from .project import Project, ProjectStatus
            project = Project.get_by_id(self.project_id)
            if project and project.status == ProjectStatus.WAITING_APPROVAL:
                project.status = ProjectStatus.REJECTED
                project.save()
    
    def cancel(self, reason=None):
        """取消申请"""
        if self.status not in [RequestStatus.PENDING]:
            raise ValueError(f"申请状态 '{self.status.value}' 无法取消")
        
        self.status = RequestStatus.CANCELLED
        self.rejection_reason = reason or "申请方主动取消"
        self.save()
    
    def expire(self):
        """过期申请"""
        if self.status == RequestStatus.PENDING:
            self.status = RequestStatus.EXPIRED
            self.save()
    
    def can_be_approved(self):
        """检查是否可以批准"""
        return self.status == RequestStatus.PENDING and not self.is_expired()
    
    def can_be_rejected(self):
        """检查是否可以拒绝"""
        return self.status == RequestStatus.PENDING
    
    def can_be_cancelled(self):
        """检查是否可以取消"""
        return self.status == RequestStatus.PENDING
    
    def is_expired(self):
        """检查是否过期"""
        if not self.deadline:
            return False
        return datetime.utcnow() > self.deadline
    
    def is_pending(self):
        """检查是否待审核"""
        return self.status == RequestStatus.PENDING
    
    def is_approved(self):
        """检查是否已批准"""
        return self.status == RequestStatus.APPROVED
    
    def is_rejected(self):
        """检查是否已拒绝"""
        return self.status == RequestStatus.REJECTED
    
    def get_data_features(self):
        """获取数据特征"""
        if not self.data_features:
            return {}
        try:
            return json.loads(self.data_features)
        except json.JSONDecodeError:
            return {}
    
    def set_data_features(self, features):
        """设置数据特征"""
        self.data_features = json.dumps(features, ensure_ascii=False)
    
    def get_requirements(self):
        """获取需求信息"""
        if not self.requirements:
            return {}
        try:
            return json.loads(self.requirements)
        except json.JSONDecodeError:
            return {}
    
    def set_requirements(self, requirements):
        """设置需求信息"""
        self.requirements = json.dumps(requirements, ensure_ascii=False)
    
    def get_contact_info(self):
        """获取联系信息"""
        if not self.contact_info:
            return {}
        try:
            return json.loads(self.contact_info)
        except json.JSONDecodeError:
            return {}
    
    def set_contact_info(self, contact_info):
        """设置联系信息"""
        self.contact_info = json.dumps(contact_info, ensure_ascii=False)
    
    def get_processing_time(self):
        """获取处理时间"""
        if not self.approval_time:
            return None
        return (self.approval_time - self.created_at).total_seconds()
    
    def get_days_since_submission(self):
        """获取提交天数"""
        return (datetime.utcnow() - self.created_at).days
    
    def get_urgency_level(self):
        """获取紧急程度"""
        if not self.deadline:
            return 'normal'
        
        days_until_deadline = (self.deadline - datetime.utcnow()).days
        
        if days_until_deadline < 0:
            return 'expired'
        elif days_until_deadline <= 1:
            return 'urgent'
        elif days_until_deadline <= 3:
            return 'high'
        else:
            return 'normal'
    
    def to_dict(self, include_sensitive=False):
        """转换为字典"""
        data = super().to_dict()
        
        # 转换枚举值
        data['request_type'] = self.request_type.value if self.request_type else None
        data['status'] = self.status.value if self.status else None
        
        # 添加计算属性
        data['is_expired'] = self.is_expired()
        data['urgency_level'] = self.get_urgency_level()
        data['days_since_submission'] = self.get_days_since_submission()
        data['processing_time'] = self.get_processing_time()
        
        # 添加解析的JSON字段
        data['data_features'] = self.get_data_features()
        data['requirements'] = self.get_requirements()
        
        # 联系信息只在需要时包含
        if include_sensitive:
            data['contact_info'] = self.get_contact_info()
        
        return data
    
    @classmethod
    def get_pending_requests(cls, business_type=None, request_type=None):
        """获取待审核的申请"""
        query = cls.query.filter_by(status=RequestStatus.PENDING)
        
        if business_type:
            query = query.filter_by(business_type=business_type)
        if request_type:
            query = query.filter_by(request_type=request_type)
        
        return query.order_by(cls.priority.desc(), cls.created_at.asc()).all()
    
    @classmethod
    def get_user_requests(cls, user_id, status=None):
        """获取用户的申请"""
        query = cls.query.filter_by(client_user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_expired_requests(cls):
        """获取过期的申请"""
        return cls.query.filter(
            cls.status == RequestStatus.PENDING,
            cls.deadline < datetime.utcnow()
        ).all()
    
    @classmethod
    def get_urgent_requests(cls, days=3):
        """获取紧急申请"""
        urgent_deadline = datetime.utcnow() + datetime.timedelta(days=days)
        return cls.query.filter(
            cls.status == RequestStatus.PENDING,
            cls.deadline <= urgent_deadline
        ).order_by(cls.deadline.asc()).all()
    
    @classmethod
    def create_request(cls, client_user_id, title, request_type='federated_training', **kwargs):
        """创建新申请"""
        # 验证用户是否存在
        from .user import User
        user = User.get_by_id(client_user_id)
        if not user:
            raise ValueError("用户不存在")
        
        # 创建申请
        request = cls(client_user_id=client_user_id, title=title, 
                     request_type=request_type, **kwargs)
        
        # 设置申请方组织
        if user.organization and not request.client_organization:
            request.client_organization = user.organization
        
        request.save()
        return request
    
    @classmethod
    def auto_expire_requests(cls):
        """自动过期超期申请"""
        expired_requests = cls.get_expired_requests()
        for request in expired_requests:
            request.expire()
        return len(expired_requests)
    
    def __repr__(self):
        return f'<TrainingRequest {self.title} ({self.status.value if self.status else "unknown"})>'