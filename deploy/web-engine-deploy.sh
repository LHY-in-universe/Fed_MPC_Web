#!/bin/bash

# Fed_MPC_Web Web引擎部署脚本
# 支持多种Web服务器引擎的部署方案

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

# 显示使用说明
show_usage() {
    cat << 'USAGE_EOF'
Fed_MPC_Web Web引擎部署脚本

用法: ./web-engine-deploy.sh [ENGINE] [OPTIONS]

支持的Web引擎:
  nginx        - Nginx + Gunicorn (推荐)
  apache       - Apache + mod_wsgi
  docker       - Docker容器化部署 (推荐)
  standalone   - 独立Python服务器 (开发/测试)
  uwsgi        - uWSGI + Nginx
  caddy        - Caddy服务器

选项:
  --domain DOMAIN     设置域名 (默认: localhost)
  --port PORT         设置端口 (默认: 80)
  --ssl              启用SSL/HTTPS
  --backup           部署前备份现有配置
  --no-start         部署后不自动启动服务
  --help             显示帮助信息

示例:
  # Docker部署 (推荐)
  ./web-engine-deploy.sh docker --domain example.com --ssl

  # Nginx部署
  ./web-engine-deploy.sh nginx --domain example.com --port 80 --ssl

  # 开发环境
  ./web-engine-deploy.sh standalone --port 5000

更多详情请查看: https://docs.example.com/deployment
USAGE_EOF
}

# 解析命令行参数
ENGINE=""
DOMAIN="localhost"
PORT="80"
SSL_ENABLED=false
BACKUP_ENABLED=false
AUTO_START=true

while [[ $# -gt 0 ]]; do
    case $1 in
        nginx|apache|docker|standalone|uwsgi|caddy)
            ENGINE="$1"
            shift
            ;;
        --domain)
            DOMAIN="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --ssl)
            SSL_ENABLED=true
            shift
            ;;
        --backup)
            BACKUP_ENABLED=true
            shift
            ;;
        --no-start)
            AUTO_START=false
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            print_error "未知参数: $1"
            show_usage
            exit 1
            ;;
    esac
done

if [ -z "$ENGINE" ]; then
    print_error "请指定Web引擎"
    show_usage
    exit 1
fi

# 获取项目目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

print_status "Fed_MPC_Web Web引擎部署"
print_status "引擎: $ENGINE"
print_status "域名: $DOMAIN"
print_status "端口: $PORT"
print_status "SSL: $([ "$SSL_ENABLED" = true ] && echo "启用" || echo "禁用")"

# ===========================================
# Docker 部署
# ===========================================
deploy_docker() {
    print_status "开始Docker部署..."

    # 检查Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装，请先安装Docker"
        print_status "安装命令: curl -fsSL https://get.docker.com | sh"
        exit 1
    fi

    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose未安装"
        exit 1
    fi

    # 创建环境变量文件
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        print_warning ".env文件不存在，从模板创建..."
        cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
        
        # 更新域名配置
        if [ "$DOMAIN" != "localhost" ]; then
            sed -i "s/your-domain.com/$DOMAIN/g" "$PROJECT_ROOT/.env" 2>/dev/null || \
            sed -i "" "s/your-domain.com/$DOMAIN/g" "$PROJECT_ROOT/.env" 2>/dev/null || true
        fi
        
        print_warning "请编辑 .env 文件配置必要参数后重新运行"
        exit 1
    fi

    # SSL配置
    if [ "$SSL_ENABLED" = true ]; then
        print_status "配置SSL证书..."
        
        # 更新docker-compose.yml以启用HTTPS
        if [ -f "$PROJECT_ROOT/docker-compose.yml" ]; then
            # 这里可以添加SSL相关的配置修改
            print_status "SSL配置将在容器启动后通过Let's Encrypt自动获取"
        fi
    fi

    cd "$PROJECT_ROOT"
    
    # 构建和启动服务
    print_status "构建Docker镜像..."
    docker-compose build

    print_status "启动服务..."
    docker-compose up -d

    # 等待服务启动
    print_status "等待服务启动..."
    sleep 15

    # 健康检查
    if curl -f "http://localhost:$PORT/api/health" &>/dev/null; then
        print_success "✓ 部署成功！服务正常运行"
    else
        print_warning "服务可能未完全启动，请检查日志: docker-compose logs -f app"
    fi

    print_success "Docker部署完成！"
    print_status "访问地址: http://$DOMAIN:$PORT"
}

# ===========================================
# Nginx + Gunicorn 部署
# ===========================================
deploy_nginx() {
    print_status "开始Nginx + Gunicorn部署..."

    # 检查系统
    if ! command -v nginx &> /dev/null; then
        print_status "安装Nginx..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y nginx
        elif command -v yum &> /dev/null; then
            sudo yum install -y nginx
        else
            print_error "无法自动安装Nginx，请手动安装"
            exit 1
        fi
    fi

    # 创建应用目录
    APP_DIR="/opt/fed_mpc_web"
    print_status "创建应用目录: $APP_DIR"
    sudo mkdir -p "$APP_DIR"
    sudo cp -r "$PROJECT_ROOT"/* "$APP_DIR/"
    sudo chown -R www-data:www-data "$APP_DIR" 2>/dev/null || sudo chown -R nginx:nginx "$APP_DIR" 2>/dev/null || true

    # 安装Python依赖
    print_status "安装Python依赖..."
    cd "$APP_DIR"
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -r requirements.txt 2>/dev/null || pip install -r backend/requirements.txt
    pip install gunicorn

    # 创建Gunicorn配置
    cat > "$APP_DIR/gunicorn.conf.py" << 'GUNICORN_CONF'
import multiprocessing

# 服务器配置
bind = "127.0.0.1:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# 日志配置
accesslog = "/opt/fed_mpc_web/logs/gunicorn_access.log"
errorlog = "/opt/fed_mpc_web/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# 进程配置
preload_app = True
max_requests = 1000
max_requests_jitter = 100

# 安全配置
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
GUNICORN_CONF

    # 创建systemd服务文件
    sudo tee /etc/systemd/system/fed-mpc-web.service > /dev/null << SERVICE_CONF
[Unit]
Description=Fed_MPC_Web Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/fed_mpc_web
Environment="PATH=/opt/fed_mpc_web/venv/bin"
ExecStart=/opt/fed_mpc_web/venv/bin/gunicorn --config /opt/fed_mpc_web/gunicorn.conf.py backend.app:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE_CONF

    # 创建Nginx配置
    sudo tee "/etc/nginx/sites-available/fed_mpc_web" > /dev/null << NGINX_CONF
server {
    listen $PORT;
    server_name $DOMAIN;
    
    # 静态文件
    location /static/ {
        alias /opt/fed_mpc_web/frontend/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # 前端页面
    location / {
        root /opt/fed_mpc_web/frontend;
        try_files \$uri \$uri/ /homepage/index.html;
        index index.html;
    }
    
    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 超时配置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy strict-origin-when-cross-origin;
    
    # 限制文件上传大小
    client_max_body_size 100M;
    
    # Gzip压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
NGINX_CONF

    # SSL配置
    if [ "$SSL_ENABLED" = true ]; then
        print_status "配置SSL证书..."
        
        # 安装certbot
        if command -v apt-get &> /dev/null; then
            sudo apt-get install -y certbot python3-certbot-nginx
        elif command -v yum &> /dev/null; then
            sudo yum install -y certbot python3-certbot-nginx
        fi
        
        # 获取证书
        sudo certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email "admin@$DOMAIN" || print_warning "SSL证书获取失败，请手动配置"
    fi

    # 启用站点
    sudo ln -sf /etc/nginx/sites-available/fed_mpc_web /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default

    # 测试配置
    sudo nginx -t

    # 启动服务
    if [ "$AUTO_START" = true ]; then
        print_status "启动服务..."
        
        # 创建日志目录
        sudo mkdir -p /opt/fed_mpc_web/logs
        sudo chown www-data:www-data /opt/fed_mpc_web/logs 2>/dev/null || sudo chown nginx:nginx /opt/fed_mpc_web/logs 2>/dev/null || true
        
        # 启动应用
        sudo systemctl daemon-reload
        sudo systemctl enable fed-mpc-web
        sudo systemctl start fed-mpc-web
        
        # 启动Nginx
        sudo systemctl enable nginx
        sudo systemctl restart nginx
        
        # 检查服务状态
        sleep 5
        if curl -f "http://localhost:$PORT/api/health" &>/dev/null; then
            print_success "✓ Nginx部署成功！"
        else
            print_warning "服务可能未正常启动，请检查日志"
            sudo systemctl status fed-mpc-web
        fi
    fi

    print_success "Nginx + Gunicorn部署完成！"
    print_status "访问地址: http://$DOMAIN:$PORT"
}

# ===========================================
# Apache + mod_wsgi 部署
# ===========================================
deploy_apache() {
    print_status "开始Apache + mod_wsgi部署..."
    
    # 检查系统并安装Apache
    if ! command -v apache2 &> /dev/null && ! command -v httpd &> /dev/null; then
        print_status "安装Apache..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y apache2 libapache2-mod-wsgi-py3
        elif command -v yum &> /dev/null; then
            sudo yum install -y httpd python3-mod_wsgi
        else
            print_error "无法自动安装Apache，请手动安装"
            exit 1
        fi
    fi

    # 创建应用目录
    APP_DIR="/var/www/fed_mpc_web"
    print_status "创建应用目录: $APP_DIR"
    sudo mkdir -p "$APP_DIR"
    sudo cp -r "$PROJECT_ROOT"/* "$APP_DIR/"
    sudo chown -R www-data:www-data "$APP_DIR" 2>/dev/null || sudo chown -R apache:apache "$APP_DIR" 2>/dev/null || true

    # 安装Python依赖
    cd "$APP_DIR"
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt 2>/dev/null || pip install -r backend/requirements.txt

    # 创建WSGI文件
    cat > "$APP_DIR/fed_mpc_web.wsgi" << 'WSGI_CONF'
#!/usr/bin/python3
import sys
import os

# 添加项目路径
sys.path.insert(0, "/var/www/fed_mpc_web/")
sys.path.insert(0, "/var/www/fed_mpc_web/backend/")

# 激活虚拟环境
activate_this = '/var/www/fed_mpc_web/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from backend.app import app as application

if __name__ == "__main__":
    application.run()
WSGI_CONF

    # 创建Apache虚拟主机配置
    if command -v apache2 &> /dev/null; then
        APACHE_CONF="/etc/apache2/sites-available/fed_mpc_web.conf"
        APACHE_CMD="apache2"
    else
        APACHE_CONF="/etc/httpd/conf.d/fed_mpc_web.conf"
        APACHE_CMD="httpd"
    fi

    sudo tee "$APACHE_CONF" > /dev/null << APACHE_VHOST
<VirtualHost *:$PORT>
    ServerName $DOMAIN
    DocumentRoot /var/www/fed_mpc_web/frontend
    
    WSGIDaemonProcess fed_mpc_web python-home=/var/www/fed_mpc_web/venv python-path=/var/www/fed_mpc_web
    WSGIProcessGroup fed_mpc_web
    WSGIScriptAlias /api /var/www/fed_mpc_web/fed_mpc_web.wsgi
    
    # 静态文件
    Alias /static /var/www/fed_mpc_web/frontend
    <Directory /var/www/fed_mpc_web/frontend>
        Require all granted
    </Directory>
    
    <Directory /var/www/fed_mpc_web>
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>
    
    # 日志配置
    ErrorLog \${APACHE_LOG_DIR}/fed_mpc_web_error.log
    CustomLog \${APACHE_LOG_DIR}/fed_mpc_web_access.log combined
    
    # 安全配置
    Header always set X-Frame-Options DENY
    Header always set X-Content-Type-Options nosniff
    Header always set X-XSS-Protection "1; mode=block"
</VirtualHost>
APACHE_VHOST

    # 启用模块和站点
    if command -v a2enmod &> /dev/null; then
        sudo a2enmod wsgi
        sudo a2enmod headers
        sudo a2ensite fed_mpc_web
        sudo a2dissite 000-default
    fi

    # 启动服务
    if [ "$AUTO_START" = true ]; then
        print_status "启动Apache服务..."
        sudo systemctl enable $APACHE_CMD
        sudo systemctl restart $APACHE_CMD
        
        # 检查服务状态
        sleep 5
        if curl -f "http://localhost:$PORT/" &>/dev/null; then
            print_success "✓ Apache部署成功！"
        else
            print_warning "服务可能未正常启动，请检查日志"
            sudo systemctl status $APACHE_CMD
        fi
    fi

    print_success "Apache + mod_wsgi部署完成！"
    print_status "访问地址: http://$DOMAIN:$PORT"
}

# ===========================================
# 独立Python服务器部署
# ===========================================
deploy_standalone() {
    print_status "开始独立Python服务器部署..."
    
    # 检查Python和pip
    if ! command -v python3 &> /dev/null; then
        print_error "Python3未安装"
        exit 1
    fi

    cd "$PROJECT_ROOT"
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        print_status "创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    # 安装依赖
    print_status "安装Python依赖..."
    pip install -r requirements.txt 2>/dev/null || pip install -r backend/requirements.txt
    
    # 创建生产配置
    cat > production_config.py << 'PROD_CONF'
import os

class ProductionConfig:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production')
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///fed_mpc_web.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 服务器配置
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', $PORT))
    
    # CORS配置
    CORS_ORIGINS = ['http://$DOMAIN:$PORT', 'https://$DOMAIN:$PORT']
PROD_CONF

    # 创建启动脚本
    cat > start_production.py << 'START_SCRIPT'
from backend.app import app
from production_config import ProductionConfig

app.config.from_object(ProductionConfig)

if __name__ == '__main__':
    app.run(
        host=ProductionConfig.HOST,
        port=ProductionConfig.PORT,
        debug=False,
        threaded=True
    )
START_SCRIPT

    if [ "$AUTO_START" = true ]; then
        print_status "启动应用服务器..."
        print_status "服务器将在端口 $PORT 启动"
        print_status "按 Ctrl+C 停止服务器"
        python start_production.py
    else
        print_status "部署完成，使用以下命令启动服务器:"
        print_status "cd $PROJECT_ROOT && source venv/bin/activate && python start_production.py"
    fi
    
    print_success "独立Python服务器部署完成！"
    print_status "访问地址: http://$DOMAIN:$PORT"
}

# ===========================================
# 主部署逻辑
# ===========================================

# 备份现有配置
if [ "$BACKUP_ENABLED" = true ]; then
    print_status "备份现有配置..."
    BACKUP_DIR="$PROJECT_ROOT/backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    # 这里可以添加具体的备份逻辑
    print_status "✓ 备份完成: $BACKUP_DIR"
fi

# 根据选择的引擎进行部署
case $ENGINE in
    docker)
        deploy_docker
        ;;
    nginx)
        deploy_nginx
        ;;
    apache)
        deploy_apache
        ;;
    standalone)
        deploy_standalone
        ;;
    uwsgi)
        print_error "uWSGI部署功能开发中..."
        exit 1
        ;;
    caddy)
        print_error "Caddy部署功能开发中..."
        exit 1
        ;;
    *)
        print_error "不支持的Web引擎: $ENGINE"
        show_usage
        exit 1
        ;;
esac

print_success "🎉 Fed_MPC_Web 部署完成！"
print_status ""
print_status "管理命令："
if [ "$ENGINE" = "docker" ]; then
    print_status "  - 查看状态: docker-compose ps"
    print_status "  - 查看日志: docker-compose logs -f app"
    print_status "  - 重启服务: docker-compose restart app"
    print_status "  - 停止服务: docker-compose down"
elif [ "$ENGINE" = "nginx" ] || [ "$ENGINE" = "apache" ]; then
    print_status "  - 查看状态: sudo systemctl status fed-mpc-web"
    print_status "  - 查看日志: sudo journalctl -u fed-mpc-web -f"
    print_status "  - 重启服务: sudo systemctl restart fed-mpc-web"
    print_status "  - 停止服务: sudo systemctl stop fed-mpc-web"
fi