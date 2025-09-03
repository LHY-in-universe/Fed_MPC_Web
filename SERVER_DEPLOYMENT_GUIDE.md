# Fed_MPC_Web 服务器部署完整指南

## 🚀 快速开始

Fed_MPC_Web 支持多种Web引擎部署方案，您可以根据自己的需求选择最适合的部署方式。

### 📦 方案一：一键打包部署（推荐）

```bash
# 1. 执行打包脚本
./deploy/package-for-deployment.sh

# 2. 上传生成的压缩包到服务器
scp fed_mpc_web_deployment_*.tar.gz user@your-server:/opt/

# 3. 在服务器上解压并部署
tar -xzf fed_mpc_web_deployment_*.tar.gz
cd fed_mpc_web_deployment_*
./quick-deploy.sh
```

### 🐳 方案二：Docker部署（推荐）

```bash
# 直接使用Docker部署
./deploy/web-engine-deploy.sh docker --domain your-domain.com --ssl
```

### 🌐 方案三：选择Web引擎部署

```bash
# Nginx + Gunicorn （生产推荐）
./deploy/web-engine-deploy.sh nginx --domain your-domain.com --port 80 --ssl

# Apache + mod_wsgi
./deploy/web-engine-deploy.sh apache --domain your-domain.com --ssl

# 独立Python服务器（开发/测试）
./deploy/web-engine-deploy.sh standalone --port 5000
```

---

## 🎯 部署方案对比

| 方案 | 优势 | 适用场景 | 难度 |
|------|------|----------|------|
| **Docker** | 环境隔离、一致性、易维护 | 生产环境、微服务架构 | ⭐⭐ |
| **Nginx + Gunicorn** | 高性能、成熟稳定 | 高并发生产环境 | ⭐⭐⭐ |
| **Apache + mod_wsgi** | 功能丰富、配置灵活 | 企业级环境、复杂需求 | ⭐⭐⭐⭐ |
| **独立Python** | 简单直接、快速启动 | 开发环境、小规模部署 | ⭐ |

---

## 📋 系统要求

### 最低配置
- **CPU**: 1核心 (推荐2核心)
- **内存**: 2GB RAM (推荐4GB)
- **存储**: 10GB 可用空间
- **网络**: 公网IP + 开放80/443端口
- **系统**: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+

### 推荐配置
- **CPU**: 4核心
- **内存**: 8GB RAM
- **存储**: 50GB SSD
- **网络**: 100Mbps带宽

---

## 🔧 详细部署步骤

### 1️⃣ 服务器准备

#### 更新系统
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

#### 安装基础工具
```bash
# Ubuntu/Debian
sudo apt install -y curl wget git unzip software-properties-common

# CentOS/RHEL  
sudo yum install -y curl wget git unzip epel-release
```

#### 配置防火墙
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

### 2️⃣ 选择部署方案

#### 🐳 方案A：Docker部署

**安装Docker**
```bash
# 一键安装脚本
curl -fsSL https://get.docker.com | sh

# 添加用户到docker组
sudo usermod -aG docker $USER

# 重新登录或执行
newgrp docker
```

**安装Docker Compose**
```bash
# 下载最新版本
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

**执行部署**
```bash
# 克隆项目
git clone <your-repo-url> /opt/fed_mpc_web
cd /opt/fed_mpc_web

# 配置环境变量
cp .env.example .env
nano .env  # 编辑必要配置

# 一键部署
./deploy/web-engine-deploy.sh docker --domain your-domain.com --ssl
```

#### 🌐 方案B：Nginx + Gunicorn部署

**安装Python和依赖**
```bash
# Ubuntu/Debian
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential
sudo apt install -y nginx

# CentOS/RHEL
sudo yum install -y python3 python3-pip python3-devel gcc gcc-c++ make
sudo yum install -y nginx
```

**执行部署**
```bash
# 克隆项目
git clone <your-repo-url> /opt/fed_mpc_web
cd /opt/fed_mpc_web

# 执行Nginx部署
./deploy/web-engine-deploy.sh nginx --domain your-domain.com --port 80 --ssl
```

#### 🔧 方案C：Apache + mod_wsgi部署

**安装Apache和依赖**
```bash
# Ubuntu/Debian
sudo apt install -y apache2 libapache2-mod-wsgi-py3
sudo apt install -y python3 python3-pip python3-venv python3-dev

# CentOS/RHEL
sudo yum install -y httpd python3-mod_wsgi
sudo yum install -y python3 python3-pip python3-devel
```

**执行部署**
```bash
# 克隆项目  
git clone <your-repo-url> /opt/fed_mpc_web
cd /opt/fed_mpc_web

# 执行Apache部署
./deploy/web-engine-deploy.sh apache --domain your-domain.com --ssl
```

### 3️⃣ SSL/HTTPS配置

#### 使用Let's Encrypt免费证书

**安装Certbot**
```bash
# Ubuntu/Debian
sudo apt install -y certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install -y certbot python3-certbot-nginx
```

**获取证书**
```bash
# 为域名获取证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 设置自动续期
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### 4️⃣ 环境配置

#### 核心环境变量配置

编辑 `.env` 文件，配置以下必要参数：

```bash
# 安全密钥 (必须修改)
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-different-from-secret-key

# 数据库配置 (必须配置)
MYSQL_ROOT_PASSWORD=your-strong-root-password  
MYSQL_PASSWORD=your-strong-database-password

# 域名配置
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# 可选配置
MAIL_USERNAME=your-email@domain.com
MAIL_PASSWORD=your-app-specific-password
```

#### 生成安全密钥

```bash
# 生成SECRET_KEY
python3 -c "import secrets; print(secrets.token_hex(32))"

# 生成JWT_SECRET_KEY  
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## 🔍 部署验证

### 检查服务状态

#### Docker部署
```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f app

# 健康检查
curl http://localhost/api/health
```

#### Nginx/Apache部署
```bash
# 查看服务状态
sudo systemctl status fed-mpc-web
sudo systemctl status nginx  # 或 apache2

# 查看日志
sudo journalctl -u fed-mpc-web -f

# 健康检查
curl http://localhost/api/health
```

### 功能测试

1. **主页访问**: http://your-domain.com
2. **API测试**: http://your-domain.com/api/health
3. **模块测试**: 
   - P2P AI训练: http://your-domain.com/p2pai/
   - EdgeAI管理: http://your-domain.com/edgeai/
   - 区块链金融: http://your-domain.com/blockchain/
   - 密钥加密: http://your-domain.com/crypto/

---

## 📊 监控和维护

### 日志管理

#### Docker环境
```bash
# 查看应用日志
docker-compose logs -f app

# 查看数据库日志  
docker-compose logs -f mysql

# 导出日志
docker-compose logs app > app.log
```

#### 传统部署
```bash
# 应用日志
sudo tail -f /opt/fed_mpc_web/logs/gunicorn_access.log
sudo tail -f /opt/fed_mpc_web/logs/gunicorn_error.log

# 系统日志
sudo journalctl -u fed-mpc-web -f

# Web服务器日志
sudo tail -f /var/log/nginx/access.log  # Nginx
sudo tail -f /var/log/apache2/access.log  # Apache
```

### 性能监控

#### 资源监控
```bash
# 系统资源
htop
free -h
df -h

# Docker资源 (Docker部署)
docker stats

# 网络连接
ss -tuln
```

#### 应用监控
```bash
# 进程监控
ps aux | grep gunicorn
ps aux | grep python

# 端口监听
netstat -tlnp | grep :80
```

### 数据备份

#### 自动备份脚本
```bash
#!/bin/bash
# 保存为 /opt/fed_mpc_web/backup.sh

BACKUP_DIR="/opt/fed_mpc_web/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 数据库备份 (Docker环境)
if command -v docker-compose &> /dev/null; then
    docker-compose exec -T mysql mysqldump -u fed_mpc_user -p$MYSQL_PASSWORD fed_mpc_web > $BACKUP_DIR/db_$DATE.sql
else
    # 传统环境数据库备份
    mysqldump -u fed_mpc_user -p fed_mpc_web > $BACKUP_DIR/db_$DATE.sql
fi

# 文件备份
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz uploads/ 2>/dev/null || true

# 清理7天前的备份
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

#### 设置定时备份
```bash
# 添加到crontab
chmod +x /opt/fed_mpc_web/backup.sh
crontab -e

# 添加以下行 (每天凌晨2点备份)
0 2 * * * /opt/fed_mpc_web/backup.sh >> /opt/fed_mpc_web/backup.log 2>&1
```

---

## 🚨 故障排除

### 常见问题

#### 1. 服务无法启动
```bash
# 检查端口占用
sudo netstat -tlnp | grep :80

# 检查配置文件语法
nginx -t  # Nginx
apache2ctl configtest  # Apache

# 查看详细错误日志
sudo journalctl -u fed-mpc-web --no-pager
```

#### 2. 数据库连接失败
```bash
# 检查数据库服务
sudo systemctl status mysql
docker-compose exec mysql mysqladmin ping  # Docker环境

# 检查数据库配置
grep MYSQL .env

# 测试数据库连接
mysql -u fed_mpc_user -p -h localhost fed_mpc_web
```

#### 3. SSL证书问题
```bash
# 检查证书状态
sudo certbot certificates

# 手动续期证书
sudo certbot renew

# 强制续期
sudo certbot renew --force-renewal
```

#### 4. 性能问题
```bash
# 检查系统负载
uptime
iostat 1 5

# 检查内存使用
free -h
ps aux --sort=-%mem | head -10

# 优化配置
# 编辑 gunicorn.conf.py 调整worker数量
# 编辑 nginx.conf 调整worker_processes
```

### 紧急恢复

#### 快速重启所有服务
```bash
# Docker环境
docker-compose restart

# 传统环境
sudo systemctl restart fed-mpc-web
sudo systemctl restart nginx  # 或 apache2
```

#### 从备份恢复
```bash
# 停止应用
docker-compose stop app  # Docker环境
sudo systemctl stop fed-mpc-web  # 传统环境

# 恢复数据库
docker-compose exec -T mysql mysql -u fed_mpc_user -p fed_mpc_web < backups/db_latest.sql

# 恢复文件
tar -xzf backups/uploads_latest.tar.gz

# 重启应用
docker-compose start app  # Docker环境  
sudo systemctl start fed-mpc-web  # 传统环境
```

---

## 🔒 安全加固

### 系统安全

#### 更新管理
```bash
# 设置自动安全更新 (Ubuntu)
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# 定期手动更新
sudo apt update && sudo apt upgrade -y  # Ubuntu
sudo yum update -y  # CentOS
```

#### SSH加固
```bash
# 编辑SSH配置
sudo nano /etc/ssh/sshd_config

# 推荐设置：
# Port 22 (可改为非标准端口)
# PermitRootLogin no
# PasswordAuthentication no (使用密钥认证)
# PubkeyAuthentication yes

# 重启SSH服务
sudo systemctl restart sshd
```

### 应用安全

#### 环境变量安全
```bash
# 设置安全的文件权限
chmod 600 .env
chown root:root .env  # 或适当的用户

# 定期轮换密钥
# 更新 .env 中的 SECRET_KEY 和 JWT_SECRET_KEY
```

#### Web服务器安全
```bash
# Nginx安全配置已包含在部署脚本中：
# - 隐藏服务器版本
# - 添加安全头
# - 限制请求大小
# - 启用Gzip压缩

# Apache安全配置已包含在部署脚本中：
# - 添加安全头
# - 配置访问控制
```

---

## 📞 技术支持

### 文档资源
- **项目地址**: [GitHub Repository]
- **API文档**: http://your-domain.com/api/docs
- **部署文档**: [Documentation URL]

### 问题反馈
- **Issues**: [GitHub Issues URL]  
- **讨论**: [GitHub Discussions URL]
- **邮件**: admin@your-domain.com

### 社区支持
- **技术交流群**: [QQ/微信群]
- **开发者论坛**: [Forum URL]
- **视频教程**: [YouTube/Bilibili]

---

## 📝 版本更新

### 获取最新版本
```bash
# 查看当前版本
cat VERSION 2>/dev/null || echo "版本信息不可用"

# 拉取最新代码 (Git部署)
git pull origin main

# 更新Docker镜像
docker-compose pull
docker-compose up -d --force-recreate
```

### 更新记录
- **v1.0.0**: 初始版本，支持基础联邦学习功能
- **v1.1.0**: 添加EdgeAI管理模块，完善国际化支持
- **v1.2.0**: 优化部署脚本，增加多种Web引擎支持

---

**🎉 祝您部署成功！如有问题，请随时联系技术支持。**