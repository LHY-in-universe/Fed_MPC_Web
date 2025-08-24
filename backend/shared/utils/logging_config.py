"""
统一日志配置系统
支持结构化日志、多输出目标、日志轮转
"""

import logging
import logging.handlers
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False

class JSONFormatter(logging.Formatter):
    """JSON格式化器"""
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为JSON"""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'thread_name': record.threadName,
            'process': record.process,
            'process_name': record.processName,
        }
        
        # 添加异常信息
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # 添加额外字段
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'business_type'):
            log_entry['business_type'] = record.business_type
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'duration'):
            log_entry['duration'] = record.duration
        if hasattr(record, 'status_code'):
            log_entry['status_code'] = record.status_code
        
        return json.dumps(log_entry, ensure_ascii=False)

class CustomFormatter(logging.Formatter):
    """自定义文本格式化器"""
    
    def __init__(self):
        super().__init__()
        
        # 不同级别的颜色
        self.COLORS = {
            'DEBUG': '\033[36m',     # 青色
            'INFO': '\033[32m',      # 绿色
            'WARNING': '\033[33m',   # 黄色
            'ERROR': '\033[31m',     # 红色
            'CRITICAL': '\033[35m',  # 紫色
            'RESET': '\033[0m'       # 重置
        }
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录"""
        # 基础格式
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        level = record.levelname
        logger_name = record.name
        message = record.getMessage()
        
        # 添加颜色（如果支持）
        if hasattr(record, 'no_color') and record.no_color:
            color_start = color_end = ''
        else:
            color_start = self.COLORS.get(level, '')
            color_end = self.COLORS['RESET']
        
        # 构建日志行
        log_line = f"{timestamp} [{color_start}{level:<8}{color_end}] {logger_name}: {message}"
        
        # 添加上下文信息
        context_parts = []
        if hasattr(record, 'user_id'):
            context_parts.append(f"user={record.user_id}")
        if hasattr(record, 'business_type'):
            context_parts.append(f"business={record.business_type}")
        if hasattr(record, 'request_id'):
            context_parts.append(f"request={record.request_id}")
        if hasattr(record, 'duration'):
            context_parts.append(f"duration={record.duration:.3f}s")
        
        if context_parts:
            log_line += f" [{', '.join(context_parts)}]"
        
        # 添加异常信息
        if record.exc_info:
            log_line += '\n' + self.formatException(record.exc_info)
        
        return log_line

class LoggingConfig:
    """日志配置管理器"""
    
    def __init__(self, app_name: str = "fed_mpc_web", log_dir: str = "./logs"):
        self.app_name = app_name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 日志级别映射
        self.LEVELS = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
    
    def setup_logging(self, config: Dict[str, Any] = None):
        """设置日志系统"""
        if config is None:
            config = self._get_default_config()
        
        # 清理现有处理器
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # 设置根日志级别
        root_level = config.get('level', 'INFO')
        root_logger.setLevel(self.LEVELS[root_level])
        
        # 创建处理器
        handlers = self._create_handlers(config.get('handlers', {}))
        
        # 添加处理器到根日志器
        for handler in handlers:
            root_logger.addHandler(handler)
        
        # 设置特定日志器
        loggers_config = config.get('loggers', {})
        for logger_name, logger_config in loggers_config.items():
            logger = logging.getLogger(logger_name)
            logger.setLevel(self.LEVELS[logger_config.get('level', root_level)])
            
            # 是否禁用传播到根日志器
            if not logger_config.get('propagate', True):
                logger.propagate = False
                
                # 为该日志器添加特定处理器
                logger_handlers = self._create_handlers(logger_config.get('handlers', {}))
                for handler in logger_handlers:
                    logger.addHandler(handler)
        
        # 设置第三方库日志级别
        self._configure_third_party_loggers()
        
        # 如果可用，配置structlog
        if STRUCTLOG_AVAILABLE:
            self._configure_structlog()
        
        logging.info(f"{self.app_name} 日志系统初始化完成")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认日志配置"""
        return {
            'level': os.environ.get('LOG_LEVEL', 'INFO'),
            'handlers': {
                'console': {
                    'class': 'StreamHandler',
                    'level': 'INFO',
                    'format': 'text',
                    'stream': 'stdout'
                },
                'file': {
                    'class': 'RotatingFileHandler',
                    'level': 'DEBUG',
                    'format': 'json',
                    'filename': self.log_dir / f'{self.app_name}.log',
                    'max_bytes': 100 * 1024 * 1024,  # 100MB
                    'backup_count': 10
                },
                'error_file': {
                    'class': 'RotatingFileHandler',
                    'level': 'ERROR',
                    'format': 'json',
                    'filename': self.log_dir / f'{self.app_name}_error.log',
                    'max_bytes': 50 * 1024 * 1024,  # 50MB
                    'backup_count': 5
                }
            },
            'loggers': {
                'werkzeug': {'level': 'WARNING'},
                'urllib3': {'level': 'WARNING'},
                'requests': {'level': 'WARNING'},
                'sqlalchemy.engine': {'level': 'WARNING'},
                'sqlalchemy.pool': {'level': 'WARNING'}
            }
        }
    
    def _create_handlers(self, handlers_config: Dict[str, Any]) -> list:
        """创建日志处理器"""
        handlers = []
        
        for handler_name, handler_config in handlers_config.items():
            handler = None
            handler_class = handler_config.get('class', 'StreamHandler')
            
            try:
                # 控制台处理器
                if handler_class == 'StreamHandler':
                    import sys
                    stream = sys.stdout if handler_config.get('stream') == 'stdout' else sys.stderr
                    handler = logging.StreamHandler(stream)
                
                # 文件处理器
                elif handler_class == 'FileHandler':
                    handler = logging.FileHandler(
                        handler_config['filename'],
                        encoding='utf-8'
                    )
                
                # 轮转文件处理器
                elif handler_class == 'RotatingFileHandler':
                    handler = logging.handlers.RotatingFileHandler(
                        handler_config['filename'],
                        maxBytes=handler_config.get('max_bytes', 100 * 1024 * 1024),
                        backupCount=handler_config.get('backup_count', 10),
                        encoding='utf-8'
                    )
                
                # 时间轮转文件处理器
                elif handler_class == 'TimedRotatingFileHandler':
                    handler = logging.handlers.TimedRotatingFileHandler(
                        handler_config['filename'],
                        when=handler_config.get('when', 'midnight'),
                        interval=handler_config.get('interval', 1),
                        backupCount=handler_config.get('backup_count', 30),
                        encoding='utf-8'
                    )
                
                # Syslog处理器
                elif handler_class == 'SysLogHandler':
                    handler = logging.handlers.SysLogHandler(
                        address=handler_config.get('address', '/dev/log')
                    )
                
                if handler:
                    # 设置级别
                    level = handler_config.get('level', 'INFO')
                    handler.setLevel(self.LEVELS[level])
                    
                    # 设置格式化器
                    format_type = handler_config.get('format', 'text')
                    if format_type == 'json':
                        formatter = JSONFormatter()
                    else:
                        formatter = CustomFormatter()
                    
                    handler.setFormatter(formatter)
                    handlers.append(handler)
                    
            except Exception as e:
                print(f"创建日志处理器 {handler_name} 失败: {e}")
        
        return handlers
    
    def _configure_third_party_loggers(self):
        """配置第三方库日志"""
        # SQLAlchemy
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
        logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
        
        # Requests
        logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
        logging.getLogger('requests.packages.urllib3').setLevel(logging.WARNING)
        
        # Werkzeug
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    def _configure_structlog(self):
        """配置structlog（如果可用）"""
        try:
            structlog.configure(
                processors=[
                    structlog.stdlib.filter_by_level,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.processors.TimeStamper(fmt="ISO"),
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    structlog.processors.UnicodeDecoder(),
                    structlog.processors.JSONRenderer()
                ],
                context_class=dict,
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )
        except Exception as e:
            logging.warning(f"配置structlog失败: {e}")

class RequestLogger:
    """请求日志记录器"""
    
    def __init__(self, logger_name: str = "fed_mpc_web.requests"):
        self.logger = logging.getLogger(logger_name)
    
    def log_request(self, request, response, duration: float, user_id: str = None,
                   business_type: str = None, request_id: str = None):
        """记录HTTP请求"""
        extra = {
            'user_id': user_id,
            'business_type': business_type,
            'request_id': request_id,
            'duration': duration,
            'status_code': response.status_code,
            'no_color': True  # 文件日志不需要颜色
        }
        
        self.logger.info(
            f"{request.method} {request.path} -> {response.status_code} ({duration:.3f}s)",
            extra=extra
        )
    
    def log_error(self, request, error, user_id: str = None, business_type: str = None,
                 request_id: str = None):
        """记录请求错误"""
        extra = {
            'user_id': user_id,
            'business_type': business_type,
            'request_id': request_id,
            'no_color': True
        }
        
        self.logger.error(
            f"{request.method} {request.path} -> ERROR: {error}",
            extra=extra,
            exc_info=True
        )

class SecurityLogger:
    """安全事件日志记录器"""
    
    def __init__(self, logger_name: str = "fed_mpc_web.security"):
        self.logger = logging.getLogger(logger_name)
    
    def log_login_attempt(self, user_id: str, success: bool, ip_address: str,
                         business_type: str = None):
        """记录登录尝试"""
        status = "SUCCESS" if success else "FAILED"
        extra = {
            'user_id': user_id,
            'business_type': business_type,
            'ip_address': ip_address,
            'security_event': 'login_attempt',
            'no_color': True
        }
        
        if success:
            self.logger.info(f"Login {status}: {user_id} from {ip_address}", extra=extra)
        else:
            self.logger.warning(f"Login {status}: {user_id} from {ip_address}", extra=extra)
    
    def log_permission_denied(self, user_id: str, resource: str, ip_address: str):
        """记录权限拒绝"""
        extra = {
            'user_id': user_id,
            'ip_address': ip_address,
            'security_event': 'permission_denied',
            'resource': resource,
            'no_color': True
        }
        
        self.logger.warning(f"Permission denied: {user_id} -> {resource}", extra=extra)
    
    def log_suspicious_activity(self, description: str, user_id: str = None,
                               ip_address: str = None, **kwargs):
        """记录可疑活动"""
        extra = {
            'user_id': user_id,
            'ip_address': ip_address,
            'security_event': 'suspicious_activity',
            'no_color': True,
            **kwargs
        }
        
        self.logger.critical(f"Suspicious activity: {description}", extra=extra)

# 创建全局实例
logging_config = LoggingConfig()
request_logger = RequestLogger()
security_logger = SecurityLogger()

def init_logging(app, config: Dict[str, Any] = None):
    """初始化Flask应用的日志系统"""
    import uuid
    from flask import g, request
    
    # 设置日志系统
    logging_config.setup_logging(config)
    
    @app.before_request
    def before_request():
        """请求开始时的处理"""
        g.request_start_time = datetime.now()
        g.request_id = str(uuid.uuid4())[:8]
    
    @app.after_request
    def after_request(response):
        """请求结束时的处理"""
        if hasattr(g, 'request_start_time'):
            duration = (datetime.now() - g.request_start_time).total_seconds()
            
            # 确定业务类型
            business_type = 'unknown'
            if request.path.startswith('/api/ai'):
                business_type = 'ai'
            elif request.path.startswith('/api/blockchain'):
                business_type = 'blockchain'
            elif request.path.startswith('/api/crypto'):
                business_type = 'crypto'
            
            # 记录请求日志
            request_logger.log_request(
                request, response, duration,
                user_id=getattr(g, 'current_user', None),
                business_type=business_type,
                request_id=getattr(g, 'request_id', None)
            )
        
        return response
    
    # 注册错误处理器
    @app.errorhandler(Exception)
    def handle_exception(error):
        """处理未捕获的异常"""
        request_logger.log_error(
            request, error,
            user_id=getattr(g, 'current_user', None),
            business_type=getattr(g, 'business_type', 'unknown'),
            request_id=getattr(g, 'request_id', None)
        )
        
        # 继续正常的错误处理流程
        return {"error": "Internal server error"}, 500
    
    logging.info("Flask应用日志系统初始化完成")