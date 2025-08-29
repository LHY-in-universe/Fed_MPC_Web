"""
训练轮次模型
记录联邦学习每轮训练的详细信息
"""

from .base import BaseModel, db
from datetime import datetime
import enum
import json

class RoundStatus(enum.Enum):
    """训练轮次状态枚举"""
    STARTED = 'started'         # 已开始
    IN_PROGRESS = 'in_progress' # 进行中
    COMPLETED = 'completed'     # 已完成
    FAILED = 'failed'          # 失败

class TrainingRound(BaseModel):
    """训练轮次模型"""
    
    __tablename__ = 'training_rounds'
    
    # 关联信息
    session_id = db.Column(db.Integer, db.ForeignKey('training_sessions.id'), nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)
    
    # 轮次信息
    round_number = db.Column(db.Integer, nullable=False, index=True)
    status = db.Column(db.Enum(RoundStatus), default=RoundStatus.STARTED, index=True)
    
    # 时间信息
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Float)  # 持续时间（秒）
    
    # 训练指标
    global_accuracy = db.Column(db.Float, default=0.0)
    global_loss = db.Column(db.Float, default=0.0)
    learning_rate = db.Column(db.Float)
    batch_size = db.Column(db.Integer)
    
    # 参与方信息
    participants_count = db.Column(db.Integer, default=0)
    active_participants = db.Column(db.Integer, default=0)
    participant_metrics = db.Column(db.Text)  # JSON格式的各参与方指标
    
    # 模型聚合信息
    aggregation_method = db.Column(db.String(50), default='fedavg')
    model_weights_hash = db.Column(db.String(64))  # 模型权重哈希值
    
    # 通信统计
    data_uploaded = db.Column(db.BigInteger, default=0)      # 上传数据量（字节）
    data_downloaded = db.Column(db.BigInteger, default=0)    # 下载数据量（字节）
    communication_time = db.Column(db.Float, default=0.0)   # 通信时间（秒）
    
    # 详细日志
    round_logs = db.Column(db.Text)  # JSON格式的轮次日志
    error_details = db.Column(db.Text)  # 错误详情
    
    def __init__(self, session_id, project_id, round_number, **kwargs):
        self.session_id = session_id
        self.project_id = project_id
        self.round_number = round_number
        
        # 设置其他属性
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def start_round(self, learning_rate=None, batch_size=None):
        """开始训练轮次"""
        self.status = RoundStatus.IN_PROGRESS
        self.start_time = datetime.utcnow()
        
        if learning_rate is not None:
            self.learning_rate = learning_rate
        if batch_size is not None:
            self.batch_size = batch_size
        
        self.save()
        
        # 记录开始日志
        self.add_round_log({
            'type': 'round_start',
            'message': f'第 {self.round_number} 轮训练开始',
            'learning_rate': self.learning_rate,
            'batch_size': self.batch_size
        })
    
    def complete_round(self, accuracy=None, loss=None, participant_metrics=None):
        """完成训练轮次"""
        if self.status not in [RoundStatus.STARTED, RoundStatus.IN_PROGRESS]:
            raise ValueError(f"轮次状态 '{self.status.value}' 无法完成")
        
        self.status = RoundStatus.COMPLETED
        self.end_time = datetime.utcnow()
        
        # 计算持续时间
        if self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()
        
        # 更新训练指标
        if accuracy is not None:
            self.global_accuracy = float(accuracy)
        if loss is not None:
            self.global_loss = float(loss)
        
        # 更新参与方指标
        if participant_metrics:
            self.set_participant_metrics(participant_metrics)
            self.active_participants = len(participant_metrics)
        
        self.save()
        
        # 记录完成日志
        self.add_round_log({
            'type': 'round_complete',
            'message': f'第 {self.round_number} 轮训练完成',
            'accuracy': self.global_accuracy,
            'loss': self.global_loss,
            'duration': self.duration,
            'active_participants': self.active_participants
        })
    
    def fail_round(self, error_message, error_details=None):
        """轮次失败"""
        self.status = RoundStatus.FAILED
        self.end_time = datetime.utcnow()
        
        if self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()
        
        self.error_details = error_details or error_message
        self.save()
        
        # 记录失败日志
        self.add_round_log({
            'type': 'round_failed',
            'message': f'第 {self.round_number} 轮训练失败: {error_message}',
            'error_details': error_details
        })
    
    def update_participant_metric(self, participant_id, metrics):
        """更新单个参与方的指标"""
        current_metrics = self.get_participant_metrics()
        current_metrics[str(participant_id)] = {
            'accuracy': metrics.get('accuracy'),
            'loss': metrics.get('loss'),
            'data_size': metrics.get('data_size'),
            'training_time': metrics.get('training_time'),
            'timestamp': datetime.utcnow().isoformat()
        }
        self.set_participant_metrics(current_metrics)
        self.save()
    
    def update_communication_stats(self, uploaded=0, downloaded=0, comm_time=0.0):
        """更新通信统计"""
        self.data_uploaded += uploaded
        self.data_downloaded += downloaded
        self.communication_time += comm_time
        self.save()
    
    def get_participant_metrics(self):
        """获取参与方指标"""
        if not self.participant_metrics:
            return {}
        try:
            return json.loads(self.participant_metrics)
        except json.JSONDecodeError:
            return {}
    
    def set_participant_metrics(self, metrics):
        """设置参与方指标"""
        self.participant_metrics = json.dumps(metrics, ensure_ascii=False)
    
    def get_round_logs(self):
        """获取轮次日志"""
        if not self.round_logs:
            return []
        try:
            return json.loads(self.round_logs)
        except json.JSONDecodeError:
            return []
    
    def add_round_log(self, log_entry):
        """添加轮次日志"""
        logs = self.get_round_logs()
        log_entry['timestamp'] = datetime.utcnow().isoformat()
        log_entry['round_number'] = self.round_number
        logs.append(log_entry)
        
        self.round_logs = json.dumps(logs, ensure_ascii=False)
    
    def get_average_participant_accuracy(self):
        """获取参与方平均准确率"""
        metrics = self.get_participant_metrics()
        if not metrics:
            return 0.0
        
        accuracies = [m.get('accuracy', 0) for m in metrics.values() if m.get('accuracy') is not None]
        return sum(accuracies) / len(accuracies) if accuracies else 0.0
    
    def get_total_data_processed(self):
        """获取总处理数据量"""
        metrics = self.get_participant_metrics()
        if not metrics:
            return 0
        
        return sum(m.get('data_size', 0) for m in metrics.values())
    
    def get_communication_efficiency(self):
        """获取通信效率（数据量/通信时间）"""
        if self.communication_time <= 0:
            return 0.0
        
        total_data = self.data_uploaded + self.data_downloaded
        return total_data / self.communication_time if total_data > 0 else 0.0
    
    def is_completed(self):
        """检查是否已完成"""
        return self.status == RoundStatus.COMPLETED
    
    def is_failed(self):
        """检查是否失败"""
        return self.status == RoundStatus.FAILED
    
    def get_performance_summary(self):
        """获取性能摘要"""
        return {
            'round_number': self.round_number,
            'status': self.status.value,
            'accuracy': self.global_accuracy,
            'loss': self.global_loss,
            'duration': self.duration,
            'participants': self.active_participants,
            'avg_participant_accuracy': self.get_average_participant_accuracy(),
            'data_processed': self.get_total_data_processed(),
            'communication_efficiency': self.get_communication_efficiency()
        }
    
    def to_dict(self, include_logs=False):
        """转换为字典"""
        data = super().to_dict()
        
        # 转换枚举值
        data['status'] = self.status.value if self.status else None
        
        # 添加计算属性
        data['performance_summary'] = self.get_performance_summary()
        data['participant_metrics'] = self.get_participant_metrics()
        
        # 可选包含日志
        if include_logs:
            data['round_logs'] = self.get_round_logs()
        
        return data
    
    @classmethod
    def get_by_session(cls, session_id, round_number=None):
        """根据会话ID获取训练轮次"""
        query = cls.query.filter_by(session_id=session_id)
        
        if round_number is not None:
            query = query.filter_by(round_number=round_number)
            return query.first()
        
        return query.order_by(cls.round_number.asc()).all()
    
    @classmethod
    def get_latest_round(cls, session_id):
        """获取会话的最新轮次"""
        return cls.query.filter_by(session_id=session_id)\
                      .order_by(cls.round_number.desc())\
                      .first()
    
    @classmethod
    def get_completed_rounds(cls, session_id):
        """获取已完成的轮次"""
        return cls.query.filter_by(session_id=session_id, status=RoundStatus.COMPLETED)\
                      .order_by(cls.round_number.asc())\
                      .all()
    
    @classmethod
    def create_round(cls, session_id, project_id, round_number, **kwargs):
        """创建新的训练轮次"""
        # 检查轮次是否已存在
        existing = cls.query.filter_by(session_id=session_id, round_number=round_number).first()
        if existing:
            raise ValueError(f"轮次 {round_number} 已存在")
        
        round_instance = cls(session_id=session_id, project_id=project_id, 
                           round_number=round_number, **kwargs)
        round_instance.save()
        return round_instance
    
    def __repr__(self):
        return f'<TrainingRound {self.round_number} ({self.status.value if self.status else "unknown"})>'