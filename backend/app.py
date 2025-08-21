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

# 导入路由模块
from routes.auth import auth_bp
from routes.client import client_bp
from routes.server import server_bp
from routes.training import training_bp

def create_app():
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 配置
    app.config.from_object('config.Config')
    
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
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(client_bp, url_prefix='/api/client')
    app.register_blueprint(server_bp, url_prefix='/api/server')
    app.register_blueprint(training_bp, url_prefix='/api/training')
    
    # 全局错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'API endpoint not found',
            'message': '请求的API接口不存在'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal server error',
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
        return jsonify({
            'status': 'running',
            'services': {
                'auth': 'online',
                'training': 'online',
                'database': 'connected'  # TODO: 实际检查数据库连接
            },
            'supported_business_types': ['ai', 'blockchain']
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
            # TODO: 实现JWT令牌验证
            # data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            # current_user = data['user_id']
            pass
        except:
            return jsonify({'error': 'Token is invalid'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)