# Fed_MPC_Web 部署指南

本文档详细说明如何将Fed_MPC_Web联邦学习平台部署到生产服务器。

## 📋 目录结构

```
deploy/
├── README.md              # 本部署指南
├── production_config.py   # 生产环境配置
├── requirements-prod.txt  # 生产环境依赖
├── nginx.conf            # Nginx配置
├── gunicorn.conf.py      # Gunicorn配置
├── supervisord.conf      # Supervisor配置
├── start.sh             # 容器启动脚本
└── deploy.sh            # 自动化部署脚本
```

## 🚀 快速部署

### 方法1: Docker Compose (推荐)

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd Fed_MPC_Web

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填写数据库密码等配置

# 3. 启动所有服务
docker-compose up -d

# 4. 检查服务状态
docker-compose ps
curl http://localhost/api/health
```

### 方法2: 自动化部署脚本

```bash
# 本地部署
./deploy/deploy.sh production --local

# 远程部署
./deploy/deploy.sh production root your-server.com --remote
```

## 🔧 详细部署步骤

### 1. 服务器准备

**最低系统要求:**
- OS: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- CPU: 2核心
- RAM: 4GB
- 存储: 20GB
- 网络: 公网IP + 开放80,443端口

**安装Docker和Docker Compose:**

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# CentOS/RHEL
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. 项目部署

```bash
# 1. 在服务器上创建项目目录
sudo mkdir -p /opt/fed_mpc_web
cd /opt/fed_mpc_web

# 2. 上传项目文件
# 方式A: Git克隆
git clone <your-repo-url> .

# 方式B: 本地上传
scp -r ./Fed_MPC_Web/* user@server:/opt/fed_mpc_web/

# 3. 配置环境变量
cp .env.example .env
nano .env  # 编辑配置

# 4. 设置权限
sudo chown -R $USER:$USER /opt/fed_mpc_web
chmod +x deploy/deploy.sh deploy/start.sh

# 5. 启动服务
docker-compose up -d
```

### 3. 环境变量配置

编辑 `.env` 文件，必须配置的变量：

```bash
# 安全配置 (必须修改)
SECRET_KEY=your-super-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-different-from-above

# 数据库配置 (必须配置)
MYSQL_ROOT_PASSWORD=your-root-password
MYSQL_PASSWORD=your-secure-database-password

# 域名配置
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# 邮件配置 (可选)
MAIL_USERNAME=your-email@domain.com
MAIL_PASSWORD=your-app-specific-password
```

### 4. SSL证书配置 (HTTPS)

```bash
# 使用Let's Encrypt免费证书
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔍 服务管理

### Docker Compose 命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f app
docker-compose logs -f mysql

# 重启服务
docker-compose restart app

# 停止所有服务
docker-compose down

# 更新服务
docker-compose pull
docker-compose up -d --force-recreate

# 进入容器
docker-compose exec app bash
docker-compose exec mysql mysql -u root -p
```

### 数据库管理

```bash
# 备份数据库
docker-compose exec mysql mysqldump -u fed_mpc_user -p fed_mpc_web > backup_$(date +%Y%m%d).sql

# 恢复数据库
docker-compose exec -T mysql mysql -u fed_mpc_user -p fed_mpc_web < backup_20240101.sql

# 连接数据库
docker-compose exec mysql mysql -u fed_mpc_user -p fed_mpc_web
```

### 应用管理

```bash
# 重载应用配置
docker-compose exec app supervisorctl reload

# 查看应用进程
docker-compose exec app supervisorctl status

# 重启特定进程
docker-compose exec app supervisorctl restart fed_mpc_web

# 查看应用日志
docker-compose exec app tail -f /app/logs/gunicorn_access.log
```

## 📊 监控和维护

### 健康检查

```bash
# API健康检查
curl http://your-domain.com/api/health

# 数据库连接检查
docker-compose exec mysql mysqladmin ping -u fed_mpc_user -p

# 服务器资源监控
docker stats
```

### 日志管理

```bash
# 查看应用日志
docker-compose logs -f --tail=100 app

# 查看Nginx日志
docker-compose exec app tail -f /var/log/nginx/fed_mpc_web_access.log

# 查看系统日志
docker-compose exec app tail -f /var/log/supervisor/fed_mpc_web.log
```

### 备份策略

```bash
# 自动化备份脚本
cat > /opt/fed_mpc_web/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/fed_mpc_web/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
docker-compose exec -T mysql mysqldump -u fed_mpc_user -p$MYSQL_PASSWORD fed_mpc_web > $BACKUP_DIR/db_$DATE.sql

# 备份上传文件
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz uploads/

# 清理7天前的备份
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/fed_mpc_web/backup.sh

# 设置定时备份
crontab -e
# 添加: 0 2 * * * /opt/fed_mpc_web/backup.sh >> /opt/fed_mpc_web/backup.log 2>&1
```

## 🔒 安全配置

### 防火墙设置

```bash
# Ubuntu UFW
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# CentOS/RHEL firewalld
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### Nginx安全加固

```bash
# 隐藏Nginx版本
echo 'server_tokens off;' >> /etc/nginx/nginx.conf

# 限制请求大小
echo 'client_max_body_size 100M;' >> /etc/nginx/nginx.conf

# 添加安全头
# (已包含在nginx.conf中)
```

### 数据库安全

```bash
# MySQL安全脚本
docker-compose exec mysql mysql_secure_installation

# 限制数据库访问
# 确保MySQL只监听内部网络
```

## 📈 性能优化

### 应用性能

```bash
# 调整Gunicorn工作进程数
# 编辑 deploy/gunicorn.conf.py
workers = multiprocessing.cpu_count() * 2 + 1

# 调整数据库连接池
# 编辑 deploy/production_config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'max_overflow': 30
}
```

### 系统性能

```bash
# 调整系统限制
echo '* soft nofile 65536' >> /etc/security/limits.conf
echo '* hard nofile 65536' >> /etc/security/limits.conf

# 调整内核参数
echo 'net.core.somaxconn = 65535' >> /etc/sysctl.conf
sysctl -p
```

## 🚨 故障排除

### 常见问题

**1. 容器启动失败**
```bash
# 检查日志
docker-compose logs app

# 检查配置文件
docker-compose config
```

**2. 数据库连接失败**
```bash
# 检查数据库状态
docker-compose exec mysql mysqladmin ping

# 检查环境变量
docker-compose exec app env | grep MYSQL
```

**3. Nginx 502错误**
```bash
# 检查上游服务
curl http://127.0.0.1:5000/api/health

# 检查Nginx配置
docker-compose exec app nginx -t
```

**4. 权限问题**
```bash
# 修复文件权限
docker-compose exec app chown -R appuser:appuser /app/logs
docker-compose exec app chown -R appuser:appuser /app/uploads
```

### 紧急恢复

```bash
# 回滚到前一版本
./deploy/deploy.sh --rollback

# 从备份恢复数据库
docker-compose exec -T mysql mysql -u fed_mpc_user -p fed_mpc_web < backups/latest_backup.sql

# 重启所有服务
docker-compose down && docker-compose up -d
```

## 📞 技术支持

- 项目地址: [GitHub Repository]
- 文档地址: [Documentation URL]
- 问题反馈: [Issues URL]
- 技术交流: [Contact Information]

## 📝 更新日志

- v1.0.0: 初始版本，支持Docker部署
- v1.1.0: 添加监控和备份功能
- v1.2.0: 增加SSL和安全配置

---

**部署完成后，请访问 `http://your-domain.com` 验证系统正常运行！**