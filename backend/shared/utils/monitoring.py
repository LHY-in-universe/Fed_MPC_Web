"""
应用监控和指标收集
集成Prometheus监控系统
"""

import time
import functools
from datetime import datetime
from typing import Dict, Any, Optional
from flask import request, g
import logging

try:
    from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger(__name__)

class ApplicationMonitoring:
    """应用程序监控类"""
    
    def __init__(self, app_name: str = "fed_mpc_web"):
        self.app_name = app_name
        self.enabled = PROMETHEUS_AVAILABLE
        
        if self.enabled:
            self._init_metrics()
        else:
            logger.warning("Prometheus客户端未安装，监控功能已禁用")
    
    def _init_metrics(self):
        """初始化Prometheus指标"""
        # HTTP请求指标
        self.http_requests_total = Counter(
            'fed_mpc_web_http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code', 'business_type']
        )
        
        self.http_request_duration = Histogram(
            'fed_mpc_web_http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint', 'business_type']
        )
        
        # 业务指标
        self.active_sessions = Gauge(
            'fed_mpc_web_active_sessions_total',
            'Number of active user sessions',
            ['business_type']
        )
        
        self.training_sessions = Gauge(
            'fed_mpc_web_training_sessions_total',
            'Number of training sessions',
            ['status', 'business_type']
        )
        
        self.transactions_total = Counter(
            'fed_mpc_web_transactions_total',
            'Total blockchain transactions',
            ['status', 'transaction_type']
        )
        
        self.keys_generated = Counter(
            'fed_mpc_web_keys_generated_total',
            'Total cryptographic keys generated',
            ['key_type', 'key_size']
        )
        
        # 系统指标
        self.database_connections = Gauge(
            'fed_mpc_web_database_connections',
            'Number of active database connections'
        )
        
        self.database_query_duration = Histogram(
            'fed_mpc_web_database_query_duration_seconds',
            'Database query duration in seconds',
            ['query_type']
        )
        
        self.cache_operations = Counter(
            'fed_mpc_web_cache_operations_total',
            'Total cache operations',
            ['operation', 'result']
        )
        
        # 错误指标
        self.errors_total = Counter(
            'fed_mpc_web_errors_total',
            'Total application errors',
            ['error_type', 'module', 'severity']
        )
        
        # 应用信息
        self.app_info = Info(
            'fed_mpc_web_app_info',
            'Application information'
        )
        
        # 设置应用信息
        self.app_info.info({
            'version': '1.0.0',
            'python_version': self._get_python_version(),
            'start_time': datetime.now().isoformat()
        })
    
    def _get_python_version(self) -> str:
        """获取Python版本"""
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def record_http_request(self, method: str, endpoint: str, status_code: int, 
                          duration: float, business_type: str = 'unknown'):
        """记录HTTP请求指标"""
        if not self.enabled:
            return
        
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            business_type=business_type
        ).inc()
        
        self.http_request_duration.labels(
            method=method,
            endpoint=endpoint,
            business_type=business_type
        ).observe(duration)
    
    def record_training_session(self, status: str, business_type: str = 'ai'):
        """记录训练会话指标"""
        if not self.enabled:
            return
        
        self.training_sessions.labels(
            status=status,
            business_type=business_type
        ).inc()
    
    def record_transaction(self, status: str, transaction_type: str):
        """记录区块链交易指标"""
        if not self.enabled:
            return
        
        self.transactions_total.labels(
            status=status,
            transaction_type=transaction_type
        ).inc()
    
    def record_key_generation(self, key_type: str, key_size: int):
        """记录密钥生成指标"""
        if not self.enabled:
            return
        
        self.keys_generated.labels(
            key_type=key_type,
            key_size=str(key_size)
        ).inc()
    
    def record_database_query(self, duration: float, query_type: str = 'select'):
        """记录数据库查询指标"""
        if not self.enabled:
            return
        
        self.database_query_duration.labels(
            query_type=query_type
        ).observe(duration)
    
    def record_cache_operation(self, operation: str, result: str):
        """记录缓存操作指标"""
        if not self.enabled:
            return
        
        self.cache_operations.labels(
            operation=operation,
            result=result
        ).inc()
    
    def record_error(self, error_type: str, module: str, severity: str = 'error'):
        """记录错误指标"""
        if not self.enabled:
            return
        
        self.errors_total.labels(
            error_type=error_type,
            module=module,
            severity=severity
        ).inc()
    
    def update_active_sessions(self, count: int, business_type: str):
        """更新活跃会话数量"""
        if not self.enabled:
            return
        
        self.active_sessions.labels(business_type=business_type).set(count)
    
    def update_database_connections(self, count: int):
        """更新数据库连接数量"""
        if not self.enabled:
            return
        
        self.database_connections.set(count)
    
    def get_metrics(self) -> str:
        """获取Prometheus格式的指标数据"""
        if not self.enabled:
            return "# Prometheus not available\n"
        
        return generate_latest()
    
    def get_content_type(self) -> str:
        """获取指标数据的Content-Type"""
        if not self.enabled:
            return "text/plain"
        
        return CONTENT_TYPE_LATEST

# 全局监控实例
monitoring = ApplicationMonitoring()

def monitor_request_duration(business_type: str = 'unknown'):
    """装饰器：监控请求持续时间"""
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = f(*args, **kwargs)
                duration = time.time() - start_time
                
                # 记录成功请求
                monitoring.record_http_request(
                    method=request.method,
                    endpoint=request.endpoint or 'unknown',
                    status_code=getattr(result, 'status_code', 200),
                    duration=duration,
                    business_type=business_type
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # 记录错误请求
                monitoring.record_http_request(
                    method=request.method,
                    endpoint=request.endpoint or 'unknown',
                    status_code=500,
                    duration=duration,
                    business_type=business_type
                )
                
                # 记录错误
                monitoring.record_error(
                    error_type=type(e).__name__,
                    module=f.__module__,
                    severity='error'
                )
                
                raise
        
        return wrapper
    return decorator

def monitor_database_query(query_type: str = 'select'):
    """装饰器：监控数据库查询"""
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = f(*args, **kwargs)
                duration = time.time() - start_time
                monitoring.record_database_query(duration, query_type)
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                monitoring.record_database_query(duration, query_type)
                monitoring.record_error(
                    error_type=type(e).__name__,
                    module='database',
                    severity='error'
                )
                raise
        
        return wrapper
    return decorator

class SystemMetricsCollector:
    """系统指标收集器"""
    
    def __init__(self):
        self.monitoring = monitoring
    
    def collect_system_metrics(self):
        """收集系统指标"""
        try:
            # 收集数据库连接数
            self._collect_database_metrics()
            
            # 收集应用状态
            self._collect_application_metrics()
            
        except Exception as e:
            logger.error(f"收集系统指标失败: {e}")
    
    def _collect_database_metrics(self):
        """收集数据库指标"""
        try:
            from models.base import db
            
            # 获取数据库连接池信息
            engine = db.engine
            pool = engine.pool
            
            # 更新连接数指标
            if hasattr(pool, 'checked_in'):
                active_connections = pool.checked_in()
                self.monitoring.update_database_connections(active_connections)
            
        except Exception as e:
            logger.debug(f"收集数据库指标失败: {e}")
    
    def _collect_application_metrics(self):
        """收集应用指标"""
        try:
            # 这里可以添加其他应用指标的收集逻辑
            pass
        except Exception as e:
            logger.debug(f"收集应用指标失败: {e}")

# 创建指标收集器实例
metrics_collector = SystemMetricsCollector()

def init_monitoring(app):
    """初始化Flask应用的监控"""
    
    @app.before_request
    def before_request():
        """请求开始时记录时间"""
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        """请求结束时记录指标"""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            # 从URL确定业务类型
            business_type = 'unknown'
            if request.path.startswith('/api/ai'):
                business_type = 'ai'
            elif request.path.startswith('/api/blockchain'):
                business_type = 'blockchain'
            elif request.path.startswith('/api/crypto'):
                business_type = 'crypto'
            
            monitoring.record_http_request(
                method=request.method,
                endpoint=request.endpoint or request.path,
                status_code=response.status_code,
                duration=duration,
                business_type=business_type
            )
        
        return response
    
    @app.route('/api/metrics')
    def metrics_endpoint():
        """Prometheus指标端点"""
        # 收集最新的系统指标
        metrics_collector.collect_system_metrics()
        
        # 返回指标数据
        from flask import Response
        return Response(
            monitoring.get_metrics(),
            mimetype=monitoring.get_content_type()
        )
    
    logger.info("应用监控系统已初始化")