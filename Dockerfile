# Fed_MPC_Web 生产环境Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    DEBIAN_FRONTEND=noninteractive

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    pkg-config \
    default-libmysqlclient-dev \
    curl \
    wget \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .
COPY deploy/requirements-prod.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements-prod.txt

# 创建必要的目录
RUN mkdir -p /app/logs /app/uploads /app/static /var/log/supervisor

# 复制应用代码
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY database/ ./database/
COPY deploy/ ./deploy/

# 复制配置文件
COPY deploy/nginx.conf /etc/nginx/sites-available/fed_mpc_web
COPY deploy/supervisord.conf /etc/supervisor/conf.d/fed_mpc_web.conf
COPY deploy/gunicorn.conf.py ./

# 设置Nginx
RUN ln -sf /etc/nginx/sites-available/fed_mpc_web /etc/nginx/sites-enabled/ \
    && rm -f /etc/nginx/sites-enabled/default

# 创建启动脚本
COPY deploy/start.sh ./
RUN chmod +x start.sh

# 设置权限
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser /var/log/supervisor

# 暴露端口
EXPOSE 80 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost/api/health || exit 1

# 切换到非root用户
USER appuser

# 启动命令
CMD ["./start.sh"]