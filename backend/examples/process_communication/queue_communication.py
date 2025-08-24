"""
示例2: 使用队列进行进程间通信
演示如何使用multiprocessing.Queue在进程间传递数据
"""

import multiprocessing as mp
import json
import time
import random
from datetime import datetime

class QueueBasedProcessor:
    def __init__(self):
        self.input_queue = mp.Queue()
        self.output_queue = mp.Queue()
        self.processes = []
        
    def worker_process(self, worker_id, input_queue, output_queue):
        """工作进程函数"""
        print(f"Worker {worker_id} started")
        
        while True:
            try:
                # 从输入队列获取任务
                task = input_queue.get(timeout=10)
                
                if task is None:  # 终止信号
                    print(f"Worker {worker_id} received termination signal")
                    break
                
                print(f"Worker {worker_id} processing task: {task['task_id']}")
                
                # 模拟处理任务
                task_type = task.get('type', 'default')
                
                if task_type == 'calculation':
                    result = self.do_calculation(task['data'])
                elif task_type == 'data_processing':
                    result = self.process_data(task['data'])
                elif task_type == 'ai_training':
                    result = self.simulate_ai_training(task['data'])
                else:
                    result = {'error': f'Unknown task type: {task_type}'}
                
                # 准备结果
                response = {
                    'task_id': task['task_id'],
                    'worker_id': worker_id,
                    'result': result,
                    'processed_at': datetime.now().isoformat(),
                    'processing_time': random.uniform(0.5, 3.0)
                }
                
                # 发送结果到输出队列
                output_queue.put(response)
                print(f"Worker {worker_id} completed task: {task['task_id']}")
                
            except Exception as e:
                error_response = {
                    'task_id': task.get('task_id', 'unknown') if 'task' in locals() else 'unknown',
                    'worker_id': worker_id,
                    'error': str(e),
                    'processed_at': datetime.now().isoformat()
                }
                output_queue.put(error_response)
                
        print(f"Worker {worker_id} finished")
    
    def do_calculation(self, data):
        """模拟数学计算"""
        numbers = data.get('numbers', [1, 2, 3, 4, 5])
        operation = data.get('operation', 'sum')
        
        if operation == 'sum':
            result = sum(numbers)
        elif operation == 'multiply':
            result = 1
            for n in numbers:
                result *= n
        elif operation == 'average':
            result = sum(numbers) / len(numbers) if numbers else 0
        else:
            result = None
            
        time.sleep(random.uniform(0.5, 2.0))  # 模拟计算时间
        return {'operation': operation, 'result': result, 'input_size': len(numbers)}
    
    def process_data(self, data):
        """模拟数据处理"""
        dataset = data.get('dataset', [])
        processing_type = data.get('processing_type', 'clean')
        
        time.sleep(random.uniform(1.0, 3.0))  # 模拟处理时间
        
        if processing_type == 'clean':
            processed_count = len([x for x in dataset if x is not None])
        elif processing_type == 'transform':
            processed_count = len(dataset) * 2  # 假设转换后数据翻倍
        else:
            processed_count = len(dataset)
            
        return {
            'processing_type': processing_type,
            'original_size': len(dataset),
            'processed_size': processed_count,
            'success_rate': random.uniform(0.85, 0.99)
        }
    
    def simulate_ai_training(self, data):
        """模拟AI训练"""
        model_type = data.get('model_type', 'neural_network')
        epochs = data.get('epochs', 10)
        
        # 模拟训练过程
        training_results = []
        for epoch in range(epochs):
            accuracy = random.uniform(0.6, 0.95)
            loss = random.uniform(0.05, 0.4)
            training_results.append({
                'epoch': epoch + 1,
                'accuracy': round(accuracy, 4),
                'loss': round(loss, 4)
            })
            time.sleep(0.1)  # 模拟训练时间
        
        final_accuracy = training_results[-1]['accuracy']
        return {
            'model_type': model_type,
            'epochs_completed': epochs,
            'final_accuracy': final_accuracy,
            'final_loss': training_results[-1]['loss'],
            'training_history': training_results
        }
    
    def start_workers(self, num_workers=3):
        """启动工作进程"""
        for i in range(num_workers):
            p = mp.Process(
                target=self.worker_process,
                args=(i, self.input_queue, self.output_queue)
            )
            p.start()
            self.processes.append(p)
        print(f"Started {num_workers} workers")
    
    def add_task(self, task_id, task_type, data):
        """添加任务到队列"""
        task = {
            'task_id': task_id,
            'type': task_type,
            'data': data,
            'submitted_at': datetime.now().isoformat()
        }
        self.input_queue.put(task)
        print(f"Added task {task_id} to queue")
    
    def get_results(self, timeout=5):
        """获取处理结果"""
        results = []
        try:
            while True:
                result = self.output_queue.get(timeout=timeout)
                results.append(result)
        except:
            pass  # 队列为空或超时
        return results
    
    def shutdown(self):
        """关闭所有工作进程"""
        # 发送终止信号
        for _ in self.processes:
            self.input_queue.put(None)
        
        # 等待进程结束
        for p in self.processes:
            p.join(timeout=10)
            if p.is_alive():
                p.terminate()
        
        print("All workers stopped")

# 示例使用
if __name__ == "__main__":
    processor = QueueBasedProcessor()
    
    try:
        # 启动3个工作进程
        processor.start_workers(3)
        
        # 添加不同类型的任务
        tasks = [
            ('task_1', 'calculation', {'numbers': [1, 2, 3, 4, 5], 'operation': 'sum'}),
            ('task_2', 'calculation', {'numbers': [2, 4, 6, 8], 'operation': 'multiply'}),
            ('task_3', 'data_processing', {'dataset': list(range(100)), 'processing_type': 'clean'}),
            ('task_4', 'ai_training', {'model_type': 'cnn', 'epochs': 5}),
            ('task_5', 'data_processing', {'dataset': list(range(50)), 'processing_type': 'transform'}),
        ]
        
        # 提交任务
        for task_id, task_type, data in tasks:
            processor.add_task(task_id, task_type, data)
        
        print("\n等待任务完成...")
        time.sleep(8)  # 等待任务处理
        
        # 获取结果
        results = processor.get_results()
        print(f"\n收到 {len(results)} 个结果:")
        
        for result in results:
            if 'error' in result:
                print(f"任务 {result['task_id']} 失败: {result['error']}")
            else:
                print(f"任务 {result['task_id']} 完成: {json.dumps(result['result'], ensure_ascii=False, indent=2)}")
        
    finally:
        processor.shutdown()