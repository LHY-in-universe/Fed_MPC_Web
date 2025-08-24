"""
示例4: Flask后端集成进程管理
演示如何在Flask应用中集成进程控制和通信功能
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
import uuid
import json
from datetime import datetime
from typing import Dict, Any
import subprocess
import sys
import os

class FlaskProcessManager:
    def __init__(self):
        self.running_processes = {}
        self.completed_tasks = {}
        self.task_queue = []
        self.is_processing = False
        self.processor_thread = None
        
    def add_task(self, task_type: str, data: Dict[str, Any], user_id: str = None) -> str:
        """添加任务到处理队列"""
        task_id = str(uuid.uuid4())
        
        task = {
            'task_id': task_id,
            'task_type': task_type,
            'data': data,
            'user_id': user_id,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'progress': 0
        }
        
        self.task_queue.append(task)
        self.running_processes[task_id] = task
        
        # 启动处理线程（如果未运行）
        if not self.is_processing:
            self.start_processor()
            
        return task_id
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        if task_id in self.running_processes:
            return self.running_processes[task_id]
        elif task_id in self.completed_tasks:
            return self.completed_tasks[task_id]
        else:
            return {'error': 'Task not found'}
    
    def get_all_tasks(self, user_id: str = None) -> list:
        """获取所有任务（可按用户过滤）"""
        all_tasks = list(self.running_processes.values()) + list(self.completed_tasks.values())
        
        if user_id:
            all_tasks = [task for task in all_tasks if task.get('user_id') == user_id]
        
        return sorted(all_tasks, key=lambda x: x['created_at'], reverse=True)
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if task_id in self.running_processes:
            task = self.running_processes[task_id]
            if task['status'] == 'pending':
                task['status'] = 'cancelled'
                task['completed_at'] = datetime.now().isoformat()
                self.completed_tasks[task_id] = task
                del self.running_processes[task_id]
                return True
        return False
    
    def process_ai_training_task(self, task_id: str, data: Dict[str, Any]):
        """处理AI训练任务"""
        task = self.running_processes[task_id]
        task['status'] = 'running'
        task['started_at'] = datetime.now().isoformat()
        
        try:
            project_name = data.get('project_name', 'Unnamed Project')
            model_type = data.get('model_type', 'neural_network')
            epochs = data.get('epochs', 10)
            batch_size = data.get('batch_size', 32)
            
            # 模拟训练过程
            training_history = []
            
            for epoch in range(1, epochs + 1):
                # 更新进度
                progress = int((epoch / epochs) * 100)
                task['progress'] = progress
                task['current_epoch'] = epoch
                
                # 模拟训练指标
                accuracy = min(0.95, 0.5 + (epoch / epochs) * 0.4 + (hash(str(epoch)) % 100) * 0.001)
                loss = max(0.05, 0.5 - (epoch / epochs) * 0.4 + (hash(str(epoch+1)) % 100) * 0.001)
                
                epoch_result = {
                    'epoch': epoch,
                    'accuracy': round(accuracy, 4),
                    'loss': round(loss, 4),
                    'lr': 0.001 * (0.9 ** (epoch // 3))  # 学习率衰减
                }
                
                training_history.append(epoch_result)
                
                print(f"Task {task_id}: Epoch {epoch}/{epochs}, Accuracy: {accuracy:.4f}")
                time.sleep(1)  # 模拟训练时间
            
            # 任务完成
            result = {
                'project_name': project_name,
                'model_type': model_type,
                'total_epochs': epochs,
                'batch_size': batch_size,
                'final_accuracy': training_history[-1]['accuracy'],
                'final_loss': training_history[-1]['loss'],
                'training_history': training_history,
                'model_size': f"{hash(project_name) % 100 + 50}MB",
                'training_time': f"{epochs * 1.2:.1f}s"
            }
            
            task['status'] = 'completed'
            task['progress'] = 100
            task['result'] = result
            task['completed_at'] = datetime.now().isoformat()
            
        except Exception as e:
            task['status'] = 'failed'
            task['error'] = str(e)
            task['completed_at'] = datetime.now().isoformat()
    
    def process_blockchain_task(self, task_id: str, data: Dict[str, Any]):
        """处理区块链任务"""
        task = self.running_processes[task_id]
        task['status'] = 'running'
        task['started_at'] = datetime.now().isoformat()
        
        try:
            operation = data.get('operation', 'create_transaction')
            
            if operation == 'create_transaction':
                # 模拟交易创建过程
                steps = ['验证账户余额', '构建交易', '数字签名', '广播交易', '等待确认']
                
                for i, step in enumerate(steps):
                    task['progress'] = int((i + 1) / len(steps) * 100)
                    task['current_step'] = step
                    print(f"Task {task_id}: {step}")
                    time.sleep(1)
                
                # 生成交易结果
                tx_hash = f"0x{hash(str(data) + str(time.time())) & 0xffffffffffffffff:016x}"
                
                result = {
                    'operation': operation,
                    'transaction_hash': tx_hash,
                    'from_address': data.get('from', '0x1234...'),
                    'to_address': data.get('to', '0x5678...'),
                    'amount': data.get('amount', 1.0),
                    'gas_price': 20,
                    'gas_used': 21000,
                    'block_number': 12345000 + hash(tx_hash) % 1000,
                    'confirmations': 6,
                    'status': 'confirmed'
                }
                
            elif operation == 'deploy_contract':
                # 模拟合约部署
                steps = ['编译合约', '估算Gas', '部署交易', '确认部署', '验证合约']
                
                for i, step in enumerate(steps):
                    task['progress'] = int((i + 1) / len(steps) * 100)
                    task['current_step'] = step
                    print(f"Task {task_id}: {step}")
                    time.sleep(1.5)
                
                contract_address = f"0x{hash(str(data.get('contract_code', '')) + str(time.time())) & 0xffffffffffffffff:016x}"
                
                result = {
                    'operation': operation,
                    'contract_address': contract_address,
                    'deployment_hash': f"0x{hash(contract_address) & 0xffffffffffffffff:016x}",
                    'gas_used': 500000,
                    'contract_size': len(data.get('contract_code', 'contract code')),
                    'status': 'deployed'
                }
            
            task['status'] = 'completed'
            task['progress'] = 100
            task['result'] = result
            task['completed_at'] = datetime.now().isoformat()
            
        except Exception as e:
            task['status'] = 'failed'
            task['error'] = str(e)
            task['completed_at'] = datetime.now().isoformat()
    
    def process_crypto_task(self, task_id: str, data: Dict[str, Any]):
        """处理密码学任务"""
        task = self.running_processes[task_id]
        task['status'] = 'running'
        task['started_at'] = datetime.now().isoformat()
        
        try:
            operation = data.get('operation', 'generate_keys')
            
            if operation == 'generate_keys':
                key_type = data.get('key_type', 'RSA')
                key_size = data.get('key_size', 2048)
                
                steps = ['生成随机数', '创建密钥对', '验证密钥', '保存密钥', '生成指纹']
                
                for i, step in enumerate(steps):
                    task['progress'] = int((i + 1) / len(steps) * 100)
                    task['current_step'] = step
                    print(f"Task {task_id}: {step}")
                    time.sleep(0.8)
                
                result = {
                    'operation': operation,
                    'key_type': key_type,
                    'key_size': key_size,
                    'key_id': str(uuid.uuid4()),
                    'fingerprint': f"{hash(key_type + str(key_size)) & 0xffffffff:08x}",
                    'public_key_preview': f"-----BEGIN {key_type} PUBLIC KEY-----\n...\n-----END {key_type} PUBLIC KEY-----",
                    'creation_time': datetime.now().isoformat(),
                    'status': 'generated'
                }
                
            elif operation == 'encrypt_file':
                file_size = data.get('file_size', 1024)
                algorithm = data.get('algorithm', 'AES-256')
                
                steps = ['读取文件', '生成密钥', '初始化向量', '加密数据', '保存结果']
                
                for i, step in enumerate(steps):
                    task['progress'] = int((i + 1) / len(steps) * 100)
                    task['current_step'] = step
                    print(f"Task {task_id}: {step}")
                    time.sleep(0.6)
                
                result = {
                    'operation': operation,
                    'algorithm': algorithm,
                    'original_size': file_size,
                    'encrypted_size': file_size + 32,  # 加密后稍大
                    'encryption_key_id': str(uuid.uuid4()),
                    'iv': f"{hash(str(time.time())) & 0xffffffff:08x}",
                    'status': 'encrypted'
                }
            
            task['status'] = 'completed'
            task['progress'] = 100
            task['result'] = result
            task['completed_at'] = datetime.now().isoformat()
            
        except Exception as e:
            task['status'] = 'failed'
            task['error'] = str(e)
            task['completed_at'] = datetime.now().isoformat()
    
    def process_task(self, task):
        """处理单个任务"""
        task_id = task['task_id']
        task_type = task['task_type']
        
        try:
            if task_type == 'ai_training':
                self.process_ai_training_task(task_id, task['data'])
            elif task_type == 'blockchain':
                self.process_blockchain_task(task_id, task['data'])
            elif task_type == 'crypto':
                self.process_crypto_task(task_id, task['data'])
            else:
                task['status'] = 'failed'
                task['error'] = f'Unknown task type: {task_type}'
                task['completed_at'] = datetime.now().isoformat()
        
        except Exception as e:
            task['status'] = 'failed'
            task['error'] = str(e)
            task['completed_at'] = datetime.now().isoformat()
        
        # 移动到已完成任务
        self.completed_tasks[task_id] = task
        if task_id in self.running_processes:
            del self.running_processes[task_id]
    
    def processor_loop(self):
        """处理器主循环"""
        self.is_processing = True
        
        while self.is_processing:
            if self.task_queue:
                task = self.task_queue.pop(0)
                if task['status'] == 'pending':
                    print(f"Processing task {task['task_id']} ({task['task_type']})")
                    self.process_task(task)
            else:
                time.sleep(1)
        
        print("Task processor stopped")
    
    def start_processor(self):
        """启动任务处理线程"""
        if not self.is_processing:
            self.processor_thread = threading.Thread(target=self.processor_loop)
            self.processor_thread.start()
            print("Task processor started")
    
    def stop_processor(self):
        """停止任务处理线程"""
        self.is_processing = False
        if self.processor_thread:
            self.processor_thread.join(timeout=10)

# 创建Flask应用
app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 创建进程管理器实例
process_manager = FlaskProcessManager()

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """创建新任务"""
    try:
        data = request.get_json()
        
        task_type = data.get('task_type')
        task_data = data.get('data', {})
        user_id = data.get('user_id', 'anonymous')
        
        if not task_type:
            return jsonify({'error': 'task_type is required'}), 400
        
        task_id = process_manager.add_task(task_type, task_data, user_id)
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Task created successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """获取任务状态"""
    try:
        status = process_manager.get_task_status(task_id)
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks', methods=['GET'])
def get_all_tasks():
    """获取所有任务"""
    try:
        user_id = request.args.get('user_id')
        tasks = process_manager.get_all_tasks(user_id)
        
        return jsonify({
            'tasks': tasks,
            'total': len(tasks)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def cancel_task(task_id):
    """取消任务"""
    try:
        success = process_manager.cancel_task(task_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Task cancelled'})
        else:
            return jsonify({'error': 'Task not found or cannot be cancelled'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'message': 'Process manager is running',
        'active_tasks': len(process_manager.running_processes),
        'completed_tasks': len(process_manager.completed_tasks)
    })

if __name__ == '__main__':
    try:
        print("Starting Flask Process Manager...")
        print("Available endpoints:")
        print("- POST /api/tasks - Create new task")
        print("- GET  /api/tasks/<task_id> - Get task status")
        print("- GET  /api/tasks - Get all tasks")
        print("- DELETE /api/tasks/<task_id> - Cancel task")
        print("- GET  /api/health - Health check")
        
        app.run(host='127.0.0.1', port=5001, debug=True, threaded=True)
    except KeyboardInterrupt:
        print("Shutting down...")
        process_manager.stop_processor()