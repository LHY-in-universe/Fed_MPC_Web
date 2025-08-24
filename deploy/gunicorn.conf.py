"""
Gunicorn配置文件
生产环境Flask应用服务器配置
"""

import multiprocessing
import os

# 服务器绑定
bind = "127.0.0.1:5000"
backlog = 2048

# 工作进程配置
workers = multiprocessing.cpu_count() * 2 + 1  # 推荐配置
worker_class = "gevent"  # 异步工作模式
worker_connections = 1000
max_requests = 1000  # 处理请求数后重启worker
max_requests_jitter = 50  # 随机抖动，避免同时重启

# 超时设置
timeout = 30  # worker超时时间
keepalive = 2  # keep-alive连接时间
graceful_timeout = 30  # 优雅关闭超时

# 服务器机制
preload_app = True  # 预加载应用
daemon = False  # 不以守护进程运行（Docker中使用）
pidfile = "/tmp/gunicorn.pid"
user = "appuser"
group = "appuser"
tmp_upload_dir = None

# 日志配置
loglevel = "info"
accesslog = "/app/logs/gunicorn_access.log"
errorlog = "/app/logs/gunicorn_error.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 安全配置
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# 性能配置
sendfile = True  # 使用sendfile进行文件传输

# SSL配置（如果需要）
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

def when_ready(server):
    """服务器启动后的回调"""
    server.log.info("Fed_MPC_Web server is ready. Listening on: %s", server.address)

def worker_int(worker):
    """worker中断信号处理"""
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    """fork worker之前的回调"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """fork worker之后的回调"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """worker初始化完成后的回调"""
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    """worker异常退出的回调"""
    worker.log.info("Worker aborted (pid: %s)", worker.pid)

def on_exit(server):
    """服务器退出时的回调"""
    server.log.info("Fed_MPC_Web server is shutting down")

# 环境变量配置
raw_env = [
    'FLASK_ENV=production',
    f'SECRET_KEY={os.environ.get("SECRET_KEY", "your-production-secret")}',
    f'MYSQL_HOST={os.environ.get("MYSQL_HOST", "localhost")}',
    f'MYSQL_USER={os.environ.get("MYSQL_USER", "fed_mpc_user")}',
    f'MYSQL_PASSWORD={os.environ.get("MYSQL_PASSWORD", "")}',
    f'MYSQL_DB={os.environ.get("MYSQL_DB", "fed_mpc_web")}',
]