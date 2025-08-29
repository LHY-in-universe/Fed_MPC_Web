"""
数据集模型类
管理训练数据集的存储和元数据
"""

from .base import BaseModel, db
from datetime import datetime
import json


class Dataset(BaseModel):
    """数据集模型"""
    
    __tablename__ = 'datasets'
    
    # 基本信息
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # 数据类型和格式
    data_type = db.Column(db.String(50), nullable=False, index=True)  # image, text, tabular, audio, video, time_series
    file_format = db.Column(db.String(20))  # csv, json, parquet, jpg, png等
    file_path = db.Column(db.String(255))   # 数据文件路径
    
    # 数据统计
    total_samples = db.Column(db.Integer, default=0)      # 总样本数
    feature_count = db.Column(db.Integer, default=0)      # 特征数量
    class_count = db.Column(db.Integer, default=0)        # 类别数量
    file_size = db.Column(db.BigInteger, default=0)       # 文件大小（字节）
    
    # 数据集状态
    status = db.Column(db.String(20), default='created', index=True)  # created, processing, ready, error
    processing_progress = db.Column(db.Integer, default=0)  # 处理进度(0-100)
    error_message = db.Column(db.Text)  # 错误信息
    
    # 数据质量信息
    completeness_score = db.Column(db.Numeric(5, 2))      # 完整性评分
    consistency_score = db.Column(db.Numeric(5, 2))       # 一致性评分
    accuracy_score = db.Column(db.Numeric(5, 2))          # 准确性评分
    uniqueness_score = db.Column(db.Numeric(5, 2))        # 唯一性评分
    
    # 数据划分
    train_split = db.Column(db.Numeric(3, 2), default=0.7)    # 训练集比例
    val_split = db.Column(db.Numeric(3, 2), default=0.15)     # 验证集比例
    test_split = db.Column(db.Numeric(3, 2), default=0.15)    # 测试集比例
    
    # 预处理配置
    preprocessing_config = db.Column(db.JSON, default=dict)   # 预处理配置
    augmentation_config = db.Column(db.JSON, default=dict)    # 数据增强配置
    
    # 元数据和标签
    metadata = db.Column(db.JSON, default=dict)  # 额外元数据
    tags = db.Column(db.JSON, default=list)      # 标签
    
    # 数据模式和结构
    data_schema = db.Column(db.JSON, default=dict)    # 数据模式定义
    column_info = db.Column(db.JSON, default=dict)    # 列信息（表格数据）
    class_distribution = db.Column(db.JSON, default=dict)  # 类别分布
    
    # 访问控制
    is_public = db.Column(db.Boolean, default=False)    # 是否公开
    privacy_level = db.Column(db.String(20), default='private')  # private, shared, public
    
    # 版本控制
    version = db.Column(db.String(20), default='v1.0')
    parent_dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'))  # 父数据集ID（用于版本控制）
    
    # 关联关系
    parent_dataset = db.relationship('Dataset', remote_side='Dataset.id', backref='child_datasets')
    
    def __init__(self, user_id, name, data_type, **kwargs):
        self.user_id = user_id
        self.name = name
        self.data_type = data_type
        
        # 设置其他属性
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def update_statistics(self, total_samples=None, feature_count=None, class_count=None):
        """更新数据集统计信息"""
        if total_samples is not None:
            self.total_samples = total_samples
        if feature_count is not None:
            self.feature_count = feature_count
        if class_count is not None:
            self.class_count = class_count
        self.updated_at = datetime.utcnow()
        self.save()
    
    def update_quality_scores(self, completeness=None, consistency=None, accuracy=None, uniqueness=None):
        """更新数据质量评分"""
        if completeness is not None:
            self.completeness_score = completeness
        if consistency is not None:
            self.consistency_score = consistency
        if accuracy is not None:
            self.accuracy_score = accuracy
        if uniqueness is not None:
            self.uniqueness_score = uniqueness
        self.updated_at = datetime.utcnow()
        self.save()
    
    def set_processing_status(self, status, progress=None, error_message=None):
        """设置处理状态"""
        self.status = status
        if progress is not None:
            self.processing_progress = progress
        if error_message is not None:
            self.error_message = error_message
        self.updated_at = datetime.utcnow()
        self.save()
    
    def set_class_distribution(self, distribution):
        """设置类别分布"""
        self.class_distribution = distribution
        if distribution:
            self.class_count = len(distribution)
        self.save()
    
    def set_data_schema(self, schema):
        """设置数据模式"""
        self.data_schema = schema
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
    
    def get_data_summary(self):
        """获取数据摘要"""
        return {
            'total_samples': self.total_samples,
            'feature_count': self.feature_count,
            'class_count': self.class_count,
            'file_size_mb': round(self.file_size / (1024 * 1024), 2) if self.file_size else 0,
            'data_type': self.data_type,
            'status': self.status,
            'processing_progress': self.processing_progress
        }
    
    def get_quality_summary(self):
        """获取质量摘要"""
        scores = {
            'completeness': float(self.completeness_score) if self.completeness_score else None,
            'consistency': float(self.consistency_score) if self.consistency_score else None,
            'accuracy': float(self.accuracy_score) if self.accuracy_score else None,
            'uniqueness': float(self.uniqueness_score) if self.uniqueness_score else None
        }
        
        # 计算总体质量评分
        valid_scores = [score for score in scores.values() if score is not None]
        overall_score = sum(valid_scores) / len(valid_scores) if valid_scores else None
        
        return {
            'individual_scores': scores,
            'overall_score': overall_score,
            'score_count': len(valid_scores)
        }
    
    def get_split_info(self):
        """获取数据划分信息"""
        return {
            'train_split': float(self.train_split),
            'val_split': float(self.val_split),
            'test_split': float(self.test_split),
            'train_samples': int(self.total_samples * float(self.train_split)) if self.total_samples else 0,
            'val_samples': int(self.total_samples * float(self.val_split)) if self.total_samples else 0,
            'test_samples': int(self.total_samples * float(self.test_split)) if self.total_samples else 0
        }
    
    def is_ready_for_training(self):
        """检查是否准备好用于训练"""
        return (
            self.status == 'ready' and
            self.total_samples > 0 and
            self.feature_count > 0
        )
    
    def validate_splits(self):
        """验证数据划分比例"""
        total = float(self.train_split) + float(self.val_split) + float(self.test_split)
        return abs(total - 1.0) < 0.01  # 允许0.01的误差
    
    def create_version(self, new_name, description=None):
        """创建新版本"""
        new_dataset = Dataset(
            user_id=self.user_id,
            name=new_name,
            data_type=self.data_type,
            description=description or f"{self.name}的新版本",
            parent_dataset_id=self.id,
            version=f"v{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        new_dataset.save()
        return new_dataset
    
    def to_dict(self, include_sensitive=False, include_stats=True):
        """转换为字典"""
        exclude_fields = []
        if not include_sensitive:
            exclude_fields.extend(['file_path', 'error_message'])
        
        data = super().to_dict(exclude_fields=exclude_fields)
        
        # 转换数值字段
        numeric_fields = ['completeness_score', 'consistency_score', 'accuracy_score', 'uniqueness_score',
                         'train_split', 'val_split', 'test_split']
        for field in numeric_fields:
            if data.get(field) is not None:
                data[field] = float(data[field])
        
        # 包含统计信息
        if include_stats:
            data['data_summary'] = self.get_data_summary()
            data['quality_summary'] = self.get_quality_summary()
            data['split_info'] = self.get_split_info()
            data['ready_for_training'] = self.is_ready_for_training()
        
        return data
    
    @classmethod
    def get_by_user(cls, user_id, status=None, data_type=None, limit=None):
        """根据用户获取数据集列表"""
        query = cls.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        if data_type:
            query = query.filter_by(data_type=data_type)
        
        query = query.order_by(cls.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @classmethod
    def get_public_datasets(cls, data_type=None, limit=20):
        """获取公开数据集"""
        query = cls.query.filter_by(is_public=True, status='ready')
        
        if data_type:
            query = query.filter_by(data_type=data_type)
        
        return query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def search_datasets(cls, user_id, keyword=None, data_type=None, status=None):
        """搜索数据集"""
        query = cls.query.filter_by(user_id=user_id)
        
        if keyword:
            query = query.filter(
                db.or_(
                    cls.name.contains(keyword),
                    cls.description.contains(keyword)
                )
            )
        
        if data_type:
            query = query.filter_by(data_type=data_type)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(cls.created_at.desc()).all()
    
    def __repr__(self):
        return f'<Dataset {self.name} ({self.data_type})>'