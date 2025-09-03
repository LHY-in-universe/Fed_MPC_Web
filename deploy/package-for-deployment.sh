#!/bin/bash

# Fed_MPC_Web 打包部署脚本
# 此脚本将项目打包为可在服务器上直接部署的压缩包

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 输出函数
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOY_DIR="$SCRIPT_DIR"

# 配置变量
PACKAGE_NAME="fed_mpc_web_deployment"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_VERSION="${PACKAGE_NAME}_${TIMESTAMP}"
BUILD_DIR="/tmp/${PACKAGE_VERSION}"

print_status "开始打包 Fed_MPC_Web 项目..."

# 1. 创建构建目录
print_status "创建构建目录: $BUILD_DIR"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# 2. 复制核心项目文件
print_status "复制项目文件..."

# 复制后端代码
cp -r "$PROJECT_ROOT/backend" "$BUILD_DIR/"
print_status "✓ 复制后端代码"

# 复制前端代码
cp -r "$PROJECT_ROOT/frontend" "$BUILD_DIR/"
print_status "✓ 复制前端代码"

# 复制数据库脚本
cp -r "$PROJECT_ROOT/database" "$BUILD_DIR/"
print_status "✓ 复制数据库脚本"

# 复制部署配置
cp -r "$PROJECT_ROOT/deploy" "$BUILD_DIR/"
print_status "✓ 复制部署配置"

# 复制Docker配置
cp "$PROJECT_ROOT/docker-compose.yml" "$BUILD_DIR/"
cp "$PROJECT_ROOT/Dockerfile" "$BUILD_DIR/"
print_status "✓ 复制Docker配置"

# 复制环境配置模板
cp "$PROJECT_ROOT/.env.example" "$BUILD_DIR/"
print_status "✓ 复制环境配置模板"

# 复制项目文档
cp "$PROJECT_ROOT/README.md" "$BUILD_DIR/" 2>/dev/null || true
print_status "✓ 复制项目文档"

# 复制requirements文件
cp "$PROJECT_ROOT/requirements.txt" "$BUILD_DIR/" 2>/dev/null || true
cp "$PROJECT_ROOT/backend/requirements.txt" "$BUILD_DIR/" 2>/dev/null || true
print_status "✓ 复制依赖文件"

# 3. 清理不必要的文件
print_status "清理不必要的文件..."

# 删除缓存文件
find "$BUILD_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$BUILD_DIR" -name "*.pyc" -delete 2>/dev/null || true
find "$BUILD_DIR" -name ".DS_Store" -delete 2>/dev/null || true

# 删除开发文件
rm -rf "$BUILD_DIR/backend/venv" 2>/dev/null || true
rm -rf "$BUILD_DIR/venv" 2>/dev/null || true
rm -rf "$BUILD_DIR/.git" 2>/dev/null || true
rm -rf "$BUILD_DIR/node_modules" 2>/dev/null || true
rm -rf "$BUILD_DIR/backend/instance" 2>/dev/null || true

print_status "✓ 清理完成"

# 4. 创建快速部署脚本
print_status "创建快速部署脚本..."

cat > "$BUILD_DIR/quick-deploy.sh" << 'DEPLOY_SCRIPT'
#!/bin/bash

# Fed_MPC_Web 快速部署脚本
# 在目标服务器上执行此脚本完成部署

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

print_status "开始部署 Fed_MPC_Web..."

# 检查Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker 未安装，请先安装 Docker"
    print_status "安装命令: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 检查环境变量文件
if [ ! -f ".env" ]; then
    print_warning ".env 文件不存在，从模板创建..."
    cp .env.example .env
    print_warning "请编辑 .env 文件，配置必要的环境变量："
    print_warning "  - SECRET_KEY (应用密钥)"
    print_warning "  - JWT_SECRET_KEY (JWT密钥)" 
    print_warning "  - MYSQL_ROOT_PASSWORD (MySQL root密码)"
    print_warning "  - MYSQL_PASSWORD (MySQL用户密码)"
    print_warning "  - CORS_ORIGINS (允许的域名)"
    echo
    read -p "配置完成后按 Enter 继续部署..." -r
fi

# 创建必要的目录
print_status "创建必要的目录..."
mkdir -p logs uploads backups
sudo chown -R $USER:$USER . 2>/dev/null || chown -R $USER:$USER .

# 拉取最新镜像
print_status "拉取Docker镜像..."
docker-compose pull mysql redis || print_warning "部分镜像拉取失败，将使用本地缓存"

# 构建应用镜像
print_status "构建应用镜像..."
docker-compose build app

# 启动数据库服务
print_status "启动数据库服务..."
docker-compose up -d mysql redis

# 等待数据库启动
print_status "等待数据库启动..."
sleep 15

# 启动应用服务
print_status "启动应用服务..."
docker-compose up -d app

# 等待应用启动
print_status "等待应用启动..."
sleep 10

# 检查服务状态
print_status "检查服务状态..."
docker-compose ps

# 健康检查
print_status "执行健康检查..."
if curl -f http://localhost/api/health &>/dev/null || curl -f http://localhost:80/api/health &>/dev/null; then
    print_success "✓ 应用健康检查通过"
else
    print_warning "健康检查失败，请检查日志："
    print_status "docker-compose logs app"
fi

print_success "部署完成！"
print_status "应用已启动，请访问："
print_status "  - 主页: http://$(hostname -I | awk '{print $1}')/"
print_status "  - 健康检查: http://$(hostname -I | awk '{print $1}')/api/health"
print_status ""
print_status "常用管理命令："
print_status "  - 查看日志: docker-compose logs -f app"
print_status "  - 重启服务: docker-compose restart app"
print_status "  - 停止服务: docker-compose down"
print_status "  - 更新服务: docker-compose pull && docker-compose up -d"
DEPLOY_SCRIPT

chmod +x "$BUILD_DIR/quick-deploy.sh"
print_status "✓ 快速部署脚本创建完成"

# 5. 创建安装说明
print_status "创建安装说明..."

cat > "$BUILD_DIR/DEPLOYMENT_GUIDE.md" << 'GUIDE_EOF'
# Fed_MPC_Web 部署指南

## 🚀 快速部署

1. **解压部署包**
   ```bash
   tar -xzf fed_mpc_web_deployment_*.tar.gz
   cd fed_mpc_web_deployment_*
   ```

2. **配置环境变量**
   ```bash
   # 复制环境变量模板
   cp .env.example .env
   
   # 编辑配置文件（必须修改的配置项已标注）
   nano .env
   ```

3. **执行快速部署**
   ```bash
   # 给脚本执行权限
   chmod +x quick-deploy.sh
   
   # 执行部署
   ./quick-deploy.sh
   ```

## 🔧 手动部署步骤

### 1. 系统要求
- Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- Docker 20.10+
- Docker Compose 2.0+
- 2GB+ RAM
- 10GB+ 可用磁盘空间

### 2. 安装Docker
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# CentOS/RHEL
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo systemctl enable docker
```

### 3. 安装Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 4. 配置应用
```bash
# 编辑环境变量
cp .env.example .env
nano .env

# 必须配置的变量：
# - SECRET_KEY: 应用密钥
# - JWT_SECRET_KEY: JWT密钥  
# - MYSQL_ROOT_PASSWORD: MySQL root密码
# - MYSQL_PASSWORD: MySQL用户密码
# - CORS_ORIGINS: 允许的域名
```

### 5. 启动服务
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f app
```

## 🔍 验证部署

1. **检查服务状态**
   ```bash
   docker-compose ps
   ```

2. **健康检查**
   ```bash
   curl http://localhost/api/health
   ```

3. **访问应用**
   - 主页: http://your-server-ip/
   - API文档: http://your-server-ip/api/docs

## 📊 监控和管理

### 查看日志
```bash
# 应用日志
docker-compose logs -f app

# 数据库日志
docker-compose logs -f mysql

# 所有服务日志
docker-compose logs -f
```

### 服务管理
```bash
# 重启服务
docker-compose restart app

# 停止所有服务
docker-compose down

# 更新服务
docker-compose pull
docker-compose up -d
```

### 数据备份
```bash
# 备份数据库
docker-compose exec mysql mysqldump -u fed_mpc_user -p fed_mpc_web > backup_$(date +%Y%m%d).sql

# 恢复数据库
docker-compose exec -T mysql mysql -u fed_mpc_user -p fed_mpc_web < backup_20240101.sql
```

## 🔒 SSL配置 (可选)

使用Let's Encrypt免费证书：

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

## 🚨 故障排除

### 常见问题

1. **容器启动失败**
   - 检查Docker服务: `sudo systemctl status docker`
   - 查看容器日志: `docker-compose logs app`

2. **数据库连接失败**
   - 检查环境变量: `docker-compose exec app env | grep MYSQL`
   - 检查数据库状态: `docker-compose exec mysql mysqladmin ping`

3. **端口占用**
   - 检查端口占用: `sudo netstat -tulpn | grep :80`
   - 修改docker-compose.yml中的端口映射

### 联系支持
- 项目地址: [GitHub Repository]
- 问题反馈: [Issues URL]
GUIDE_EOF

print_status "✓ 安装说明创建完成"

# 6. 创建系统服务文件
print_status "创建系统服务文件..."

cat > "$BUILD_DIR/deploy/fed-mpc-web.service" << 'SERVICE_EOF'
[Unit]
Description=Fed_MPC_Web Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/fed_mpc_web
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
SERVICE_EOF

print_status "✓ 系统服务文件创建完成"

# 7. 创建版本信息文件
cat > "$BUILD_DIR/VERSION" << VERSION_EOF
Fed_MPC_Web Deployment Package
==============================

Package Version: $PACKAGE_VERSION
Build Date: $(date)
Build Host: $(hostname)

Contents:
- Backend Application
- Frontend Web Interface  
- Database Scripts
- Docker Configuration
- Deployment Scripts
- Configuration Templates

For deployment instructions, see DEPLOYMENT_GUIDE.md
VERSION_EOF

# 8. 创建压缩包
print_status "创建部署压缩包..."
cd "/tmp"
tar -czf "${PACKAGE_VERSION}.tar.gz" "${PACKAGE_VERSION}/"

# 移动到项目目录
mv "${PACKAGE_VERSION}.tar.gz" "$PROJECT_ROOT/"
print_success "✓ 压缩包创建完成: $PROJECT_ROOT/${PACKAGE_VERSION}.tar.gz"

# 9. 清理临时文件
print_status "清理临时文件..."
rm -rf "$BUILD_DIR"
print_status "✓ 临时文件清理完成"

# 10. 显示部署包信息
print_success "打包完成！"
echo
print_status "部署包信息："
print_status "  - 文件名: ${PACKAGE_VERSION}.tar.gz"
print_status "  - 位置: $PROJECT_ROOT/${PACKAGE_VERSION}.tar.gz"
print_status "  - 大小: $(du -h "$PROJECT_ROOT/${PACKAGE_VERSION}.tar.gz" | cut -f1)"
echo
print_status "部署步骤："
print_status "  1. 将压缩包上传到目标服务器"
print_status "  2. 解压: tar -xzf ${PACKAGE_VERSION}.tar.gz"
print_status "  3. 进入目录: cd ${PACKAGE_VERSION}/"
print_status "  4. 配置环境: cp .env.example .env && nano .env"
print_status "  5. 执行部署: ./quick-deploy.sh"
echo
print_status "详细部署说明请查看解压后的 DEPLOYMENT_GUIDE.md 文件"
print_success "🎉 打包完成！"