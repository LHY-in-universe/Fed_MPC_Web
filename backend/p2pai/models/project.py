"""
项目模型
处理联邦学习项目的创建、管理等功能
"""

from .base import BaseModel, db
import enum
from decimal import Decimal

class ProjectType(enum.Enum):
    """项目类型枚举"""
    LOCAL = 'local'
    FEDERATED = 'federated'

class TrainingMode(enum.Enum):
    """训练模式枚举"""
    NORMAL = 'normal'
    MPC = 'mpc'

class ProjectStatus(enum.Enum):
    """项目状态枚举"""
    CREATED = 'created'
    RUNNING = 'running'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    WAITING_APPROVAL = 'waiting_approval'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    STOPPED = 'stopped'

class BusinessType(enum.Enum):
    """业务类型枚举"""
    AI = 'ai'
    BLOCKCHAIN = 'blockchain'

class Project(BaseModel):
    """项目模型"""
    
    __tablename__ = 'projects'
    
    # 基本信息
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # 项目类型和模式
    project_type = db.Column(db.Enum(ProjectType), nullable=False, index=True)
    training_mode = db.Column(db.Enum(TrainingMode), nullable=False)
    business_type = db.Column(db.Enum(BusinessType), nullable=False, index=True)
    status = db.Column(db.Enum(ProjectStatus), default=ProjectStatus.CREATED, index=True)
    
    # 模型信息
    model_type = db.Column(db.String(50))
    model_config = db.Column(db.Text)  # JSON格式的模型配置
    
    # 训练指标
    accuracy = db.Column(db.DECIMAL(5, 4), default=Decimal('0.0000'))
    loss = db.Column(db.DECIMAL(8, 6), default=Decimal('0.000000'))
    current_round = db.Column(db.Integer, default=0)
    total_rounds = db.Column(db.Integer, default=100)
    
    # 节点信息
    nodes_online = db.Column(db.Integer, default=0)
    nodes_total = db.Column(db.Integer, default=1)
    
    # 文件路径
    model_path = db.Column(db.String(255))
    data_path = db.Column(db.String(255))
    
    # 关联关系
    training_sessions = db.relationship('TrainingSession', backref='project', 
                                      lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, user_id, name, project_type, training_mode, business_type, **kwargs):
        self.user_id = user_id
        self.name = name
        self.project_type = project_type if isinstance(project_type, ProjectType) else ProjectType(project_type)
        self.training_mode = training_mode if isinstance(training_mode, TrainingMode) else TrainingMode(training_mode)
        self.business_type = business_type if isinstance(business_type, BusinessType) else BusinessType(business_type)
        
        # 设置其他属性
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def can_start_training(self):
        """检查是否可以开始训练"""
        return self.status in [ProjectStatus.CREATED, ProjectStatus.PAUSED, ProjectStatus.APPROVED]
    
    def can_stop_training(self):
        """检查是否可以停止训练"""
        return self.status == ProjectStatus.RUNNING
    
    def can_delete(self):
        """检查是否可以删除"""
        return self.status not in [ProjectStatus.RUNNING]
    
    def is_mpc_mode(self):
        """是否为MPC模式"""
        return self.training_mode == TrainingMode.MPC
    
    def is_federated(self):
        """是否为联邦训练项目"""
        return self.project_type == ProjectType.FEDERATED
    
    def update_training_metrics(self, accuracy=None, loss=None, current_round=None):
        """更新训练指标"""
        if accuracy is not None:
            self.accuracy = Decimal(str(accuracy))
        if loss is not None:
            self.loss = Decimal(str(loss))
        if current_round is not None:
            self.current_round = current_round
        self.save()
    
    def start_training(self):
        """开始训练"""
        if not self.can_start_training():
            raise ValueError(f"项目状态 '{self.status.value}' 无法开始训练")
        
        self.status = ProjectStatus.RUNNING
        self.nodes_online = self.nodes_total if self.is_federated() else 1
        self.save()
    
    def pause_training(self):
        """暂停训练"""
        if self.status != ProjectStatus.RUNNING:
            raise ValueError("只有运行中的项目可以暂停")
        
        self.status = ProjectStatus.PAUSED
        self.save()
    
    def stop_training(self):
        """停止训练"""
        if not self.can_stop_training():
            raise ValueError("无法停止非运行状态的项目")
        
        self.status = ProjectStatus.STOPPED
        self.nodes_online = 0
        self.save()
    
    def complete_training(self):
        """完成训练"""
        if self.status != ProjectStatus.RUNNING:
            raise ValueError("只有运行中的项目可以完成")
        
        self.status = ProjectStatus.COMPLETED
        self.current_round = self.total_rounds
        self.save()
    
    def get_training_progress(self):
        """获取训练进度"""
        if self.total_rounds == 0:
            return 0.0
        return round((self.current_round / self.total_rounds) * 100, 2)
    
    def get_masked_metrics(self):
        """获取MPC模式下的脱敏指标"""
        if self.is_mpc_mode():
            return {
                'accuracy': '***',
                'loss': '***',
                'current_round': self.current_round,
                'total_rounds': self.total_rounds,
                'progress': self.get_training_progress()
            }
        else:
            return {
                'accuracy': float(self.accuracy),
                'loss': float(self.loss),
                'current_round': self.current_round,
                'total_rounds': self.total_rounds,
                'progress': self.get_training_progress()
            }
    
    def to_dict(self):
        """转换为字典"""
        data = super().to_dict()
        
        # 转换枚举值
        data['project_type'] = self.project_type.value
        data['training_mode'] = self.training_mode.value
        data['business_type'] = self.business_type.value
        data['status'] = self.status.value
        
        # 转换Decimal类型
        data['accuracy'] = float(self.accuracy) if self.accuracy else 0.0
        data['loss'] = float(self.loss) if self.loss else 0.0
        
        # 添加训练进度
        data['progress'] = self.get_training_progress()
        
        # 添加训练指标（考虑MPC模式）
        data.update(self.get_masked_metrics())
        
        return data
    
    @classmethod
    def get_by_user(cls, user_id, status=None, project_type=None):
        """根据用户ID获取项目列表"""
        query = cls.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        if project_type:
            query = query.filter_by(project_type=project_type)
        
        return query.order_by(cls.updated_at.desc()).all()
    
    @classmethod
    def get_by_business_type(cls, business_type, status=None):
        """根据业务类型获取项目列表"""
        query = cls.query.filter_by(business_type=business_type)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(cls.updated_at.desc()).all()
    
    @classmethod
    def get_running_projects(cls, business_type=None):
        """获取所有运行中的项目"""
        query = cls.query.filter_by(status=ProjectStatus.RUNNING)
        
        if business_type:
            query = query.filter_by(business_type=business_type)
        
        return query.all()
    
    @classmethod
    def create_project(cls, user_id, name, project_type, training_mode, business_type, **kwargs):
        """创建新项目"""
        # 验证用户是否存在
        from .user import User
        user = User.get_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        # 验证业务类型匹配
        if not user.can_access_business_type(business_type):
            raise ValueError("用户无权访问该业务类型")
        
        # 创建项目
        project = cls(user_id=user_id, name=name, project_type=project_type,
                     training_mode=training_mode, business_type=business_type, **kwargs)
        project.save()
        return project
    
    def __repr__(self):
        return f'<Project {self.name} ({self.status.value})>'