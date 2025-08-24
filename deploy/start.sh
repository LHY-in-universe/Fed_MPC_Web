#!/bin/bash

# Fed_MPC_Web 生产环境启动脚本

set -e

echo "Starting Fed_MPC_Web in production mode..."

# 检查环境变量
if [ -z "$SECRET_KEY" ]; then
    echo "WARNING: SECRET_KEY not set, using default (not secure for production)"
    export SECRET_KEY="fallback-secret-key-change-this"
fi

if [ -z "$MYSQL_PASSWORD" ]; then
    echo "ERROR: MYSQL_PASSWORD must be set"
    exit 1
fi

# 等待数据库启动
echo "Waiting for database connection..."
python << EOF
import time
import sys
import pymysql
import os

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        connection = pymysql.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            port=int(os.environ.get('MYSQL_PORT', 3306)),
            user=os.environ.get('MYSQL_USER', 'fed_mpc_user'),
            password=os.environ.get('MYSQL_PASSWORD'),
            database=os.environ.get('MYSQL_DB', 'fed_mpc_web')
        )
        connection.close()
        print("Database connection successful!")
        sys.exit(0)
    except Exception as e:
        retry_count += 1
        print(f"Database connection attempt {retry_count}/{max_retries} failed: {e}")
        time.sleep(2)

print("Failed to connect to database after all retries")
sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo "Database connection failed, exiting..."
    exit 1
fi

# 初始化数据库
echo "Initializing database..."
cd /app/backend
python << EOF
from app import create_app
from models.base import db

app = create_app('production')
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
EOF

# 创建必要的目录
mkdir -p /app/logs
mkdir -p /app/uploads
mkdir -p /var/log/supervisor

# 设置权限
chown -R appuser:appuser /app/logs
chown -R appuser:appuser /app/uploads

# 运行数据库迁移（如果需要）
echo "Running database migrations..."
cd /app
# python -m flask db upgrade  # 如果使用Flask-Migrate

# 收集静态文件（如果需要）
echo "Collecting static files..."
# python manage.py collectstatic  # 如果有静态文件收集

# 启动Supervisor管理所有服务
echo "Starting services with Supervisor..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/fed_mpc_web.conf