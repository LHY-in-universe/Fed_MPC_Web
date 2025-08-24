"""
AI模型模型类
管理AI模型的定义、配置和状态
"""

from .base import BaseModel, db
from datetime import datetime
import json


class Model(BaseModel):
    """AI模型模型"""
    
    __tablename__ = 'models'
    
    # 基本信息
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # 模型配置
    model_type = db.Column(db.String(50), nullable=False, index=True)  # cnn, rnn, lstm, transformer等
    architecture = db.Column(db.String(100), nullable=False)  # ResNet, LSTM, Transformer等
    hyperparameters = db.Column(db.JSON, default=dict)  # 超参数配置
    
    # 模型状态
    status = db.Column(db.String(20), default='created', index=True)  # created, training, trained, deployed, error
    version = db.Column(db.String(20), default='v1.0')
    
    # 性能指标
    accuracy = db.Column(db.Numeric(5, 4), default=0.0)  # 准确率
    loss = db.Column(db.Numeric(10, 6), default=0.0)    # 损失值
    precision = db.Column(db.Numeric(5, 4))             # 精确率
    recall = db.Column(db.Numeric(5, 4))                # 召回率
    f1_score = db.Column(db.Numeric(5, 4))              # F1分数
    
    # 文件存储
    model_path = db.Column(db.String(255))  # 模型文件路径
    weights_path = db.Column(db.String(255))  # 权重文件路径
    config_path = db.Column(db.String(255))   # 配置文件路径
    
    # 模型信息
    input_shape = db.Column(db.JSON)  # 输入形状
    output_shape = db.Column(db.JSON)  # 输出形状
    model_size = db.Column(db.BigInteger)  # 模型大小（字节）
    parameter_count = db.Column(db.Integer)  # 参数数量
    
    # 训练信息
    training_dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'))
    training_start_time = db.Column(db.DateTime)
    training_end_time = db.Column(db.DateTime)
    training_duration = db.Column(db.Integer)  # 训练时长（秒）
    
    # 部署信息
    deployment_status = db.Column(db.String(20), default='not_deployed')  # not_deployed, deploying, deployed, failed
    deployment_url = db.Column(db.String(255))  # 部署URL
    deployment_config = db.Column(db.JSON, default=dict)  # 部署配置
    
    # 元数据
    metadata = db.Column(db.JSON, default=dict)  # 额外元数据
    tags = db.Column(db.JSON, default=list)  # 标签
    
    # 关联关系
    training_sessions = db.relationship('TrainingSession', backref='model', lazy='dynamic', cascade='all, delete-orphan')
    training_dataset = db.relationship('Dataset', backref='trained_models', lazy='select')
    
    def __init__(self, user_id, name, model_type, architecture, **kwargs):
        self.user_id = user_id
        self.name = name
        self.model_type = model_type
        self.architecture = architecture
        
        # 设置其他属性
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def update_metrics(self, accuracy=None, loss=None, precision=None, recall=None, f1_score=None):
        """更新模型性能指标"""
        if accuracy is not None:
            self.accuracy = accuracy
        if loss is not None:
            self.loss = loss
        if precision is not None:
            self.precision = precision
        if recall is not None:
            self.recall = recall
        if f1_score is not None:
            self.f1_score = f1_score
        self.updated_at = datetime.utcnow()
        self.save()
    
    def start_training(self, dataset_id=None):
        """开始训练"""
        self.status = 'training'
        self.training_start_time = datetime.utcnow()
        if dataset_id:
            self.training_dataset_id = dataset_id
        self.save()
    
    def complete_training(self, final_accuracy=None, final_loss=None):
        """完成训练"""
        self.status = 'trained'
        self.training_end_time = datetime.utcnow()
        
        if self.training_start_time:
            duration = self.training_end_time - self.training_start_time
            self.training_duration = int(duration.total_seconds())
        
        if final_accuracy is not None:
            self.accuracy = final_accuracy
        if final_loss is not None:
            self.loss = final_loss
        
        self.save()
    
    def deploy(self, deployment_url=None, config=None):
        """部署模型"""
        self.deployment_status = 'deploying'
        if deployment_url:
            self.deployment_url = deployment_url
        if config:
            self.deployment_config = config
        self.save()
    
    def complete_deployment(self, success=True):
        """完成部署"""
        self.deployment_status = 'deployed' if success else 'failed'
        self.save()
    
    def add_tag(self, tag):
        """添加标签"""
        if not self.tags:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)
            self.save()
    
    def remove_tag(self, tag):
        """移除标签"""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
            self.save()
    
    def get_training_history(self, limit=10):
        """获取训练历史"""
        return self.training_sessions.order_by(
            db.desc('created_at')
        ).limit(limit).all()
    
    def calculate_model_complexity(self):
        """计算模型复杂度"""
        if self.parameter_count and self.model_size:
            return {
                'parameter_count': self.parameter_count,
                'model_size_mb': round(self.model_size / (1024 * 1024), 2),
                'complexity_score': min(100, (self.parameter_count / 1000000) * 10)  # 简单的复杂度评分
            }
        return None
    
    def get_performance_summary(self):
        """获取性能摘要"""
        return {
            'accuracy': float(self.accuracy) if self.accuracy else 0.0,
            'loss': float(self.loss) if self.loss else 0.0,
            'precision': float(self.precision) if self.precision else None,
            'recall': float(self.recall) if self.recall else None,
            'f1_score': float(self.f1_score) if self.f1_score else None,
            'status': self.status,
            'training_duration': self.training_duration
        }
    
    def to_dict(self, include_sensitive=False, include_relations=False):
        """转换为字典"""
        exclude_fields = []
        if not include_sensitive:
            exclude_fields.extend(['model_path', 'weights_path', 'config_path'])
        
        data = super().to_dict(exclude_fields=exclude_fields)
        
        # 转换数值字段
        numeric_fields = ['accuracy', 'loss', 'precision', 'recall', 'f1_score']
        for field in numeric_fields:
            if data.get(field) is not None:
                data[field] = float(data[field])
        
        # 添加性能摘要
        data['performance_summary'] = self.get_performance_summary()
        
        # 添加复杂度信息
        complexity = self.calculate_model_complexity()
        if complexity:
            data['complexity'] = complexity
        
        # 包含关联关系
        if include_relations:
            data['training_sessions_count'] = self.training_sessions.count()
            if self.training_dataset:
                data['training_dataset'] = {
                    'id': self.training_dataset.id,
                    'name': self.training_dataset.name,
                    'data_type': self.training_dataset.data_type
                }
        
        return data
    
    @classmethod
    def get_by_user(cls, user_id, status=None, model_type=None, limit=None):
        """根据用户获取模型列表"""
        query = cls.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        if model_type:
            query = query.filter_by(model_type=model_type)
        
        query = query.order_by(cls.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @classmethod
    def get_by_status(cls, status):
        """根据状态获取模型"""
        return cls.query.filter_by(status=status).all()
    
    @classmethod
    def search_models(cls, user_id, keyword=None, model_type=None, status=None):
        """搜索模型"""
        query = cls.query.filter_by(user_id=user_id)
        
        if keyword:
            query = query.filter(
                db.or_(
                    cls.name.contains(keyword),
                    cls.description.contains(keyword)
                )
            )
        
        if model_type:
            query = query.filter_by(model_type=model_type)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(cls.created_at.desc()).all()
    
    def __repr__(self):
        return f'<Model {self.name} ({self.model_type})>'