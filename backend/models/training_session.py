"""
训练会话模型
处理联邦学习训练会话的管理
"""

from .base import BaseModel, db, JSONField
import enum
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

class SessionStatus(enum.Enum):
    """会话状态枚举"""
    CREATED = 'created'
    RUNNING = 'running'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    FAILED = 'failed'

class ParticipantStatus(enum.Enum):
    """参与者状态枚举"""
    ONLINE = 'online'
    OFFLINE = 'offline'
    TRAINING = 'training'
    WAITING = 'waiting'
    ERROR = 'error'

class TrainingSession(BaseModel):
    """训练会话模型"""
    
    __tablename__ = 'training_sessions'
    
    # 关联项目
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)
    
    # 会话基本信息
    session_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    training_mode = db.Column(db.String(20), nullable=False)  # normal, mpc
    model_type = db.Column(db.String(50))
    
    # 训练配置
    total_rounds = db.Column(db.Integer, nullable=False)
    current_round = db.Column(db.Integer, default=0)
    participants_count = db.Column(db.Integer, default=0)
    
    # 训练指标
    accuracy = db.Column(db.DECIMAL(5, 4), default=Decimal('0.0000'))
    loss = db.Column(db.DECIMAL(8, 6), default=Decimal('0.000000'))
    
    # 会话状态
    status = db.Column(db.Enum(SessionStatus), default=SessionStatus.CREATED, index=True)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # 配置和元数据
    config = db.Column(db.Text)  # JSON格式的训练配置
    metadata = db.Column(db.Text)  # JSON格式的元数据
    
    # 关联关系
    participants = db.relationship('SessionParticipant', backref='session', 
                                 lazy='dynamic', cascade='all, delete-orphan')
    training_rounds = db.relationship('TrainingRound', backref='session',
                                    lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, project_id, training_mode, total_rounds, **kwargs):
        self.project_id = project_id
        self.session_id = str(uuid.uuid4())
        self.training_mode = training_mode
        self.total_rounds = total_rounds
        
        # 设置其他属性
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def start_session(self):
        """开始训练会话"""
        if self.status != SessionStatus.CREATED:
            raise ValueError("只有创建状态的会话可以开始")
        
        self.status = SessionStatus.RUNNING
        self.started_at = datetime.utcnow()
        self.save()
    
    def pause_session(self):
        """暂停训练会话"""
        if self.status != SessionStatus.RUNNING:
            raise ValueError("只有运行中的会话可以暂停")
        
        self.status = SessionStatus.PAUSED
        self.save()
    
    def resume_session(self):
        """恢复训练会话"""
        if self.status != SessionStatus.PAUSED:
            raise ValueError("只有暂停的会话可以恢复")
        
        self.status = SessionStatus.RUNNING
        self.save()
    
    def complete_session(self):
        """完成训练会话"""
        if self.status not in [SessionStatus.RUNNING, SessionStatus.PAUSED]:
            raise ValueError("只有运行中或暂停的会话可以完成")
        
        self.status = SessionStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.current_round = self.total_rounds
        self.save()
    
    def fail_session(self, reason=None):
        """标记会话失败"""
        self.status = SessionStatus.FAILED
        if reason:
            metadata = JSONField.deserialize(self.metadata) or {}
            metadata['failure_reason'] = reason
            self.metadata = JSONField.serialize(metadata)
        self.save()
    
    def add_participant(self, user_id, node_name=None, node_address=None):
        """添加参与者"""
        # 检查是否已经是参与者
        existing = self.participants.filter_by(user_id=user_id).first()
        if existing:
            return existing
        
        participant = SessionParticipant(
            session_id=self.id,
            user_id=user_id,
            node_name=node_name or f"Node-{user_id}",
            node_address=node_address
        )
        participant.save()
        
        # 更新参与者数量
        self.participants_count = self.participants.count()
        self.save()
        
        return participant
    
    def remove_participant(self, user_id):
        """移除参与者"""
        participant = self.participants.filter_by(user_id=user_id).first()
        if participant:
            participant.delete()
            self.participants_count = self.participants.count()
            self.save()
    
    def get_online_participants(self):
        """获取在线参与者"""
        return self.participants.filter_by(status=ParticipantStatus.ONLINE).all()
    
    def update_round_metrics(self, round_number, accuracy=None, loss=None):
        """更新轮次指标"""
        if accuracy is not None:
            self.accuracy = Decimal(str(accuracy))
        if loss is not None:
            self.loss = Decimal(str(loss))
        
        self.current_round = max(self.current_round, round_number)
        self.save()
    
    def is_ready_to_start(self):
        """检查是否准备好开始"""
        min_participants = 1 if self.training_mode == 'local' else 2
        return self.participants_count >= min_participants
    
    def get_progress(self):
        """获取训练进度"""
        if self.total_rounds == 0:
            return 0.0
        return round((self.current_round / self.total_rounds) * 100, 2)
    
    def to_dict(self, include_participants=True):
        """转换为字典"""
        data = super().to_dict()
        
        # 转换枚举值
        data['status'] = self.status.value
        
        # 转换Decimal类型
        data['accuracy'] = float(self.accuracy) if self.accuracy else 0.0
        data['loss'] = float(self.loss) if self.loss else 0.0
        
        # 添加进度
        data['progress'] = self.get_progress()
        
        # 解析JSON字段
        data['config'] = JSONField.deserialize(self.config)
        data['metadata'] = JSONField.deserialize(self.metadata)
        
        # 包含参与者信息
        if include_participants:
            data['participants'] = [p.to_dict() for p in self.participants]
        
        return data
    
    @classmethod
    def get_by_session_id(cls, session_id):
        """根据会话ID获取会话"""
        return cls.query.filter_by(session_id=session_id).first()
    
    @classmethod
    def get_active_sessions(cls, project_id=None):
        """获取活跃会话"""
        query = cls.query.filter(cls.status.in_([SessionStatus.RUNNING, SessionStatus.PAUSED]))
        if project_id:
            query = query.filter_by(project_id=project_id)
        return query.all()

class SessionParticipant(BaseModel):
    """会话参与者模型"""
    
    __tablename__ = 'session_participants'
    
    # 关联信息
    session_id = db.Column(db.Integer, db.ForeignKey('training_sessions.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # 节点信息
    node_name = db.Column(db.String(100))
    node_address = db.Column(db.String(255))
    status = db.Column(db.Enum(ParticipantStatus), default=ParticipantStatus.OFFLINE, index=True)
    
    # 数据信息
    data_size = db.Column(db.BigInteger, default=0)
    last_heartbeat = db.Column(db.DateTime)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 唯一约束
    __table_args__ = (db.UniqueConstraint('session_id', 'user_id', name='unique_session_user'),)
    
    def update_heartbeat(self):
        """更新心跳"""
        self.last_heartbeat = datetime.utcnow()
        if self.status == ParticipantStatus.OFFLINE:
            self.status = ParticipantStatus.ONLINE
        self.save()
    
    def set_training(self):
        """设置为训练状态"""
        self.status = ParticipantStatus.TRAINING
        self.save()
    
    def set_waiting(self):
        """设置为等待状态"""
        self.status = ParticipantStatus.WAITING
        self.save()
    
    def set_offline(self):
        """设置为离线状态"""
        self.status = ParticipantStatus.OFFLINE
        self.save()
    
    def is_online(self):
        """检查是否在线"""
        if not self.last_heartbeat:
            return False
        
        # 5分钟内有心跳认为在线
        timeout_threshold = datetime.utcnow() - timedelta(minutes=5)
        return self.last_heartbeat > timeout_threshold
    
    def to_dict(self):
        """转换为字典"""
        data = super().to_dict()
        data['status'] = self.status.value
        data['is_online'] = self.is_online()
        return data
    
    def __repr__(self):
        return f'<SessionParticipant {self.node_name} ({self.status.value})>'