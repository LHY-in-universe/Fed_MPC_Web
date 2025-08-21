"""
数据库基础模型
提供公共的数据库操作方法
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class BaseModel(db.Model):
    """基础模型类，提供公共字段和方法"""
    
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def save(self):
        """保存到数据库"""
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def delete(self):
        """从数据库删除"""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def update(self, **kwargs):
        """更新字段"""
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            self.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def to_dict(self, exclude_fields=None):
        """转换为字典"""
        exclude_fields = exclude_fields or []
        result = {}
        
        for column in self.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(self, column.name)
                if isinstance(value, datetime):
                    result[column.name] = value.isoformat()
                elif hasattr(value, '__dict__'):
                    result[column.name] = str(value)
                else:
                    result[column.name] = value
        
        return result
    
    @classmethod
    def get_by_id(cls, id):
        """根据ID获取记录"""
        return cls.query.get(id)
    
    @classmethod
    def get_all(cls, page=1, per_page=20):
        """分页获取所有记录"""
        return cls.query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
    
    @classmethod
    def create(cls, **kwargs):
        """创建新记录"""
        try:
            instance = cls(**kwargs)
            db.session.add(instance)
            db.session.commit()
            return instance
        except Exception as e:
            db.session.rollback()
            raise e

class JSONField:
    """JSON字段处理工具"""
    
    @staticmethod
    def serialize(data):
        """序列化为JSON字符串"""
        if data is None:
            return None
        return json.dumps(data, ensure_ascii=False)
    
    @staticmethod
    def deserialize(json_str):
        """反序列化JSON字符串"""
        if not json_str:
            return None
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            return None