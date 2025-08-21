"""
系统配置模型
管理平台的系统配置参数
"""

from .base import BaseModel, db
from datetime import datetime
import json

class SystemConfig(BaseModel):
    """系统配置模型"""
    
    __tablename__ = 'system_configs'
    
    # 配置信息
    config_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    config_value = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(255))
    config_type = db.Column(db.String(50), default='string')  # string, int, float, bool, json
    is_public = db.Column(db.Boolean, default=False)  # 是否允许客户端访问
    is_readonly = db.Column(db.Boolean, default=False)  # 是否只读
    
    # 版本控制
    version = db.Column(db.Integer, default=1)
    last_modified_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __init__(self, config_key, config_value, **kwargs):
        self.config_key = config_key
        self.config_value = str(config_value)
        
        # 设置其他属性
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get_value(self, default=None):
        """获取配置值，根据类型自动转换"""
        if not self.config_value:
            return default
            
        try:
            if self.config_type == 'int':
                return int(self.config_value)
            elif self.config_type == 'float':
                return float(self.config_value)
            elif self.config_type == 'bool':
                return self.config_value.lower() in ('true', '1', 'yes', 'on')
            elif self.config_type == 'json':
                return json.loads(self.config_value)
            else:
                return self.config_value
        except (ValueError, json.JSONDecodeError):
            return default
    
    def set_value(self, value, user_id=None):
        """设置配置值"""
        if self.is_readonly:
            raise ValueError(f"配置项 '{self.config_key}' 为只读配置")
        
        # 根据类型验证和转换值
        if self.config_type == 'json':
            if not isinstance(value, (dict, list, str)):
                raise ValueError("JSON配置值必须是字典、列表或JSON字符串")
            if isinstance(value, str):
                json.loads(value)  # 验证JSON格式
                self.config_value = value
            else:
                self.config_value = json.dumps(value, ensure_ascii=False)
        elif self.config_type == 'bool':
            if isinstance(value, bool):
                self.config_value = str(value).lower()
            else:
                self.config_value = str(value).lower()
        else:
            self.config_value = str(value)
        
        # 更新版本和修改者
        self.version += 1
        if user_id:
            self.last_modified_by = user_id
        
        self.save()
    
    def to_dict(self, include_value=True):
        """转换为字典"""
        data = super().to_dict()
        
        if include_value:
            data['parsed_value'] = self.get_value()
        else:
            data.pop('config_value', None)
            
        return data
    
    @classmethod
    def get_config(cls, key, default=None):
        """获取配置值的便捷方法"""
        config = cls.query.filter_by(config_key=key).first()
        return config.get_value(default) if config else default
    
    @classmethod
    def set_config(cls, key, value, description=None, config_type='string', user_id=None, **kwargs):
        """设置配置值的便捷方法"""
        config = cls.query.filter_by(config_key=key).first()
        
        if config:
            config.set_value(value, user_id)
        else:
            # 创建新配置
            config = cls(
                config_key=key,
                config_value=str(value),
                description=description,
                config_type=config_type,
                last_modified_by=user_id,
                **kwargs
            )
            config.save()
        
        return config
    
    @classmethod
    def get_public_configs(cls):
        """获取所有公开配置"""
        configs = cls.query.filter_by(is_public=True).all()
        return {config.config_key: config.get_value() for config in configs}
    
    @classmethod
    def get_configs_by_prefix(cls, prefix):
        """根据前缀获取配置"""
        configs = cls.query.filter(cls.config_key.like(f'{prefix}%')).all()
        return {config.config_key: config.get_value() for config in configs}
    
    @classmethod
    def bulk_set_configs(cls, config_dict, user_id=None):
        """批量设置配置"""
        results = {}
        
        for key, value in config_dict.items():
            try:
                config = cls.set_config(key, value, user_id=user_id)
                results[key] = {'success': True, 'config_id': config.id}
            except Exception as e:
                results[key] = {'success': False, 'error': str(e)}
        
        return results
    
    def __repr__(self):
        return f'<SystemConfig {self.config_key}={self.config_value}>'