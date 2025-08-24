"""
示例3: 使用Redis进行进程间通信
演示如何使用Redis作为消息队列进行跨进程通信
注意: 需要安装redis: pip install redis
"""

import json
import time
import uuid
import threading
from datetime import datetime
from typing import Dict, Any, Optional

# 模拟Redis客户端（如果没有安装redis包）
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Redis not available. Using mock implementation.")

class MockRedis:
    """模拟Redis客户端用于演示"""
    def __init__(self):
        self.data = {}
        self.lists = {}
        
    def set(self, key, value):
        self.data[key] = value
        
    def get(self, key):
        return self.data.get(key)
        
    def lpush(self, key, value):
        if key not in self.lists:
            self.lists[key] = []
        self.lists[key].insert(0, value)
        
    def brpop(self, keys, timeout=0):
        # 简化的阻塞弹出实现
        if isinstance(keys, str):
            keys = [keys]
        
        for key in keys:
            if key in self.lists and self.lists[key]:
                value = self.lists[key].pop()
                return (key, value)
        return None
        
    def rpop(self, key):
        if key in self.lists and self.lists[key]:
            return self.lists[key].pop()
        return None

class RedisTaskProcessor:
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        """初始化Redis任务处理器"""
        if REDIS_AVAILABLE:
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
        else:
            self.redis_client = MockRedis()
        
        self.task_queue = 'fed_mpc_tasks'
        self.result_prefix = 'fed_mpc_result:'
        self.status_prefix = 'fed_mpc_status:'
        self.running = False
        self.worker_thread = None
        
    def add_task(self, task_type: str, data: Dict[str, Any], priority: int = 0) -> str:
        """添加任务到Redis队列"""
        task_id = str(uuid.uuid4())
        
        task = {
            'task_id': task_id,
            'task_type': task_type,
            'data': data,
            'priority': priority,
            'created_at': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        # 保存任务状态
        self.redis_client.set(
            f"{self.status_prefix}{task_id}",
            json.dumps(task, ensure_ascii=False)
        )
        
        # 添加到任务队列
        self.redis_client.lpush(
            self.task_queue,
            json.dumps(task, ensure_ascii=False)
        )
        
        print(f"Task {task_id} added to queue")
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        status_data = self.redis_client.get(f"{self.status_prefix}{task_id}")
        if status_data:
            return json.loads(status_data)
        return None
    
    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务结果"""
        result_data = self.redis_client.get(f"{self.result_prefix}{task_id}")
        if result_data:
            return json.loads(result_data)
        return None
    
    def update_task_status(self, task_id: str, status: str, extra_data: Dict = None):
        """更新任务状态"""
        task_data = self.get_task_status(task_id)
        if task_data:
            task_data['status'] = status
            task_data['updated_at'] = datetime.now().isoformat()
            if extra_data:
                task_data.update(extra_data)
            
            self.redis_client.set(
                f"{self.status_prefix}{task_id}",
                json.dumps(task_data, ensure_ascii=False)
            )
    
    def save_task_result(self, task_id: str, result: Dict[str, Any]):
        """保存任务结果"""
        result_data = {
            'task_id': task_id,
            'result': result,
            'completed_at': datetime.now().isoformat()
        }
        
        self.redis_client.set(
            f"{self.result_prefix}{task_id}",
            json.dumps(result_data, ensure_ascii=False)
        )
        
        # 更新状态为完成
        self.update_task_status(task_id, 'completed')
    
    def process_federated_learning_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理联邦学习任务"""
        model_type = data.get('model_type', 'neural_network')
        rounds = data.get('rounds', 5)
        participants = data.get('participants', ['client1', 'client2', 'client3'])
        
        # 模拟联邦学习过程
        training_history = []
        global_accuracy = 0.6
        
        for round_num in range(1, rounds + 1):
            print(f"  Federated round {round_num}/{rounds}")
            
            # 模拟每个参与者的本地训练
            local_updates = {}
            for participant in participants:
                local_accuracy = global_accuracy + (0.1 * (1 - global_accuracy)) + \
                               (0.05 * (2 * hash(participant) % 10 - 5) / 10)
                local_updates[participant] = {
                    'accuracy': min(0.95, max(0.5, local_accuracy)),
                    'loss': max(0.05, 0.5 - local_accuracy + 0.1),
                    'samples': hash(participant) % 1000 + 500
                }
            
            # 模拟聚合
            total_samples = sum(update['samples'] for update in local_updates.values())
            weighted_accuracy = sum(
                update['accuracy'] * update['samples'] 
                for update in local_updates.values()
            ) / total_samples
            
            global_accuracy = weighted_accuracy
            
            round_result = {
                'round': round_num,
                'global_accuracy': round(global_accuracy, 4),
                'participants': len(participants),
                'local_updates': {k: {
                    'accuracy': round(v['accuracy'], 4),
                    'loss': round(v['loss'], 4),
                    'samples': v['samples']
                } for k, v in local_updates.items()}
            }
            
            training_history.append(round_result)
            time.sleep(0.5)  # 模拟训练时间
        
        return {
            'model_type': model_type,
            'total_rounds': rounds,
            'final_accuracy': round(global_accuracy, 4),
            'participants': participants,
            'training_history': training_history,
            'status': 'success'
        }
    
    def process_blockchain_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理区块链任务"""
        operation = data.get('operation', 'create_transaction')
        
        if operation == 'create_transaction':
            from_addr = data.get('from', '0x123...')
            to_addr = data.get('to', '0x456...')
            amount = data.get('amount', 1.0)
            
            # 模拟交易创建
            tx_hash = f"0x{hash(f'{from_addr}{to_addr}{amount}{time.time()}') & 0xffffffffffffffff:016x}"
            
            time.sleep(1)  # 模拟区块确认时间
            
            return {
                'transaction_hash': tx_hash,
                'from_address': from_addr,
                'to_address': to_addr,
                'amount': amount,
                'status': 'confirmed',
                'block_number': 12345678 + hash(tx_hash) % 1000,
                'gas_used': 21000
            }
        
        elif operation == 'deploy_contract':
            contract_code = data.get('code', 'contract code...')
            
            # 模拟合约部署
            contract_address = f"0x{hash(contract_code + str(time.time())) & 0xffffffffffffffff:016x}"
            
            time.sleep(2)  # 模拟部署时间
            
            return {
                'contract_address': contract_address,
                'deployment_hash': f"0x{hash(contract_address) & 0xffffffffffffffff:016x}",
                'status': 'deployed',
                'gas_used': 500000
            }
    
    def process_crypto_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理密码学任务"""
        operation = data.get('operation', 'generate_keys')
        
        if operation == 'generate_keys':
            key_type = data.get('key_type', 'RSA')
            key_size = data.get('key_size', 2048)
            
            # 模拟密钥生成
            time.sleep(1)
            
            return {
                'key_type': key_type,
                'key_size': key_size,
                'public_key': f"-----BEGIN {key_type} PUBLIC KEY-----\n...{hash(str(time.time()))}...\n-----END {key_type} PUBLIC KEY-----",
                'key_id': str(uuid.uuid4()),
                'fingerprint': f"{hash(key_type + str(key_size)) & 0xffffffff:08x}",
                'status': 'generated'
            }
        
        elif operation == 'encrypt':
            data_to_encrypt = data.get('data', 'Hello World')
            algorithm = data.get('algorithm', 'AES-256')
            
            time.sleep(0.5)
            
            # 模拟加密
            encrypted = f"encrypted_{hash(data_to_encrypt + algorithm) & 0xffffffffffffffff:016x}"
            
            return {
                'algorithm': algorithm,
                'original_size': len(data_to_encrypt),
                'encrypted_data': encrypted,
                'encryption_key_id': str(uuid.uuid4()),
                'status': 'encrypted'
            }
    
    def worker_loop(self):
        """工作进程主循环"""
        print("Worker started, waiting for tasks...")
        
        while self.running:
            try:
                # 从队列获取任务（阻塞等待）
                if REDIS_AVAILABLE:
                    result = self.redis_client.brpop([self.task_queue], timeout=1)
                else:
                    result = self.redis_client.brpop(self.task_queue)
                
                if not result:
                    continue
                    
                task_data = json.loads(result[1])
                task_id = task_data['task_id']
                task_type = task_data['task_type']
                
                print(f"Processing task {task_id} ({task_type})")
                
                # 更新状态为处理中
                self.update_task_status(task_id, 'processing')
                
                try:
                    # 根据任务类型处理
                    if task_type == 'federated_learning':
                        result = self.process_federated_learning_task(task_data['data'])
                    elif task_type == 'blockchain':
                        result = self.process_blockchain_task(task_data['data'])
                    elif task_type == 'crypto':
                        result = self.process_crypto_task(task_data['data'])
                    else:
                        result = {'error': f'Unknown task type: {task_type}'}
                    
                    # 保存结果
                    self.save_task_result(task_id, result)
                    print(f"Task {task_id} completed successfully")
                    
                except Exception as e:
                    # 处理错误
                    error_result = {
                        'error': str(e),
                        'task_type': task_type,
                        'failed_at': datetime.now().isoformat()
                    }
                    self.save_task_result(task_id, error_result)
                    self.update_task_status(task_id, 'failed', {'error': str(e)})
                    print(f"Task {task_id} failed: {e}")
                
            except Exception as e:
                print(f"Worker error: {e}")
                time.sleep(1)
        
        print("Worker stopped")
    
    def start_worker(self):
        """启动后台工作线程"""
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self.worker_loop)
            self.worker_thread.start()
            print("Background worker started")
    
    def stop_worker(self):
        """停止后台工作线程"""
        if self.running:
            self.running = False
            if self.worker_thread:
                self.worker_thread.join(timeout=5)
            print("Background worker stopped")

# 示例使用
if __name__ == "__main__":
    processor = RedisTaskProcessor()
    
    try:
        # 启动后台工作进程
        processor.start_worker()
        
        # 添加不同类型的任务
        print("=== 添加任务 ===")
        
        # 联邦学习任务
        fl_task_id = processor.add_task('federated_learning', {
            'model_type': 'CNN',
            'rounds': 3,
            'participants': ['上海一厂', '武汉二厂', '西安三厂']
        })
        
        # 区块链任务
        bc_task_id = processor.add_task('blockchain', {
            'operation': 'create_transaction',
            'from': '0x1234567890abcdef',
            'to': '0xabcdef1234567890',
            'amount': 10.5
        })
        
        # 密码学任务
        crypto_task_id = processor.add_task('crypto', {
            'operation': 'generate_keys',
            'key_type': 'RSA',
            'key_size': 2048
        })
        
        # 等待任务完成
        print("\n=== 等待任务完成 ===")
        tasks = [fl_task_id, bc_task_id, crypto_task_id]
        
        while tasks:
            for task_id in tasks[:]:
                status = processor.get_task_status(task_id)
                if status and status['status'] in ['completed', 'failed']:
                    print(f"\n任务 {task_id} 状态: {status['status']}")
                    
                    result = processor.get_task_result(task_id)
                    if result:
                        print(f"结果: {json.dumps(result['result'], ensure_ascii=False, indent=2)}")
                    
                    tasks.remove(task_id)
            
            if tasks:
                time.sleep(2)
        
        print("\n所有任务完成!")
        
    finally:
        processor.stop_worker()