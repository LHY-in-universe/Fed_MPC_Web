"""
EdgeAI项目数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import db

class EdgeAIProject(db.Model):
    """EdgeAI项目模型"""
    __tablename__ = 'edgeai_projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, comment='项目名称')
    description = Column(Text, comment='项目描述')
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment='项目所有者ID')
    status = Column(
        Enum('draft', 'active', 'training', 'completed', 'paused', 'error', name='project_status'),
        default='draft',
        comment='项目状态'
    )
    
    # 项目配置
    ai_model_type = Column(String(64), comment='AI模型类型')
    training_strategy = Column(String(64), comment='训练策略')
    max_nodes = Column(Integer, default=50, comment='最大节点数')
    target_accuracy = Column(Integer, default=90, comment='目标准确率(%)')
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    started_at = Column(DateTime, comment='开始训练时间')
    completed_at = Column(DateTime, comment='完成时间')
    
    # 关系
    owner = relationship('User', backref='edgeai_projects')
    edge_nodes = relationship('EdgeNode', backref='project', cascade='all, delete-orphan')
    control_nodes = relationship('ControlNode', backref='project', cascade='all, delete-orphan')
    training_tasks = relationship('TrainingTask', backref='project', cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id,
            'status': self.status,
            'ai_model_type': self.ai_model_type,
            'training_strategy': self.training_strategy,
            'max_nodes': self.max_nodes,
            'target_accuracy': self.target_accuracy,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'node_count': len(self.edge_nodes) if self.edge_nodes else 0,
            'control_node_count': len(self.control_nodes) if self.control_nodes else 0
        }
    
    def get_statistics(self):
        """获取项目统计信息"""
        if not self.edge_nodes:
            return {
                'total_nodes': 0,
                'active_nodes': 0,
                'training_nodes': 0,
                'completed_nodes': 0,
                'error_nodes': 0,
                'avg_progress': 0,
                'total_progress': 0
            }
        
        total_nodes = len(self.edge_nodes)
        active_nodes = len([n for n in self.edge_nodes if n.status == 'online'])
        training_nodes = len([n for n in self.edge_nodes if n.status == 'training'])
        completed_nodes = len([n for n in self.edge_nodes if n.status == 'completed'])
        error_nodes = len([n for n in self.edge_nodes if n.status == 'error'])
        
        total_progress = sum(n.training_progress or 0 for n in self.edge_nodes)
        avg_progress = total_progress / total_nodes if total_nodes > 0 else 0
        
        return {
            'total_nodes': total_nodes,
            'active_nodes': active_nodes,
            'training_nodes': training_nodes,
            'completed_nodes': completed_nodes,
            'error_nodes': error_nodes,
            'avg_progress': round(avg_progress, 1),
            'total_progress': total_progress
        }
    
    def __repr__(self):
        return f'<EdgeAIProject {self.name}>'