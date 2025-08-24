#!/bin/bash

# Fed_MPC_Web 自动化部署脚本
# 支持开发、测试、生产环境部署

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认配置
ENVIRONMENT=${1:-production}
DEPLOY_USER=${2:-root}
DEPLOY_HOST=${3:-your-server.com}
PROJECT_NAME="fed_mpc_web"
DOCKER_REGISTRY=${DOCKER_REGISTRY:-}

# 函数定义
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查必需的工具
check_requirements() {
    log_info "检查部署要求..."
    
    local missing_tools=()
    
    command -v docker >/dev/null 2>&1 || missing_tools+=("docker")
    command -v docker-compose >/dev/null 2>&1 || missing_tools+=("docker-compose")
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "缺少必需的工具: ${missing_tools[*]}"
        log_info "请安装这些工具后重试"
        exit 1
    fi
    
    log_success "所有要求检查通过"
}

# 验证环境配置
validate_environment() {
    log_info "验证环境配置..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            log_warning ".env文件不存在，从.env.example复制"
            cp .env.example .env
            log_warning "请编辑.env文件并填写正确的配置值"
            exit 1
        else
            log_error ".env文件和.env.example都不存在"
            exit 1
        fi
    fi
    
    # 检查关键环境变量
    source .env
    
    local required_vars=("SECRET_KEY" "MYSQL_PASSWORD")
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            log_error "环境变量 $var 未设置"
            exit 1
        fi
    done
    
    log_success "环境配置验证通过"
}

# 构建Docker镜像
build_images() {
    log_info "构建Docker镜像..."
    
    # 构建主应用镜像
    docker build -t ${PROJECT_NAME}:${ENVIRONMENT} .
    
    if [ $? -ne 0 ]; then
        log_error "Docker镜像构建失败"
        exit 1
    fi
    
    # 如果配置了镜像仓库，推送镜像
    if [ -n "$DOCKER_REGISTRY" ]; then
        log_info "推送镜像到仓库..."
        docker tag ${PROJECT_NAME}:${ENVIRONMENT} ${DOCKER_REGISTRY}/${PROJECT_NAME}:${ENVIRONMENT}
        docker push ${DOCKER_REGISTRY}/${PROJECT_NAME}:${ENVIRONMENT}
    fi
    
    log_success "镜像构建完成"
}

# 部署到本地
deploy_local() {
    log_info "开始本地部署..."
    
    # 停止现有服务
    docker-compose down --remove-orphans
    
    # 清理旧数据（谨慎使用）
    if [ "$CLEAN_DEPLOY" = "true" ]; then
        log_warning "清理模式：删除所有数据卷"
        docker-compose down -v
        docker system prune -af --volumes
    fi
    
    # 启动服务
    docker-compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 健康检查
    health_check
    
    log_success "本地部署完成"
}

# 远程部署
deploy_remote() {
    log_info "开始远程部署到 ${DEPLOY_USER}@${DEPLOY_HOST}..."
    
    # 创建部署包
    local deploy_package="/tmp/${PROJECT_NAME}_deploy.tar.gz"
    tar -czf "$deploy_package" \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='__pycache__' \
        --exclude='.env' \
        .
    
    # 上传到服务器
    log_info "上传部署包..."
    scp "$deploy_package" "${DEPLOY_USER}@${DEPLOY_HOST}:/tmp/"
    
    # 执行远程部署
    ssh "${DEPLOY_USER}@${DEPLOY_HOST}" << EOF
        set -e
        
        # 备份现有版本
        if [ -d "/opt/${PROJECT_NAME}" ]; then
            sudo mv /opt/${PROJECT_NAME} /opt/${PROJECT_NAME}_backup_\$(date +%Y%m%d_%H%M%S)
        fi
        
        # 解压新版本
        sudo mkdir -p /opt/${PROJECT_NAME}
        cd /opt/${PROJECT_NAME}
        sudo tar -xzf /tmp/${PROJECT_NAME}_deploy.tar.gz
        
        # 复制环境配置
        sudo cp /opt/${PROJECT_NAME}_config/.env ./ || true
        
        # 设置权限
        sudo chown -R ${DEPLOY_USER}:${DEPLOY_USER} /opt/${PROJECT_NAME}
        
        # 部署
        docker-compose down --remove-orphans || true
        docker-compose up -d
        
        # 清理
        rm -f /tmp/${PROJECT_NAME}_deploy.tar.gz
EOF
    
    # 清理本地临时文件
    rm -f "$deploy_package"
    
    log_success "远程部署完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost/api/health >/dev/null 2>&1; then
            log_success "健康检查通过"
            return 0
        fi
        
        log_info "健康检查尝试 $attempt/$max_attempts..."
        sleep 10
        ((attempt++))
    done
    
    log_error "健康检查失败"
    return 1
}

# 数据库备份
backup_database() {
    log_info "备份数据库..."
    
    local backup_file="backup_$(date +%Y%m%d_%H%M%S).sql"
    
    docker-compose exec mysql mysqldump \
        -u fed_mpc_user \
        -p"$MYSQL_PASSWORD" \
        fed_mpc_web > "backups/$backup_file"
    
    if [ $? -eq 0 ]; then
        log_success "数据库备份完成: backups/$backup_file"
        
        # 保留最近7天的备份
        find backups/ -name "backup_*.sql" -mtime +7 -delete
    else
        log_error "数据库备份失败"
    fi
}

# 回滚到前一版本
rollback() {
    log_info "回滚到前一版本..."
    
    # 查找备份版本
    local backup_dir="/opt/${PROJECT_NAME}_backup_*"
    local latest_backup=$(ls -dt $backup_dir 2>/dev/null | head -n1)
    
    if [ -z "$latest_backup" ]; then
        log_error "未找到备份版本"
        exit 1
    fi
    
    log_info "回滚到版本: $latest_backup"
    
    # 停止当前服务
    docker-compose down
    
    # 恢复备份版本
    sudo mv /opt/${PROJECT_NAME} /opt/${PROJECT_NAME}_rollback_$(date +%Y%m%d_%H%M%S)
    sudo mv "$latest_backup" /opt/${PROJECT_NAME}
    
    # 启动服务
    cd /opt/${PROJECT_NAME}
    docker-compose up -d
    
    health_check
    
    log_success "回滚完成"
}

# 显示使用帮助
show_help() {
    echo "Fed_MPC_Web 部署脚本"
    echo ""
    echo "用法: $0 [环境] [用户] [主机] [选项]"
    echo ""
    echo "环境:"
    echo "  production  - 生产环境（默认）"
    echo "  staging     - 测试环境"
    echo "  development - 开发环境"
    echo ""
    echo "选项:"
    echo "  --local     - 本地部署"
    echo "  --remote    - 远程部署"
    echo "  --backup    - 备份数据库"
    echo "  --rollback  - 回滚到前一版本"
    echo "  --clean     - 清理模式部署"
    echo "  --help      - 显示此帮助"
    echo ""
    echo "示例:"
    echo "  $0 production              # 本地生产环境部署"
    echo "  $0 production root server.com --remote  # 远程部署"
    echo "  $0 --backup                # 备份数据库"
    echo "  $0 --rollback              # 回滚"
}

# 主函数
main() {
    echo "======================================"
    echo "Fed_MPC_Web 自动化部署系统"
    echo "======================================"
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --local)
                DEPLOY_TYPE="local"
                shift
                ;;
            --remote)
                DEPLOY_TYPE="remote"
                shift
                ;;
            --backup)
                ACTION="backup"
                shift
                ;;
            --rollback)
                ACTION="rollback"
                shift
                ;;
            --clean)
                CLEAN_DEPLOY="true"
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                shift
                ;;
        esac
    done
    
    # 默认为本地部署
    DEPLOY_TYPE=${DEPLOY_TYPE:-local}
    ACTION=${ACTION:-deploy}
    
    # 创建必要目录
    mkdir -p backups logs
    
    # 执行相应操作
    case $ACTION in
        backup)
            backup_database
            ;;
        rollback)
            rollback
            ;;
        deploy)
            check_requirements
            validate_environment
            build_images
            
            case $DEPLOY_TYPE in
                local)
                    deploy_local
                    ;;
                remote)
                    deploy_remote
                    ;;
                *)
                    log_error "未知的部署类型: $DEPLOY_TYPE"
                    exit 1
                    ;;
            esac
            ;;
        *)
            log_error "未知的操作: $ACTION"
            show_help
            exit 1
            ;;
    esac
    
    log_success "部署操作完成！"
    
    # 显示部署信息
    echo ""
    echo "======================================"
    echo "部署信息"
    echo "======================================"
    echo "环境: $ENVIRONMENT"
    echo "类型: $DEPLOY_TYPE"
    echo "时间: $(date)"
    
    if [ "$DEPLOY_TYPE" = "local" ]; then
        echo "访问地址: http://localhost"
        echo "API地址: http://localhost/api"
        echo "健康检查: http://localhost/api/health"
    else
        echo "访问地址: http://$DEPLOY_HOST"
        echo "API地址: http://$DEPLOY_HOST/api"
        echo "健康检查: http://$DEPLOY_HOST/api/health"
    fi
    
    echo "======================================"
}

# 脚本入口
if [ "$0" = "${BASH_SOURCE[0]}" ]; then
    main "$@"
fi