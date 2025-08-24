#!/bin/bash

# Fed_MPC_Web 数据库备份和恢复脚本
# 支持自动化备份、恢复、清理等功能

set -e

# 配置变量
PROJECT_NAME="fed_mpc_web"
BACKUP_DIR="/opt/${PROJECT_NAME}/backups"
LOG_DIR="/opt/${PROJECT_NAME}/logs"
CONFIG_FILE=".env"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 加载环境变量
load_environment() {
    if [ -f "$CONFIG_FILE" ]; then
        source "$CONFIG_FILE"
        log_info "环境变量加载成功"
    else
        log_error "环境配置文件不存在: $CONFIG_FILE"
        exit 1
    fi
}

# 检查依赖
check_dependencies() {
    local missing_deps=()
    
    command -v docker-compose >/dev/null 2>&1 || missing_deps+=("docker-compose")
    command -v mysql >/dev/null 2>&1 || missing_deps+=("mysql-client")
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "缺少依赖: ${missing_deps[*]}"
        exit 1
    fi
}

# 创建备份目录
create_backup_dirs() {
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$LOG_DIR"
    log_info "备份目录创建完成"
}

# 数据库备份
backup_database() {
    local backup_type=${1:-"manual"}
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/db_backup_${timestamp}.sql"
    local backup_log="$LOG_DIR/backup_${timestamp}.log"
    
    log_info "开始数据库备份..."
    
    # 执行备份
    if docker-compose exec -T mysql mysqldump \
        --single-transaction \
        --routines \
        --triggers \
        --events \
        --set-gtid-purged=OFF \
        -u "$MYSQL_USER" \
        -p"$MYSQL_PASSWORD" \
        "$MYSQL_DB" > "$backup_file" 2>"$backup_log"; then
        
        # 压缩备份文件
        gzip "$backup_file"
        backup_file="${backup_file}.gz"
        
        # 验证备份文件
        if [ -s "$backup_file" ]; then
            local file_size=$(du -h "$backup_file" | cut -f1)
            log_success "数据库备份完成: $backup_file (大小: $file_size)"
            
            # 记录备份信息
            echo "$(date '+%Y-%m-%d %H:%M:%S'),${backup_type},${backup_file},${file_size}" >> "$BACKUP_DIR/backup_history.csv"
            
            return 0
        else
            log_error "备份文件为空"
            rm -f "$backup_file"
            return 1
        fi
    else
        log_error "数据库备份失败，查看日志: $backup_log"
        return 1
    fi
}

# 文件备份
backup_files() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local uploads_backup="$BACKUP_DIR/uploads_backup_${timestamp}.tar.gz"
    local config_backup="$BACKUP_DIR/config_backup_${timestamp}.tar.gz"
    
    log_info "开始文件备份..."
    
    # 备份上传文件
    if [ -d "uploads" ]; then
        tar -czf "$uploads_backup" uploads/ 2>/dev/null
        if [ $? -eq 0 ]; then
            local file_size=$(du -h "$uploads_backup" | cut -f1)
            log_success "上传文件备份完成: $uploads_backup (大小: $file_size)"
        else
            log_warning "上传文件备份失败"
            rm -f "$uploads_backup"
        fi
    fi
    
    # 备份配置文件
    tar -czf "$config_backup" \
        .env \
        docker-compose.yml \
        deploy/ \
        2>/dev/null
    
    if [ $? -eq 0 ]; then
        local file_size=$(du -h "$config_backup" | cut -f1)
        log_success "配置文件备份完成: $config_backup (大小: $file_size)"
    else
        log_warning "配置文件备份失败"
        rm -f "$config_backup"
    fi
}

# 完整备份
full_backup() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_name="full_backup_${timestamp}"
    local backup_log="$LOG_DIR/${backup_name}.log"
    
    log_info "开始完整备份..." | tee -a "$backup_log"
    
    # 创建备份目录
    local full_backup_dir="$BACKUP_DIR/$backup_name"
    mkdir -p "$full_backup_dir"
    
    # 备份数据库
    log_info "备份数据库..." | tee -a "$backup_log"
    if docker-compose exec -T mysql mysqldump \
        --single-transaction \
        --routines \
        --triggers \
        --events \
        --set-gtid-purged=OFF \
        -u "$MYSQL_USER" \
        -p"$MYSQL_PASSWORD" \
        "$MYSQL_DB" | gzip > "$full_backup_dir/database.sql.gz"; then
        log_success "数据库备份完成" | tee -a "$backup_log"
    else
        log_error "数据库备份失败" | tee -a "$backup_log"
        return 1
    fi
    
    # 备份应用文件
    log_info "备份应用文件..." | tee -a "$backup_log"
    if [ -d "uploads" ]; then
        cp -r uploads "$full_backup_dir/"
    fi
    
    # 备份配置
    cp .env docker-compose.yml "$full_backup_dir/" 2>/dev/null || true
    cp -r deploy "$full_backup_dir/" 2>/dev/null || true
    
    # 创建备份信息文件
    cat > "$full_backup_dir/backup_info.txt" << EOF
Backup Information
==================
Backup Name: $backup_name
Backup Time: $(date)
Database: $MYSQL_DB
Application Version: 1.0.0
Backup Type: Full Backup
EOF
    
    # 压缩完整备份
    cd "$BACKUP_DIR"
    tar -czf "${backup_name}.tar.gz" "$backup_name/"
    rm -rf "$backup_name"
    
    local file_size=$(du -h "${backup_name}.tar.gz" | cut -f1)
    log_success "完整备份完成: ${backup_name}.tar.gz (大小: $file_size)" | tee -a "$backup_log"
}

# 数据库恢复
restore_database() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        log_error "请指定备份文件"
        show_available_backups
        return 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "备份文件不存在: $backup_file"
        return 1
    fi
    
    log_warning "即将恢复数据库，这将覆盖现有数据！"
    read -p "确认继续？(yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        log_info "操作已取消"
        return 0
    fi
    
    log_info "开始数据库恢复..."
    
    # 备份当前数据库
    local pre_restore_backup="$BACKUP_DIR/pre_restore_backup_$(date +%Y%m%d_%H%M%S).sql.gz"
    docker-compose exec -T mysql mysqldump \
        --single-transaction \
        -u "$MYSQL_USER" \
        -p"$MYSQL_PASSWORD" \
        "$MYSQL_DB" | gzip > "$pre_restore_backup"
    
    log_info "当前数据库已备份到: $pre_restore_backup"
    
    # 恢复数据库
    if [[ "$backup_file" == *.gz ]]; then
        # 处理压缩文件
        if gunzip -c "$backup_file" | docker-compose exec -T mysql mysql \
            -u "$MYSQL_USER" \
            -p"$MYSQL_PASSWORD" \
            "$MYSQL_DB"; then
            log_success "数据库恢复完成"
        else
            log_error "数据库恢复失败"
            return 1
        fi
    else
        # 处理未压缩文件
        if docker-compose exec -T mysql mysql \
            -u "$MYSQL_USER" \
            -p"$MYSQL_PASSWORD" \
            "$MYSQL_DB" < "$backup_file"; then
            log_success "数据库恢复完成"
        else
            log_error "数据库恢复失败"
            return 1
        fi
    fi
}

# 显示可用备份
show_available_backups() {
    log_info "可用备份文件:"
    echo ""
    
    if [ -d "$BACKUP_DIR" ]; then
        find "$BACKUP_DIR" -name "*.sql*" -o -name "full_backup_*.tar.gz" | sort -r | head -10 | while read file; do
            local size=$(du -h "$file" | cut -f1)
            local date=$(stat -c %y "$file" 2>/dev/null | cut -d' ' -f1,2 | cut -d'.' -f1)
            printf "  %-50s %8s %s\n" "$(basename "$file")" "$size" "$date"
        done
    else
        log_warning "备份目录不存在"
    fi
    echo ""
}

# 清理旧备份
cleanup_old_backups() {
    local retention_days=${1:-7}
    
    log_info "清理 ${retention_days} 天前的备份文件..."
    
    if [ -d "$BACKUP_DIR" ]; then
        local deleted_count=0
        
        # 清理数据库备份
        find "$BACKUP_DIR" -name "db_backup_*.sql*" -mtime +$retention_days -type f | while read file; do
            rm -f "$file"
            log_info "删除旧备份: $(basename "$file")"
            ((deleted_count++))
        done
        
        # 清理完整备份
        find "$BACKUP_DIR" -name "full_backup_*.tar.gz" -mtime +$retention_days -type f | while read file; do
            rm -f "$file"
            log_info "删除旧备份: $(basename "$file")"
            ((deleted_count++))
        done
        
        log_success "清理完成，删除了 $deleted_count 个旧备份文件"
    else
        log_warning "备份目录不存在"
    fi
}

# 验证备份完整性
verify_backup() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        log_error "请指定备份文件"
        return 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "备份文件不存在: $backup_file"
        return 1
    fi
    
    log_info "验证备份文件: $(basename "$backup_file")"
    
    # 检查文件大小
    local file_size=$(stat -c%s "$backup_file")
    if [ "$file_size" -lt 1024 ]; then
        log_error "备份文件太小，可能损坏"
        return 1
    fi
    
    # 检查压缩文件完整性
    if [[ "$backup_file" == *.gz ]]; then
        if gunzip -t "$backup_file" 2>/dev/null; then
            log_success "压缩文件完整性检查通过"
        else
            log_error "压缩文件损坏"
            return 1
        fi
    fi
    
    # 检查SQL文件基本语法
    if [[ "$backup_file" == *.sql* ]]; then
        local temp_file="/tmp/backup_test.sql"
        
        if [[ "$backup_file" == *.gz ]]; then
            gunzip -c "$backup_file" | head -50 > "$temp_file"
        else
            head -50 "$backup_file" > "$temp_file"
        fi
        
        if grep -q "CREATE TABLE\|INSERT INTO\|CREATE DATABASE" "$temp_file"; then
            log_success "SQL文件格式检查通过"
        else
            log_warning "SQL文件可能不完整"
        fi
        
        rm -f "$temp_file"
    fi
    
    log_success "备份文件验证完成"
}

# 备份状态报告
backup_report() {
    log_info "生成备份状态报告..."
    
    local report_file="$LOG_DIR/backup_report_$(date +%Y%m%d).txt"
    
    cat > "$report_file" << EOF
Fed_MPC_Web 备份状态报告
========================

生成时间: $(date)
备份目录: $BACKUP_DIR

磁盘使用情况:
$(df -h "$BACKUP_DIR" 2>/dev/null || echo "无法获取磁盘信息")

最近备份文件:
EOF
    
    if [ -d "$BACKUP_DIR" ]; then
        find "$BACKUP_DIR" -name "*.sql*" -o -name "*.tar.gz" | sort -r | head -10 | while read file; do
            local size=$(du -h "$file" | cut -f1)
            local date=$(stat -c %y "$file" 2>/dev/null | cut -d' ' -f1,2 | cut -d'.' -f1)
            printf "  %-50s %8s %s\n" "$(basename "$file")" "$size" "$date" >> "$report_file"
        done
    fi
    
    cat >> "$report_file" << EOF

备份历史统计:
EOF
    
    if [ -f "$BACKUP_DIR/backup_history.csv" ]; then
        echo "总备份次数: $(wc -l < "$BACKUP_DIR/backup_history.csv")" >> "$report_file"
        echo "最近备份: $(tail -1 "$BACKUP_DIR/backup_history.csv" | cut -d',' -f1)" >> "$report_file"
    fi
    
    log_success "备份报告生成完成: $report_file"
    cat "$report_file"
}

# 显示帮助信息
show_help() {
    echo "Fed_MPC_Web 数据库备份和恢复工具"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --backup-db              备份数据库"
    echo "  --backup-files           备份文件"
    echo "  --full-backup            完整备份"
    echo "  --restore-db <file>      恢复数据库"
    echo "  --list-backups           显示可用备份"
    echo "  --cleanup [days]         清理旧备份（默认7天）"
    echo "  --verify <file>          验证备份文件"
    echo "  --report                 生成备份报告"
    echo "  --help                   显示此帮助"
    echo ""
    echo "示例:"
    echo "  $0 --backup-db                           # 备份数据库"
    echo "  $0 --full-backup                         # 完整备份"
    echo "  $0 --restore-db db_backup_20240101.sql.gz  # 恢复数据库"
    echo "  $0 --cleanup 30                          # 清理30天前的备份"
    echo ""
}

# 主函数
main() {
    echo "======================================"
    echo "Fed_MPC_Web 备份和恢复工具"
    echo "======================================"
    
    # 检查参数
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    # 初始化
    load_environment
    check_dependencies
    create_backup_dirs
    
    # 处理参数
    case "$1" in
        --backup-db)
            backup_database "manual"
            ;;
        --backup-files)
            backup_files
            ;;
        --full-backup)
            full_backup
            ;;
        --restore-db)
            if [ -n "$2" ]; then
                restore_database "$2"
            else
                log_error "请指定备份文件"
                show_available_backups
            fi
            ;;
        --list-backups)
            show_available_backups
            ;;
        --cleanup)
            cleanup_old_backups "${2:-7}"
            ;;
        --verify)
            if [ -n "$2" ]; then
                verify_backup "$2"
            else
                log_error "请指定要验证的备份文件"
            fi
            ;;
        --report)
            backup_report
            ;;
        --help)
            show_help
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
    
    log_success "操作完成！"
}

# 脚本入口
if [ "$0" = "${BASH_SOURCE[0]}" ]; then
    main "$@"
fi