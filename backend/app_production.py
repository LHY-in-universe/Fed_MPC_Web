"""
生产环境Flask应用入口
集成监控、日志、错误处理等生产级功能
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# 导入配置
from deploy.production_config import config

# 导入数据库
from models.base import db

# 导入监控和日志
from shared.utils.monitoring import init_monitoring, monitoring
from shared.utils.logging_config import init_logging, security_logger

# 导入路由模块
from routes.auth import auth_bp
from routes.client import client_bp
from routes.server import server_bp

# 导入业务模块
from ai import ai_bp
from blockchain import blockchain_bp
from crypto import crypto_bp
from homepage import homepage_bp

def create_production_app(config_name='production'):
    """创建生产环境Flask应用"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 代理修复中间件（如果使用反向代理）
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # 配置CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', ['*']),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["X-Request-ID"],
            "supports_credentials": True
        }
    })
    
    # 初始化数据库
    db.init_app(app)
    
    # 初始化日志系统
    init_logging(app)
    
    # 初始化监控系统
    init_monitoring(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 注册生产环境中间件
    register_middleware(app)
    
    # 健康检查端点
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """健康检查端点"""
        try:
            # 检查数据库连接
            db.session.execute('SELECT 1')
            
            # 收集系统状态
            status = {
                'status': 'healthy',
                'timestamp': monitoring.app_info._value.get('start_time', ''),
                'version': '1.0.0',
                'database': 'connected',
                'environment': config_name
            }
            
            return jsonify(status), 200
            
        except Exception as e:
            logging.error(f"健康检查失败: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'environment': config_name
            }), 503
    
    # 系统信息端点
    @app.route('/api/system/info', methods=['GET'])
    def system_info():
        """系统信息端点（仅管理员可访问）"""
        try:
            import platform
            import psutil
            
            info = {
                'system': {
                    'platform': platform.platform(),
                    'python_version': platform.python_version(),
                    'architecture': platform.architecture()[0]
                },
                'resources': {
                    'cpu_count': psutil.cpu_count(),
                    'memory_total': psutil.virtual_memory().total,
                    'memory_available': psutil.virtual_memory().available,
                    'disk_usage': psutil.disk_usage('/').percent
                },
                'application': {
                    'name': 'Fed_MPC_Web',
                    'version': '1.0.0',
                    'environment': config_name
                }
            }
            
            return jsonify(info), 200
            
        except ImportError:
            return jsonify({'error': 'System info not available'}), 503
        except Exception as e:
            logging.error(f"获取系统信息失败: {e}")
            return jsonify({'error': 'System info error'}), 500
    
    return app

def register_blueprints(app):
    """注册蓝图"""
    # 通用路由
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(client_bp, url_prefix='/api/client')
    app.register_blueprint(server_bp, url_prefix='/api/server')
    
    # 业务模块路由
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(blockchain_bp, url_prefix='/api/blockchain')
    app.register_blueprint(crypto_bp, url_prefix='/api/crypto')
    app.register_blueprint(homepage_bp, url_prefix='/api')

def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(400)
    def bad_request(error):
        """处理400错误"""
        monitoring.record_error('bad_request', 'http', 'warning')
        return jsonify({
            'error': 'Bad Request',
            'message': '请求参数错误'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """处理401错误"""
        monitoring.record_error('unauthorized', 'auth', 'warning')
        security_logger.log_permission_denied(
            user_id='unknown',
            resource=request.path,
            ip_address=request.remote_addr
        )
        return jsonify({
            'error': 'Unauthorized',
            'message': '需要身份认证'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """处理403错误"""
        monitoring.record_error('forbidden', 'auth', 'warning')
        security_logger.log_permission_denied(
            user_id=getattr(request, 'user_id', 'unknown'),
            resource=request.path,
            ip_address=request.remote_addr
        )
        return jsonify({
            'error': 'Forbidden',
            'message': '权限不足'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """处理404错误"""
        return jsonify({
            'error': 'Not Found',
            'message': '请求的资源不存在'
        }), 404
    
    @app.errorhandler(429)
    def too_many_requests(error):
        """处理429错误"""
        monitoring.record_error('rate_limit', 'http', 'warning')
        return jsonify({
            'error': 'Too Many Requests',
            'message': '请求频率过高，请稍后再试'
        }), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """处理500错误"""
        monitoring.record_error('internal_error', 'system', 'error')
        logging.error(f"内部服务器错误: {error}", exc_info=True)
        return jsonify({
            'error': 'Internal Server Error',
            'message': '服务器内部错误，请联系管理员'
        }), 500
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """处理503错误"""
        monitoring.record_error('service_unavailable', 'system', 'error')
        return jsonify({
            'error': 'Service Unavailable',
            'message': '服务暂时不可用，请稍后再试'
        }), 503

def register_middleware(app):
    """注册生产环境中间件"""
    
    @app.before_request
    def security_headers():
        """安全相关处理"""
        # 记录可疑请求
        if len(request.path) > 1000:  # 路径过长
            security_logger.log_suspicious_activity(
                f"Extremely long request path: {len(request.path)} characters",
                ip_address=request.remote_addr
            )
        
        # 检查请求头
        user_agent = request.headers.get('User-Agent', '')
        if not user_agent or len(user_agent) > 500:
            security_logger.log_suspicious_activity(
                f"Suspicious User-Agent: {user_agent[:100]}...",
                ip_address=request.remote_addr
            )
    
    @app.after_request
    def add_security_headers(response):
        """添加安全头"""
        # 安全相关HTTP头
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # CSP头（根据需要调整）
        if not app.config.get('DEBUG', False):
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "connect-src 'self'"
            )
        
        return response

def create_tables(app):
    """创建数据库表"""
    with app.app_context():
        try:
            db.create_all()
            logging.info("数据库表创建成功")
        except Exception as e:
            logging.error(f"数据库表创建失败: {e}")
            raise

# 创建应用实例
app = create_production_app()

if __name__ == '__main__':
    # 开发环境直接运行
    app.run(host='127.0.0.1', port=5000, debug=False)
else:
    # 生产环境由Gunicorn运行
    # 确保数据库表存在
    create_tables(app)