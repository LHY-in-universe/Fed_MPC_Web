"""
系统日志模型
记录平台的所有操作和事件
"""

from .base import BaseModel, db
from datetime import datetime
import enum
import json

class LogLevel(enum.Enum):
    """日志级别枚举"""
    DEBUG = 'debug'
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    CRITICAL = 'critical'

class LogCategory(enum.Enum):
    """日志分类枚举"""
    AUTH = 'auth'              # 认证相关
    PROJECT = 'project'        # 项目操作
    TRAINING = 'training'      # 训练相关
    SYSTEM = 'system'          # 系统操作
    API = 'api'               # API调用
    SECURITY = 'security'      # 安全事件
    DATA = 'data'             # 数据操作
    CONFIG = 'config'         # 配置变更

class SystemLog(BaseModel):
    """系统日志模型"""
    
    __tablename__ = 'system_logs'
    
    # 基本日志信息
    level = db.Column(db.Enum(LogLevel), nullable=False, index=True)
    category = db.Column(db.Enum(LogCategory), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    
    # 操作信息
    operation = db.Column(db.String(100))  # 具体操作，如 'user_login', 'project_create'
    resource_type = db.Column(db.String(50))  # 资源类型，如 'user', 'project', 'session'
    resource_id = db.Column(db.String(100))   # 资源ID
    
    # 用户信息
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    username = db.Column(db.String(50))       # 冗余存储用户名，防止用户删除后无法追踪
    user_type = db.Column(db.String(20))      # 用户类型
    business_type = db.Column(db.String(20))  # 业务类型
    
    # 请求信息
    ip_address = db.Column(db.String(45))     # 支持IPv6
    user_agent = db.Column(db.String(500))
    request_method = db.Column(db.String(10))  # GET, POST, PUT, DELETE等
    request_path = db.Column(db.String(500))
    request_id = db.Column(db.String(100))    # 用于关联同一请求的多条日志
    
    # 详细信息
    details = db.Column(db.Text)              # JSON格式的详细信息
    error_code = db.Column(db.String(50))     # 错误码
    error_stack = db.Column(db.Text)          # 错误堆栈
    
    # 性能信息
    execution_time = db.Column(db.Float)      # 执行时间（毫秒）
    memory_usage = db.Column(db.BigInteger)   # 内存使用量（字节）
    
    # 索引优化
    __table_args__ = (
        db.Index('idx_logs_time_level', 'created_at', 'level'),
        db.Index('idx_logs_category_operation', 'category', 'operation'),
        db.Index('idx_logs_user_time', 'user_id', 'created_at'),
        db.Index('idx_logs_resource', 'resource_type', 'resource_id'),
    )
    
    def __init__(self, level, category, message, **kwargs):
        self.level = level if isinstance(level, LogLevel) else LogLevel(level)
        self.category = category if isinstance(category, LogCategory) else LogCategory(category)
        self.message = message
        
        # 设置其他属性
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get_details(self):
        """获取详细信息"""
        if not self.details:
            return {}
        try:
            return json.loads(self.details)
        except json.JSONDecodeError:
            return {}
    
    def set_details(self, details):
        """设置详细信息"""
        if isinstance(details, dict):
            self.details = json.dumps(details, ensure_ascii=False)
        else:
            self.details = str(details)
    
    def add_detail(self, key, value):
        """添加详细信息"""
        details = self.get_details()
        details[key] = value
        self.set_details(details)
    
    def is_error(self):
        """是否为错误日志"""
        return self.level in [LogLevel.ERROR, LogLevel.CRITICAL]
    
    def is_security_event(self):
        """是否为安全事件"""
        return self.category == LogCategory.SECURITY or self.level == LogLevel.CRITICAL
    
    def get_formatted_message(self):
        """获取格式化的消息"""
        timestamp = self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        level = self.level.value.upper()
        category = self.category.value.upper()
        user_info = f"[{self.username}]" if self.username else "[System]"
        
        return f"[{timestamp}] {level} {category} {user_info}: {self.message}"
    
    def to_dict(self, include_sensitive=False):
        """转换为字典"""
        data = super().to_dict()
        
        # 转换枚举值
        data['level'] = self.level.value if self.level else None
        data['category'] = self.category.value if self.category else None
        
        # 添加解析的详细信息
        data['details'] = self.get_details()
        data['formatted_message'] = self.get_formatted_message()
        data['is_error'] = self.is_error()
        data['is_security_event'] = self.is_security_event()
        
        # 敏感信息只在需要时包含
        if not include_sensitive:
            # 移除可能包含敏感信息的字段
            data.pop('error_stack', None)
            data.pop('user_agent', None)
            # 只显示IP的前几位
            if self.ip_address:
                ip_parts = self.ip_address.split('.')
                if len(ip_parts) == 4:
                    data['ip_address'] = f"{ip_parts[0]}.{ip_parts[1]}.*.{ip_parts[3]}"
        
        return data
    
    @classmethod
    def log(cls, level, category, message, user_id=None, operation=None, 
            resource_type=None, resource_id=None, **kwargs):
        """记录日志的便捷方法"""
        log_entry = cls(
            level=level,
            category=category,
            message=message,
            user_id=user_id,
            operation=operation,
            resource_type=resource_type,
            resource_id=resource_id,
            **kwargs
        )
        
        # 如果提供了用户ID，获取用户信息
        if user_id:
            from .user import User
            user = User.get_by_id(user_id)
            if user:
                log_entry.username = user.username
                log_entry.user_type = user.user_type.value
                log_entry.business_type = user.business_type.value
        
        log_entry.save()
        return log_entry
    
    @classmethod
    def log_info(cls, category, message, **kwargs):
        """记录信息日志"""
        return cls.log(LogLevel.INFO, category, message, **kwargs)
    
    @classmethod
    def log_warning(cls, category, message, **kwargs):
        """记录警告日志"""
        return cls.log(LogLevel.WARNING, category, message, **kwargs)
    
    @classmethod
    def log_error(cls, category, message, **kwargs):
        """记录错误日志"""
        return cls.log(LogLevel.ERROR, category, message, **kwargs)
    
    @classmethod
    def log_critical(cls, category, message, **kwargs):
        """记录严重日志"""
        return cls.log(LogLevel.CRITICAL, category, message, **kwargs)
    
    @classmethod
    def log_auth(cls, operation, message, user_id=None, ip_address=None, **kwargs):
        """记录认证相关日志"""
        return cls.log(
            LogLevel.INFO, LogCategory.AUTH, message,
            user_id=user_id, operation=operation, 
            ip_address=ip_address, **kwargs
        )
    
    @classmethod
    def log_security(cls, message, level=LogLevel.WARNING, user_id=None, 
                    ip_address=None, **kwargs):
        """记录安全相关日志"""
        return cls.log(
            level, LogCategory.SECURITY, message,
            user_id=user_id, ip_address=ip_address, **kwargs
        )
    
    @classmethod
    def log_api(cls, method, path, user_id=None, ip_address=None, 
               execution_time=None, **kwargs):
        """记录API调用日志"""
        message = f"{method} {path}"
        return cls.log(
            LogLevel.INFO, LogCategory.API, message,
            user_id=user_id, ip_address=ip_address,
            request_method=method, request_path=path,
            execution_time=execution_time, **kwargs
        )
    
    @classmethod
    def get_by_category(cls, category, limit=100):
        """根据分类获取日志"""
        return cls.query.filter_by(category=category)\
                      .order_by(cls.created_at.desc())\
                      .limit(limit).all()
    
    @classmethod
    def get_by_level(cls, level, limit=100):
        """根据级别获取日志"""
        return cls.query.filter_by(level=level)\
                      .order_by(cls.created_at.desc())\
                      .limit(limit).all()
    
    @classmethod
    def get_by_user(cls, user_id, limit=100):
        """根据用户获取日志"""
        return cls.query.filter_by(user_id=user_id)\
                      .order_by(cls.created_at.desc())\
                      .limit(limit).all()
    
    @classmethod
    def get_error_logs(cls, hours=24, limit=100):
        """获取错误日志"""
        from datetime import datetime, timedelta
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        return cls.query.filter(
            cls.level.in_([LogLevel.ERROR, LogLevel.CRITICAL]),
            cls.created_at >= time_threshold
        ).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_security_logs(cls, hours=24, limit=100):
        """获取安全日志"""
        from datetime import datetime, timedelta
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        return cls.query.filter(
            cls.category == LogCategory.SECURITY,
            cls.created_at >= time_threshold
        ).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_recent_activity(cls, user_id=None, hours=24, limit=50):
        """获取最近活动"""
        from datetime import datetime, timedelta
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        query = cls.query.filter(cls.created_at >= time_threshold)
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        return query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def cleanup_old_logs(cls, days=90):
        """清理旧日志"""
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # 保留错误和安全日志更长时间
        critical_cutoff = datetime.utcnow() - timedelta(days=days*2)
        
        # 删除普通日志
        normal_logs = cls.query.filter(
            cls.created_at < cutoff_date,
            cls.level.in_([LogLevel.DEBUG, LogLevel.INFO]),
            cls.category != LogCategory.SECURITY
        )
        normal_count = normal_logs.count()
        normal_logs.delete()
        
        # 删除旧的错误和安全日志
        critical_logs = cls.query.filter(
            cls.created_at < critical_cutoff,
            cls.level.in_([LogLevel.ERROR, LogLevel.CRITICAL, LogLevel.WARNING])
        )
        critical_count = critical_logs.count()
        critical_logs.delete()
        
        db.session.commit()
        return normal_count + critical_count
    
    def __repr__(self):
        return f'<SystemLog {self.level.value if self.level else "unknown"} {self.category.value if self.category else "unknown"}>'