"""
训练任务数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import db

class TrainingTask(db.Model):
    """训练任务模型"""
    __tablename__ = 'edgeai_training_tasks'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, comment='任务名称')
    description = Column(Text, comment='任务描述')
    
    # 关联关系
    project_id = Column(Integer, ForeignKey('edgeai_projects.id'), nullable=False, comment='所属项目ID')
    edge_node_id = Column(Integer, ForeignKey('edgeai_edge_nodes.id'), nullable=False, comment='执行节点ID')
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False, comment='创建者ID')
    
    # 任务状态
    status = Column(
        Enum('pending', 'running', 'paused', 'completed', 'failed', 'cancelled', name='training_task_status'),
        default='pending',
        comment='任务状态'
    )
    
    # 训练配置
    model_config = Column(JSON, comment='模型配置JSON')
    hyperparameters = Column(JSON, comment='超参数JSON') 
    dataset_config = Column(JSON, comment='数据集配置JSON')
    
    # 训练进度
    progress = Column(Integer, default=0, comment='训练进度(0-100)')
    current_epoch = Column(Integer, default=0, comment='当前轮次')
    total_epochs = Column(Integer, default=100, comment='总轮次')
    
    # 训练指标
    accuracy = Column(Float, comment='准确率')
    loss = Column(Float, comment='损失值')
    f1_score = Column(Float, comment='F1分数')
    precision = Column(Float, comment='精确率')
    recall = Column(Float, comment='召回率')
    
    # 资源使用情况
    cpu_usage = Column(Float, comment='CPU使用率(%)')
    memory_usage = Column(Float, comment='内存使用率(%)')
    gpu_usage = Column(Float, comment='GPU使用率(%)')
    
    # 时间信息
    estimated_time = Column(Integer, comment='预估时间(秒)')
    elapsed_time = Column(Integer, default=0, comment='已用时间(秒)')
    remaining_time = Column(Integer, comment='剩余时间(秒)')
    
    # 错误信息
    error_message = Column(Text, comment='错误信息')
    error_code = Column(String(32), comment='错误代码')
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    started_at = Column(DateTime, comment='开始时间')
    completed_at = Column(DateTime, comment='完成时间')
    
    # 关系
    creator = relationship('User', backref='training_tasks')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'project_id': self.project_id,
            'edge_node_id': self.edge_node_id,
            'created_by': self.created_by,
            'status': self.status,
            'model_config': self.model_config or {},
            'hyperparameters': self.hyperparameters or {},
            'dataset_config': self.dataset_config or {},
            'progress': self.progress,
            'current_epoch': self.current_epoch,
            'total_epochs': self.total_epochs,
            'accuracy': self.accuracy,
            'loss': self.loss,
            'f1_score': self.f1_score,
            'precision': self.precision,
            'recall': self.recall,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'gpu_usage': self.gpu_usage,
            'estimated_time': self.estimated_time,
            'elapsed_time': self.elapsed_time,
            'remaining_time': self.remaining_time,
            'error_message': self.error_message,
            'error_code': self.error_code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'creator_name': self.creator.username if self.creator else None,
            'edge_node_name': self.edge_node.name if self.edge_node else None,
            'is_running': self.status == 'running',
            'duration': self.get_duration()
        }
    
    def start_task(self):
        """开始任务"""
        self.status = 'running'
        self.started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def pause_task(self):
        """暂停任务"""
        if self.status == 'running':
            self.status = 'paused'
            self.updated_at = datetime.utcnow()
    
    def resume_task(self):
        """恢复任务"""
        if self.status == 'paused':
            self.status = 'running'
            self.updated_at = datetime.utcnow()
    
    def complete_task(self):
        """完成任务"""
        self.status = 'completed'
        self.progress = 100
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        if self.started_at:
            self.elapsed_time = int((self.completed_at - self.started_at).total_seconds())
    
    def fail_task(self, error_message, error_code=None):
        """任务失败"""
        self.status = 'failed'
        self.error_message = error_message
        self.error_code = error_code
        self.updated_at = datetime.utcnow()
    
    def cancel_task(self):
        """取消任务"""
        self.status = 'cancelled'
        self.updated_at = datetime.utcnow()
    
    def update_progress(self, progress, epoch=None, metrics=None):
        """更新训练进度"""
        self.progress = min(100, max(0, progress))
        if epoch is not None:
            self.current_epoch = epoch
        
        if metrics:
            self.accuracy = metrics.get('accuracy', self.accuracy)
            self.loss = metrics.get('loss', self.loss)
            self.f1_score = metrics.get('f1_score', self.f1_score)
            self.precision = metrics.get('precision', self.precision)
            self.recall = metrics.get('recall', self.recall)
        
        self.updated_at = datetime.utcnow()
        
        # 计算剩余时间
        if self.started_at and self.progress > 0:
            elapsed = (datetime.utcnow() - self.started_at).total_seconds()
            self.elapsed_time = int(elapsed)
            if self.progress < 100:
                estimated_total = elapsed * 100 / self.progress
                self.remaining_time = int(estimated_total - elapsed)
    
    def update_resource_usage(self, cpu=None, memory=None, gpu=None):
        """更新资源使用情况"""
        if cpu is not None:
            self.cpu_usage = cpu
        if memory is not None:
            self.memory_usage = memory
        if gpu is not None:
            self.gpu_usage = gpu
        self.updated_at = datetime.utcnow()
    
    def get_duration(self):
        """获取任务持续时间（秒）"""
        if not self.started_at:
            return 0
        
        end_time = self.completed_at if self.completed_at else datetime.utcnow()
        return int((end_time - self.started_at).total_seconds())
    
    def get_metrics_summary(self):
        """获取指标摘要"""
        metrics = {}
        if self.accuracy is not None:
            metrics['accuracy'] = f"{self.accuracy:.2%}"
        if self.loss is not None:
            metrics['loss'] = f"{self.loss:.4f}"
        if self.f1_score is not None:
            metrics['f1_score'] = f"{self.f1_score:.3f}"
        if self.precision is not None:
            metrics['precision'] = f"{self.precision:.3f}"
        if self.recall is not None:
            metrics['recall'] = f"{self.recall:.3f}"
        return metrics
    
    def __repr__(self):
        return f'<TrainingTask {self.name} ({self.status})>'