#!/usr/bin/env python3
"""
Fed_MPC_Web 本地服务启动器
联邦学习与多方计算平台
"""

import sys
import os
import subprocess
import time
import threading
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'backend'))

def install_requirements():
    """安装必要的依赖"""
    print("📦 检查Python依赖...")
    
    required_packages = ['flask', 'flask-cors']
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"⬇️ 正在安装 {package}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                         check=True, capture_output=True)

def create_demo_app():
    """创建并启动演示应用"""
    print("🚀 启动Fed_MPC_Web服务器...")
    
    from flask import Flask, jsonify, send_from_directory, request
    from flask_cors import CORS
    import json
    from datetime import datetime
    
    app = Flask(__name__, static_folder='frontend')
    
    # 配置CORS
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:*", "http://127.0.0.1:*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 模拟用户数据
    DEMO_USERS = {
        'client1': {'password': '123456', 'type': 'client', 'business': 'ai', 'name': '客户端1'},
        'server': {'password': 'admin123', 'type': 'server', 'business': 'ai', 'name': 'AI管理员'},
        'user': {'password': 'user123', 'type': 'client', 'business': 'blockchain', 'name': '区块链用户'},
        'cryptographer': {'password': 'crypto123', 'type': 'client', 'business': 'crypto', 'name': '密码学专家'},
    }
    
    # API路由
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Fed_MPC_Web is running',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'environment': 'production'
        })
    
    @app.route('/api/test')
    def test_api():
        return jsonify({
            'success': True,
            'message': 'API服务正常运行！',
            'data': {
                'modules': ['ai', 'blockchain', 'crypto'],
                'features': ['联邦学习', '区块链交易', '密钥管理'],
                'status': 'running'
            }
        })
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')
        
        if username in DEMO_USERS and DEMO_USERS[username]['password'] == password:
            user_info = DEMO_USERS[username]
            return jsonify({
                'success': True,
                'token': f'demo_token_{username}',
                'user': {
                    'id': username,
                    'name': user_info['name'],
                    'type': user_info['type'],
                    'business_type': user_info['business']
                },
                'message': '登录成功！'
            })
        else:
            return jsonify({'error': '用户名或密码错误'}), 401
    
    @app.route('/api/ai/projects')
    def ai_projects():
        return jsonify({
            'success': True,
            'data': {
                'projects': [
                    {'id': 1, 'name': 'CNN故障检测', 'status': 'active', 'accuracy': 0.923},
                    {'id': 2, 'name': 'LSTM预测模型', 'status': 'completed', 'accuracy': 0.887},
                    {'id': 3, 'name': '联邦学习项目', 'status': 'training', 'accuracy': 0.856}
                ],
                'total': 3
            }
        })
    
    @app.route('/api/blockchain/transactions')
    def blockchain_transactions():
        return jsonify({
            'success': True,
            'data': {
                'transactions': [
                    {'hash': '0x123...abc', 'status': 'confirmed', 'amount': 1.5},
                    {'hash': '0x456...def', 'status': 'pending', 'amount': 0.8},
                    {'hash': '0x789...ghi', 'status': 'confirmed', 'amount': 2.1}
                ],
                'total': 3
            }
        })
    
    @app.route('/api/crypto/keys')
    def crypto_keys():
        return jsonify({
            'success': True,
            'data': {
                'keys': [
                    {'id': 1, 'name': '主RSA密钥', 'type': 'RSA', 'size': 2048},
                    {'id': 2, 'name': 'AES加密密钥', 'type': 'AES', 'size': 256},
                    {'id': 3, 'name': 'ECC签名密钥', 'type': 'ECC', 'size': 256}
                ],
                'total': 3
            }
        })
    
    # 前端路由
    @app.route('/')
    def index():
        import os
        try:
            # 尝试直接读取文件
            homepage_path = os.path.join(os.path.dirname(__file__), 'frontend', 'homepage', 'index.html')
            if os.path.exists(homepage_path):
                with open(homepage_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                # 如果文件不存在，使用send_from_directory
                return send_from_directory('homepage', 'index.html')
        except Exception as e:
            print(f"Error loading homepage: {e}")
            from flask import abort
            abort(500)  # 直接返回500错误，不显示任何演示页面
    
    @app.route('/ai/')
    @app.route('/ai/<path:filename>')
    def ai_module(filename=None):
        try:
            if filename:
                return send_from_directory('frontend/ai', filename)
            else:
                return send_from_directory('frontend/ai/pages', 'main-dashboard.html')
        except:
            from flask import abort
            abort(404)
    
    @app.route('/blockchain/')
    @app.route('/blockchain/<path:filename>')
    def blockchain_module(filename=None):
        try:
            if filename:
                return send_from_directory('frontend/blockchain', filename)
            else:
                return send_from_directory('frontend/blockchain/pages', 'main-dashboard.html')
        except:
            from flask import abort
            abort(404)
    
    @app.route('/crypto/')
    @app.route('/crypto/<path:filename>')
    def crypto_module(filename=None):
        try:
            if filename:
                return send_from_directory('frontend/crypto', filename)
            else:
                return send_from_directory('frontend/crypto/pages', 'main-dashboard.html')
        except:
            from flask import abort
            abort(404)
    
    @app.route('/shared/<path:filename>')
    def shared_files(filename):
        try:
            return send_from_directory('frontend/shared', filename)
        except:
            return "文件未找到", 404
    
    return app

def open_browser_delayed(url, delay=2):
    """延迟打开浏览器"""
    time.sleep(delay)
    try:
        import webbrowser
        webbrowser.open(url)
        print(f"🌐 浏览器已打开: {url}")
    except:
        print(f"请手动访问: {url}")

def main():
    """主函数"""
    print("="*60)
    print("🎯 Fed_MPC_Web 系统启动")
    print("="*60)
    
    try:
        # 检查依赖
        install_requirements()
        
        # 创建应用
        app = create_demo_app()
        
        print("✅ 系统准备完成!")
        print()
        print("🌐 访问地址:")
        print("  主页:       http://127.0.0.1:8888")
        print("  AI模块:     http://127.0.0.1:8888/ai/")
        print("  区块链模块: http://127.0.0.1:8888/blockchain/")
        print("  密码学模块: http://127.0.0.1:8888/crypto/")
        print("  健康检查:   http://127.0.0.1:8888/api/health")
        print()
        print("🔑 测试用户:")
        print("  AI客户端:   client1 / 123456")
        print("  AI管理员:   server / admin123")
        print("  区块链用户: user / user123")
        print("  密码学专家: cryptographer / crypto123")
        print()
        print("📊 系统状态: 已启动，准备接收请求...")
        print("="*60)
        
        # 在后台打开浏览器
        threading.Thread(
            target=open_browser_delayed,
            args=('http://127.0.0.1:8888',),
            daemon=True
        ).start()
        
        # 启动Flask服务器
        app.run(host='127.0.0.1', port=8888, debug=False, threaded=True)
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()