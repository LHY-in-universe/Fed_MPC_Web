# Python进程间通信和控制示例

本目录包含了多种Python进程间通信和控制的示例，展示如何在Flask后端中管理和控制其他Python进程。

## 📁 文件结构

```
process_communication/
├── README.md                    # 本说明文档
├── basic_subprocess.py          # 基础子进程控制示例
├── queue_communication.py       # 队列进程通信示例
├── redis_communication.py      # Redis消息队列示例
├── flask_process_manager.py     # Flask集成进程管理器
└── test_examples.py            # 测试所有示例的脚本
```

## 🚀 快速开始

### 1. 运行单个示例

```bash
# 基础子进程控制
python basic_subprocess.py

# 队列进程通信
python queue_communication.py

# Redis进程通信（需要Redis或使用内置Mock）
python redis_communication.py

# Flask进程管理器
python flask_process_manager.py
```

### 2. 运行所有测试

```bash
python test_examples.py
```

## 📋 示例详解

### 1. basic_subprocess.py - 基础子进程控制

**功能特点:**
- 同步和异步执行Python脚本
- 获取进程输出和错误信息
- 进程状态监控和终止
- 参数传递和结果获取

**使用场景:**
- 执行独立的计算任务
- 调用外部Python工具
- 批处理任务管理

**核心API:**
```python
controller = ProcessController()

# 同步执行
result = controller.run_python_script("script.py", ["arg1", "arg2"])

# 异步执行
async_result = controller.run_python_script("script.py", args, capture_output=False)
pid = async_result['pid']

# 检查状态
status = controller.get_process_status(pid)

# 终止进程
controller.terminate_process(pid)
```

### 2. queue_communication.py - 队列进程通信

**功能特点:**
- 使用multiprocessing.Queue进行进程间通信
- 多个工作进程并行处理任务
- 任务分发和结果收集
- 支持不同类型的任务处理

**使用场景:**
- CPU密集型任务并行处理
- 大数据批处理
- AI模型训练和推理
- 数据预处理管道

**核心API:**
```python
processor = QueueBasedProcessor()

# 启动工作进程
processor.start_workers(3)

# 添加任务
processor.add_task('task_1', 'calculation', {'numbers': [1,2,3], 'operation': 'sum'})
processor.add_task('task_2', 'ai_training', {'model_type': 'cnn', 'epochs': 5})

# 获取结果
results = processor.get_results()

# 关闭
processor.shutdown()
```

### 3. redis_communication.py - Redis消息队列

**功能特点:**
- 使用Redis作为消息队列
- 支持任务持久化和恢复
- 分布式任务处理
- 任务状态跟踪和管理

**使用场景:**
- 分布式系统任务调度
- 微服务间异步通信
- 任务队列和作业调度
- 跨机器进程协调

**核心API:**
```python
processor = RedisTaskProcessor()

# 启动后台工作进程
processor.start_worker()

# 添加任务
task_id = processor.add_task('federated_learning', {
    'model_type': 'CNN',
    'rounds': 3,
    'participants': ['client1', 'client2']
})

# 获取状态和结果
status = processor.get_task_status(task_id)
result = processor.get_task_result(task_id)

# 停止
processor.stop_worker()
```

### 4. flask_process_manager.py - Flask集成进程管理器

**功能特点:**
- Flask Web API集成
- RESTful任务管理接口
- 实时任务状态更新
- 多用户任务隔离
- Web界面友好的API

**使用场景:**
- Web应用后端任务处理
- API服务集成
- 用户任务管理
- 实时进度反馈

**API接口:**
```http
POST /api/tasks          # 创建任务
GET  /api/tasks/{id}     # 获取任务状态
GET  /api/tasks          # 获取所有任务
DELETE /api/tasks/{id}   # 取消任务
GET  /api/health         # 健康检查
```

**使用示例:**
```python
import requests

# 创建AI训练任务
task_data = {
    'task_type': 'ai_training',
    'data': {'project_name': '故障检测', 'epochs': 10},
    'user_id': 'user123'
}
response = requests.post('http://127.0.0.1:5001/api/tasks', json=task_data)
task_id = response.json()['task_id']

# 监控任务进度
status = requests.get(f'http://127.0.0.1:5001/api/tasks/{task_id}')
print(status.json())
```

## 🔧 技术方案对比

| 方案 | 适用场景 | 优点 | 缺点 | 复杂度 |
|------|----------|------|------|--------|
| subprocess | 简单任务执行 | 简单直接，无依赖 | 无持久化，难扩展 | 低 |
| multiprocessing.Queue | CPU密集型任务 | 高性能，内置支持 | 单机限制，无持久化 | 中 |
| Redis队列 | 分布式任务 | 持久化，可扩展 | 需要Redis服务 | 中 |
| Flask集成 | Web应用 | REST API，易集成 | 需要Web框架 | 高 |

## 📊 性能对比

基于测试脚本的性能数据：

- **单进程**: 基准性能，CPU利用率低
- **多进程**: 2-4倍性能提升（CPU密集型任务）
- **Redis队列**: 支持分布式，延迟稍高
- **Flask集成**: 额外HTTP开销，便于管理

## 🔍 监控和调试

### 日志记录
所有示例都包含详细的日志输出，便于调试和监控。

### 状态检查
```python
# 检查进程状态
status = get_process_status(pid)
print(f"Status: {status['status']}")

# 检查任务队列
queue_size = get_queue_size()
print(f"Queue size: {queue_size}")
```

### 性能监控
```python
# 监控CPU和内存使用
import psutil
process = psutil.Process(pid)
print(f"CPU: {process.cpu_percent()}%")
print(f"Memory: {process.memory_info().rss / 1024 / 1024:.2f}MB")
```

## ⚠️ 注意事项

### 1. 资源管理
- 确保正确关闭进程和连接
- 避免进程泄漏和资源占用
- 设置合理的超时时间

### 2. 错误处理
- 捕获和处理进程异常
- 提供友好的错误信息
- 实现重试和恢复机制

### 3. 安全考虑
- 验证输入参数
- 限制进程权限
- 防止代码注入攻击

### 4. 扩展性
- 设计可扩展的任务类型
- 支持动态添加工作进程
- 考虑分布式部署

## 📚 扩展阅读

- [Python multiprocessing 官方文档](https://docs.python.org/3/library/multiprocessing.html)
- [subprocess 模块文档](https://docs.python.org/3/library/subprocess.html)
- [Redis Python 客户端](https://redis-py.readthedocs.io/)
- [Flask 异步任务处理](https://flask.palletsprojects.com/en/2.0.x/patterns/celery/)

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这些示例！