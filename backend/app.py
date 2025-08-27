"""
联邦学习平台后端主应用
Flask + SQLAlchemy 架构
支持AI大模型和金融区块链两种业务类型
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging
from datetime import datetime, timedelta
import jwt
from functools import wraps

# 导入配置
from config import config

# 导入数据库
from models.base import db
from database import init_database, create_cli_commands

# 导入通用路由模块
from routes.auth import auth_bp
from routes.client import client_bp
from routes.server import server_bp

# 导入业务模块 - 与前端结构保持一致
from ai import ai_bp
from blockchain import blockchain_bp
from crypto import crypto_bp
from homepage import homepage_bp

def create_app(config_name=None):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 配置
    config_name = config_name or os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    
    # 初始化数据库
    db.init_app(app)
    
    # 初始化数据库数据（开发环境）
    if config_name in ['default', 'development']:
        with app.app_context():
            try:
                # 创建表
                db.create_all()
                
                # 初始化默认数据
                from database import DatabaseManager
                db_manager = DatabaseManager(app)
                db_manager.init_default_data()
            except Exception as e:
                app.logger.error(f"数据库初始化失败: {str(e)}")
    
    # 创建CLI命令
    create_cli_commands(app)
    
    # CORS设置
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:*", "http://127.0.0.1:*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-User-Type", "X-Business-Type"]
        }
    })
    
    # 日志配置
    logging.basicConfig(level=logging.INFO)
    app.logger.info('联邦学习平台启动中...')
    
    # 注册蓝图
    # 通用路由
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(client_bp, url_prefix='/api/client')
    app.register_blueprint(server_bp, url_prefix='/api/server')
    
    # 业务模块路由 - 与前端结构保持一致
    app.register_blueprint(homepage_bp, url_prefix='/api/homepage')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(blockchain_bp, url_prefix='/api/blockchain')
    app.register_blueprint(crypto_bp, url_prefix='/api/crypto')
    
    # 全局错误处理
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': '请求参数错误',
            'details': str(error.description) if hasattr(error, 'description') else None
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': '身份认证失败，请重新登录'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Forbidden',
            'message': '权限不足，无法执行此操作'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': '请求的资源不存在',
            'path': request.path if request else None
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'error': 'Method Not Allowed',
            'message': '请求方法不被允许',
            'allowed_methods': error.valid_methods if hasattr(error, 'valid_methods') else None
        }), 405
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({
            'error': 'Rate Limit Exceeded',
            'message': '请求频率过高，请稍后重试'
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        # 记录详细错误日志
        app.logger.error(f'Internal Server Error: {str(error)}', exc_info=True)
        
        # 在开发环境中返回详细错误信息
        if app.debug:
            import traceback
            return jsonify({
                'error': 'Internal Server Error',
                'message': '服务器内部错误',
                'details': str(error),
                'traceback': traceback.format_exc()
            }), 500
        else:
            return jsonify({
                'error': 'Internal Server Error',
                'message': '服务器内部错误，请联系管理员'
            }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        # 记录所有未捕获的异常
        app.logger.error(f'Unhandled Exception: {str(error)}', exc_info=True)
        
        # 数据库相关错误
        if 'database' in str(error).lower() or 'mysql' in str(error).lower():
            return jsonify({
                'error': 'Database Error',
                'message': '数据库连接错误，请稍后重试'
            }), 503
        
        # 默认处理
        return jsonify({
            'error': 'Internal Server Error',
            'message': '服务器内部错误'
        }), 500
    
    # 健康检查接口
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    
    # 获取系统状态
    @app.route('/api/status')
    def system_status():
        status = 'running'
        services = {}
        
        # 检查数据库连接
        try:
            db.session.execute('SELECT 1')
            services['database'] = 'connected'
        except Exception as e:
            services['database'] = 'disconnected'
            status = 'degraded'
            app.logger.error(f'Database connection failed: {str(e)}')
        
        # 检查认证服务
        try:
            services['auth'] = 'online'
        except Exception:
            services['auth'] = 'offline'
            status = 'degraded'
        
        # 检查训练服务
        try:
            services['training'] = 'online'
        except Exception:
            services['training'] = 'offline'
            status = 'degraded'
        
        return jsonify({
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'services': services,
            'supported_business_types': ['ai', 'blockchain', 'crypto'],
            'version': '1.0.0'
        })
    
    return app

def auth_required(f):
    """认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            from flask import current_app
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            
            # 验证用户是否存在且激活
            from models.user import User
            current_user = User.query.filter_by(id=current_user_id, status='active').first()
            if not current_user:
                return jsonify({'error': 'User not found or inactive'}), 401
                
            # 将当前用户信息传递给路由函数
            return f(current_user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': 'Token validation failed'}), 401
    
    return decorated

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)