#!/usr/bin/env python3
"""
本地演示部署脚本
不依赖Docker，直接使用Python运行完整的Fed_MPC_Web系统
"""

import sys
import os
import subprocess
import time
import threading
from pathlib import Path
import sqlite3

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'backend'))

def create_sqlite_database():
    """创建SQLite数据库（用于演示）"""
    db_path = project_root / 'fed_mpc_demo.db'
    
    print(f"📊 创建演示数据库: {db_path}")
    
    # 如果数据库已存在，删除它
    if db_path.exists():
        db_path.unlink()
    
    # 创建新数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            user_type VARCHAR(20) NOT NULL,
            business_type VARCHAR(20) NOT NULL,
            full_name VARCHAR(100),
            organization VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建项目表
    cursor.execute('''
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            project_type VARCHAR(50) NOT NULL,
            training_mode VARCHAR(50) NOT NULL,
            status VARCHAR(20) DEFAULT 'active',
            model_config JSON,
            privacy_level VARCHAR(20) DEFAULT 'standard',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # 创建训练会话表
    cursor.execute('''
        CREATE TABLE training_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id VARCHAR(100) UNIQUE NOT NULL,
            project_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            current_round INTEGER DEFAULT 0,
            total_rounds INTEGER DEFAULT 10,
            accuracy DECIMAL(10, 6),
            loss DECIMAL(10, 6),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # 插入演示用户数据
    demo_users = [
        ('client1', 'pbkdf2:sha256:260000$salt$hash', 'client', 'ai', '客户端1', 'AI科技公司'),
        ('server', 'pbkdf2:sha256:260000$salt$hash', 'server', 'ai', 'AI服务器管理员', 'AI平台管理'),
        ('user', 'pbkdf2:sha256:260000$salt$hash', 'client', 'blockchain', '普通用户', '金融用户'),
        ('cryptographer', 'pbkdf2:sha256:260000$salt$hash', 'client', 'crypto', '密码学专家', '密码学研究院'),
    ]
    
    cursor.executemany('''
        INSERT INTO users (username, password_hash, user_type, business_type, full_name, organization)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', demo_users)
    
    # 插入演示项目数据
    demo_projects = [
        (1, 'CNN图像识别', 'CNN模型用于工业故障检测', 'classification', 'federated', 'active'),
        (1, 'LSTM时序预测', 'LSTM模型用于设备状态预测', 'regression', 'local', 'completed'),
        (4, '数据加密项目', '企业数据加密解决方案', 'encryption', 'standard', 'active'),
    ]
    
    cursor.executemany('''
        INSERT INTO projects (user_id, name, description, project_type, training_mode, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', demo_projects)
    
    conn.commit()
    conn.close()
    
    print("✅ 演示数据库创建完成")
    return str(db_path)

def create_demo_config():
    """创建演示配置"""
    config_content = f'''
"""
本地演示配置
"""

import os
from datetime import timedelta

class DemoConfig:
    DEBUG = True
    TESTING = False
    
    # 安全配置
    SECRET_KEY = 'fed-mpc-demo-secret-key-2024'
    JWT_SECRET_KEY = 'fed-mpc-jwt-demo-key-2024'
    
    # SQLite数据库配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{project_root / "fed_mpc_demo.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT配置
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # CORS配置
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:8080']
    
    # 其他配置
    JSON_AS_ASCII = False
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB

config = {{'demo': DemoConfig, 'default': DemoConfig}}
'''
    
    config_path = project_root / 'backend' / 'demo_config.py'
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("✅ 演示配置文件创建完成")
    return config_path

def create_demo_app():
    """创建演示应用"""
    app_content = '''
"""
Fed_MPC_Web 本地演示应用
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'backend'))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)

# 导入配置
from demo_config import config

# 导入路由
try:
    from routes.auth import auth_bp
except ImportError as e:
    print(f"导入auth路由失败: {e}")
    auth_bp = None

def create_demo_app():
    """创建演示应用"""
    app = Flask(__name__, static_folder=str(project_root / 'frontend'))
    
    # 加载配置
    app.config.from_object(config['demo'])
    
    # 配置CORS
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 注册认证路由
    if auth_bp:
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # 健康检查
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Fed_MPC_Web Demo is running',
            'version': '1.0.0-demo',
            'database': 'sqlite',
            'environment': 'demo'
        })
    
    # API测试端点
    @app.route('/api/test')
    def test_api():
        return jsonify({
            'success': True,
            'message': '演示API正常工作',
            'data': {
                'modules': ['ai', 'blockchain', 'crypto'],
                'server_time': '2024-08-24T10:00:00Z',
                'status': 'running'
            }
        })
    
    # 前端路由 - 首页
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'homepage/index.html')
    
    # 前端路由 - AI模块
    @app.route('/ai/')
    @app.route('/ai/<path:filename>')
    def ai_module(filename='pages/main-dashboard.html'):
        try:
            return send_from_directory(f'{app.static_folder}/ai', filename)
        except:
            return send_from_directory(f'{app.static_folder}/ai/pages', 'main-dashboard.html')
    
    # 前端路由 - 区块链模块  
    @app.route('/blockchain/')
    @app.route('/blockchain/<path:filename>')
    def blockchain_module(filename='pages/main-dashboard.html'):
        try:
            return send_from_directory(f'{app.static_folder}/blockchain', filename)
        except:
            return send_from_directory(f'{app.static_folder}/blockchain/pages', 'main-dashboard.html')
    
    # 前端路由 - 密码学模块
    @app.route('/crypto/')
    @app.route('/crypto/<path:filename>')
    def crypto_module(filename='pages/main-dashboard.html'):
        try:
            return send_from_directory(f'{app.static_folder}/crypto', filename)
        except:
            return send_from_directory(f'{app.static_folder}/crypto/pages', 'main-dashboard.html')
    
    # 静态文件路由
    @app.route('/shared/<path:filename>')
    def shared_files(filename):
        return send_from_directory(f'{app.static_folder}/shared', filename)
    
    return app

if __name__ == '__main__':
    app = create_demo_app()
    print("🚀 启动Fed_MPC_Web演示服务器...")
    print("访问地址:")
    print("  主页: http://127.0.0.1:8080")
    print("  AI模块: http://127.0.0.1:8080/ai/")
    print("  区块链模块: http://127.0.0.1:8080/blockchain/")
    print("  密码学模块: http://127.0.0.1:8080/crypto/")
    print("  健康检查: http://127.0.0.1:8080/api/health")
    print("  API测试: http://127.0.0.1:8080/api/test")
    
    app.run(host='127.0.0.1', port=8080, debug=True, threaded=True)
'''
    
    app_path = project_root / 'demo_app.py'
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(app_content)
    
    print("✅ 演示应用创建完成")
    return app_path

def install_demo_dependencies():
    """安装演示所需依赖"""
    print("📦 检查并安装演示依赖...")
    
    required_packages = ['flask', 'flask-cors']
    
    for package in required_packages:
        try:
            result = subprocess.run([
                sys.executable, '-c', f'import {package.replace("-", "_")}'
            ], capture_output=True)
            
            if result.returncode != 0:
                print(f"安装 {package}...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', package])
            else:
                print(f"✅ {package} already installed")
        except Exception as e:
            print(f"⚠️ 检查 {package} 时出错: {e}")
    
    print("✅ 依赖检查完成")

def open_browser(url, delay=3):
    """延时打开浏览器"""
    time.sleep(delay)
    try:
        import webbrowser
        webbrowser.open(url)
        print(f"🌐 已在浏览器中打开: {url}")
    except:
        print(f"请手动在浏览器中访问: {url}")

def main():
    """主函数"""
    print("="*60)
    print("🎯 Fed_MPC_Web 本地演示部署")
    print("="*60)
    
    try:
        # 1. 检查和安装依赖
        install_demo_dependencies()
        
        # 2. 创建演示数据库
        db_path = create_sqlite_database()
        
        # 3. 创建演示配置
        config_path = create_demo_config()
        
        # 4. 创建演示应用
        app_path = create_demo_app()
        
        print("\\n" + "="*60)
        print("🚀 启动演示服务器...")
        print("="*60)
        
        # 5. 在后台线程中打开浏览器
        threading.Thread(
            target=open_browser, 
            args=('http://127.0.0.1:8080',), 
            daemon=True
        ).start()
        
        # 6. 启动Flask应用
        os.chdir(project_root)
        subprocess.run([sys.executable, str(app_path)])
        
    except KeyboardInterrupt:
        print("\\n👋 演示服务器已停止")
    except Exception as e:
        print(f"❌ 演示部署失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
'''
    
    demo_path = project_root / 'deploy' / 'local_demo.py'
    with open(demo_path, 'w', encoding='utf-8') as f:
        f.write(demo_content)
    
    return demo_path

if __name__ == '__main__':
    main()