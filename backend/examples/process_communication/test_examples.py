"""
测试所有进程通信示例的脚本
运行此脚本来测试各种进程间通信方法
"""

import sys
import os
import subprocess
import time
import requests
import json
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor

def test_basic_subprocess():
    """测试基础子进程控制"""
    print("\n" + "="*50)
    print("测试1: 基础子进程控制")
    print("="*50)
    
    try:
        result = subprocess.run([
            sys.executable, 'basic_subprocess.py'
        ], capture_output=True, text=True, timeout=30)
        
        print("输出:")
        print(result.stdout)
        
        if result.stderr:
            print("错误:")
            print(result.stderr)
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ 测试超时")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_queue_communication():
    """测试队列通信"""
    print("\n" + "="*50)
    print("测试2: 队列进程通信")
    print("="*50)
    
    try:
        result = subprocess.run([
            sys.executable, 'queue_communication.py'
        ], capture_output=True, text=True, timeout=60)
        
        print("输出:")
        print(result.stdout[-2000:])  # 显示最后2000个字符
        
        if result.stderr:
            print("错误:")
            print(result.stderr[-1000:])
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ 测试超时")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_redis_communication():
    """测试Redis通信"""
    print("\n" + "="*50)
    print("测试3: Redis进程通信")
    print("="*50)
    
    try:
        result = subprocess.run([
            sys.executable, 'redis_communication.py'
        ], capture_output=True, text=True, timeout=45)
        
        print("输出:")
        print(result.stdout[-2000:])
        
        if result.stderr:
            print("错误:")
            print(result.stderr[-1000:])
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ 测试超时")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_flask_process_manager():
    """测试Flask进程管理器"""
    print("\n" + "="*50)
    print("测试4: Flask进程管理器")
    print("="*50)
    
    # 启动Flask服务器
    flask_process = None
    try:
        print("启动Flask服务器...")
        flask_process = subprocess.Popen([
            sys.executable, 'flask_process_manager.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # 等待服务器启动
        time.sleep(3)
        
        # 测试健康检查
        print("测试健康检查...")
        response = requests.get('http://127.0.0.1:5001/api/health')
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
        
        # 创建不同类型的任务
        tasks = []
        
        # AI训练任务
        print("\n创建AI训练任务...")
        ai_task_data = {
            'task_type': 'ai_training',
            'data': {
                'project_name': '故障检测模型',
                'model_type': 'CNN',
                'epochs': 5,
                'batch_size': 32
            },
            'user_id': 'test_user'
        }
        
        response = requests.post('http://127.0.0.1:5001/api/tasks', json=ai_task_data)
        if response.status_code == 200:
            task_id = response.json()['task_id']
            tasks.append(('AI训练', task_id))
            print(f"✅ AI任务创建成功: {task_id}")
        else:
            print("❌ AI任务创建失败")
        
        # 区块链任务
        print("创建区块链任务...")
        bc_task_data = {
            'task_type': 'blockchain',
            'data': {
                'operation': 'create_transaction',
                'from': '0x1234567890abcdef',
                'to': '0xfedcba0987654321',
                'amount': 5.0
            },
            'user_id': 'test_user'
        }
        
        response = requests.post('http://127.0.0.1:5001/api/tasks', json=bc_task_data)
        if response.status_code == 200:
            task_id = response.json()['task_id']
            tasks.append(('区块链交易', task_id))
            print(f"✅ 区块链任务创建成功: {task_id}")
        else:
            print("❌ 区块链任务创建失败")
        
        # 密码学任务
        print("创建密码学任务...")
        crypto_task_data = {
            'task_type': 'crypto',
            'data': {
                'operation': 'generate_keys',
                'key_type': 'RSA',
                'key_size': 2048
            },
            'user_id': 'test_user'
        }
        
        response = requests.post('http://127.0.0.1:5001/api/tasks', json=crypto_task_data)
        if response.status_code == 200:
            task_id = response.json()['task_id']
            tasks.append(('密钥生成', task_id))
            print(f"✅ 密码学任务创建成功: {task_id}")
        else:
            print("❌ 密码学任务创建失败")
        
        # 监控任务执行
        print("\n监控任务执行...")
        completed_tasks = 0
        max_wait = 60  # 最多等待60秒
        wait_time = 0
        
        while completed_tasks < len(tasks) and wait_time < max_wait:
            for task_name, task_id in tasks:
                response = requests.get(f'http://127.0.0.1:5001/api/tasks/{task_id}')
                if response.status_code == 200:
                    task_status = response.json()
                    status = task_status.get('status', 'unknown')
                    progress = task_status.get('progress', 0)
                    
                    if status == 'completed':
                        print(f"✅ {task_name} 完成")
                        print(f"   结果: {json.dumps(task_status.get('result', {}), indent=4, ensure_ascii=False)}")
                        completed_tasks += 1
                    elif status == 'failed':
                        print(f"❌ {task_name} 失败: {task_status.get('error', 'Unknown error')}")
                        completed_tasks += 1
                    elif status in ['running', 'processing']:
                        current_step = task_status.get('current_step', '')
                        print(f"🔄 {task_name} 运行中 ({progress}%) - {current_step}")
                    else:
                        print(f"⏳ {task_name} 等待中")
            
            time.sleep(2)
            wait_time += 2
            print("---")
        
        # 获取所有任务
        print("\n获取所有任务...")
        response = requests.get('http://127.0.0.1:5001/api/tasks?user_id=test_user')
        if response.status_code == 200:
            all_tasks = response.json()
            print(f"✅ 用户任务总数: {all_tasks['total']}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Flask服务器")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    finally:
        # 关闭Flask服务器
        if flask_process:
            flask_process.terminate()
            try:
                flask_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                flask_process.kill()
            print("Flask服务器已关闭")

def run_performance_test():
    """运行性能测试"""
    print("\n" + "="*50)
    print("性能测试: 并发任务处理")
    print("="*50)
    
    def cpu_intensive_task(n):
        """CPU密集型任务"""
        result = 0
        for i in range(n):
            result += i * i
        return result
    
    print("测试多进程处理CPU密集型任务...")
    
    # 单进程测试
    start_time = time.time()
    single_results = []
    for i in range(4):
        result = cpu_intensive_task(100000)
        single_results.append(result)
    single_time = time.time() - start_time
    
    # 多进程测试
    start_time = time.time()
    with mp.Pool(processes=4) as pool:
        multi_results = pool.map(cpu_intensive_task, [100000] * 4)
    multi_time = time.time() - start_time
    
    print(f"单进程时间: {single_time:.2f}秒")
    print(f"多进程时间: {multi_time:.2f}秒")
    print(f"性能提升: {single_time/multi_time:.2f}x")
    
    # 线程池测试
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=4) as executor:
        thread_results = list(executor.map(cpu_intensive_task, [100000] * 4))
    thread_time = time.time() - start_time
    
    print(f"线程池时间: {thread_time:.2f}秒")
    
    return True

def main():
    """主测试函数"""
    print("🚀 开始进程通信示例测试")
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    
    # 切换到示例目录
    examples_dir = '/Users/lhy/Desktop/Git/Fed_MPC_Web/backend/examples/process_communication'
    if os.path.exists(examples_dir):
        os.chdir(examples_dir)
        print(f"切换到目录: {examples_dir}")
    else:
        print(f"❌ 示例目录不存在: {examples_dir}")
        return
    
    test_results = []
    
    # 运行所有测试
    test_functions = [
        ('基础子进程控制', test_basic_subprocess),
        ('队列进程通信', test_queue_communication),
        ('Redis进程通信', test_redis_communication),
        ('Flask进程管理器', test_flask_process_manager),
        ('性能测试', run_performance_test)
    ]
    
    for test_name, test_func in test_functions:
        try:
            print(f"\n🧪 运行测试: {test_name}")
            result = test_func()
            test_results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
                
        except KeyboardInterrupt:
            print(f"\n⏹️  测试被用户中断")
            break
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            test_results.append((test_name, False))
    
    # 输出测试总结
    print("\n" + "="*50)
    print("📊 测试总结")
    print("="*50)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:.<30} {status}")
    
    print("-" * 50)
    print(f"总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试都通过了!")
    else:
        print(f"⚠️  有 {total - passed} 个测试失败")

if __name__ == "__main__":
    main()