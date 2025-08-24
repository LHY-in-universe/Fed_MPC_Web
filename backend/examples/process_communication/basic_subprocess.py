"""
示例1: 基础子进程控制和通信
演示如何启动Python子进程、传递参数、获取输出
"""

import subprocess
import json
import time
import sys
import os

class ProcessController:
    def __init__(self):
        self.running_processes = {}
        
    def run_python_script(self, script_path, args=None, capture_output=True):
        """运行Python脚本并获取输出"""
        try:
            cmd = [sys.executable, script_path]
            if args:
                cmd.extend([str(arg) for arg in args])
            
            if capture_output:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return {
                    'success': result.returncode == 0,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode
                }
            else:
                # 异步启动进程
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                self.running_processes[process.pid] = process
                return {'pid': process.pid, 'message': 'Process started'}
                
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Process timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_process_status(self, pid):
        """获取进程状态"""
        if pid in self.running_processes:
            process = self.running_processes[pid]
            if process.poll() is None:
                return {'status': 'running', 'pid': pid}
            else:
                stdout, stderr = process.communicate()
                del self.running_processes[pid]
                return {
                    'status': 'completed',
                    'pid': pid,
                    'returncode': process.returncode,
                    'stdout': stdout,
                    'stderr': stderr
                }
        return {'status': 'not_found'}
    
    def terminate_process(self, pid):
        """终止进程"""
        if pid in self.running_processes:
            process = self.running_processes[pid]
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            del self.running_processes[pid]
            return {'success': True, 'message': f'Process {pid} terminated'}
        return {'success': False, 'error': 'Process not found'}

# 示例使用
if __name__ == "__main__":
    controller = ProcessController()
    
    # 创建一个测试脚本
    test_script = """
import sys
import time
import json

name = sys.argv[1] if len(sys.argv) > 1 else "World"
duration = int(sys.argv[2]) if len(sys.argv) > 2 else 3

print(f"Hello {name}! Starting work...")

for i in range(duration):
    print(f"Working... {i+1}/{duration}")
    time.sleep(1)

result = {
    "name": name,
    "duration": duration,
    "message": "Task completed successfully",
    "result": list(range(duration))
}

print(json.dumps(result, ensure_ascii=False))
"""
    
    # 保存测试脚本
    script_path = "worker_script.py"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("=== 同步执行示例 ===")
    result = controller.run_python_script(script_path, ["Alice", "3"])
    print(f"执行结果: {result}")
    
    print("\n=== 异步执行示例 ===")
    async_result = controller.run_python_script(script_path, ["Bob", "5"], capture_output=False)
    print(f"异步启动: {async_result}")
    
    pid = async_result['pid']
    
    # 检查进程状态
    while True:
        status = controller.get_process_status(pid)
        print(f"进程状态: {status['status']}")
        if status['status'] == 'completed':
            print(f"进程输出: {status['stdout']}")
            break
        elif status['status'] == 'not_found':
            break
        time.sleep(1)
    
    # 清理
    if os.path.exists(script_path):
        os.remove(script_path)