"""
测试版本的Flask应用 - 用于验证API基本功能
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os

# 导入配置
from config import config

# 导入认证路由
from routes.auth import auth_bp

def create_test_app():
    """创建测试应用"""
    app = Flask(__name__)
    
    # 基本配置
    app.config.from_object(config['default'])
    
    # 启用CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 注册认证路由
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # 健康检查端点
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Fed_MPC_Web Backend API is running',
            'version': '1.0.0'
        })
    
    # 测试端点
    @app.route('/api/test', methods=['GET'])
    def test_endpoint():
        return jsonify({
            'success': True,
            'message': 'API测试成功',
            'data': {
                'server_time': '2024-01-23T10:00:00Z',
                'modules': ['ai', 'blockchain', 'crypto'],
                'status': 'running'
            }
        })
    
    return app

if __name__ == '__main__':
    app = create_test_app()
    print("Starting Fed_MPC_Web Backend Test Server...")
    print("Available endpoints:")
    print("- GET  /api/health")
    print("- GET  /api/test") 
    print("- POST /api/auth/login")
    print("- POST /api/auth/logout")
    print("- GET  /api/auth/verify")
    app.run(host='127.0.0.1', port=5000, debug=True)