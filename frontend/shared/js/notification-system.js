/**
 * 现代化通知系统
 * 替换原生alert，提供更美观的用户体验
 */

class NotificationSystem {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // 创建通知容器
        this.container = document.createElement('div');
        this.container.id = 'notification-container';
        this.container.className = 'notification-container';
        document.body.appendChild(this.container);

        // 添加CSS样式
        if (!document.getElementById('notification-styles')) {
            const styles = document.createElement('style');
            styles.id = 'notification-styles';
            styles.textContent = this.getStyles();
            document.head.appendChild(styles);
        }
    }

    getStyles() {
        return `
            .notification-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                pointer-events: none;
            }

            .notification {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(226, 232, 240, 0.8);
                border-radius: 16px;
                padding: 20px;
                margin-bottom: 12px;
                min-width: 320px;
                max-width: 480px;
                box-shadow: 
                    0 20px 40px -8px rgba(0, 0, 0, 0.15),
                    0 8px 16px -8px rgba(0, 0, 0, 0.1);
                transform: translateX(400px);
                opacity: 0;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                pointer-events: auto;
                position: relative;
                overflow: hidden;
            }

            .notification.show {
                transform: translateX(0);
                opacity: 1;
            }

            .notification.hide {
                transform: translateX(400px);
                opacity: 0;
            }

            .notification::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, #6366f1, #8b5cf6, #06b6d4);
            }

            .notification.success::before {
                background: linear-gradient(90deg, #10b981, #059669);
            }

            .notification.warning::before {
                background: linear-gradient(90deg, #f59e0b, #d97706);
            }

            .notification.error::before {
                background: linear-gradient(90deg, #ef4444, #dc2626);
            }

            .notification.info::before {
                background: linear-gradient(90deg, #3b82f6, #1d4ed8);
            }

            .notification-header {
                display: flex;
                align-items: flex-start;
                justify-content: space-between;
                margin-bottom: 12px;
            }

            .notification-icon {
                width: 24px;
                height: 24px;
                margin-right: 12px;
                flex-shrink: 0;
                margin-top: 2px;
            }

            .notification-content {
                flex: 1;
            }

            .notification-title {
                font-size: 16px;
                font-weight: 600;
                color: #1e293b;
                margin: 0 0 6px 0;
                line-height: 1.4;
            }

            .notification-message {
                font-size: 14px;
                color: #64748b;
                margin: 0;
                line-height: 1.5;
                white-space: pre-line;
            }

            .notification-close {
                background: none;
                border: none;
                color: #94a3b8;
                cursor: pointer;
                padding: 4px;
                border-radius: 6px;
                transition: all 0.2s ease;
                flex-shrink: 0;
            }

            .notification-close:hover {
                background: rgba(148, 163, 184, 0.1);
                color: #64748b;
            }

            .notification-actions {
                display: flex;
                gap: 8px;
                margin-top: 16px;
                padding-top: 16px;
                border-top: 1px solid rgba(226, 232, 240, 0.8);
            }

            .notification-btn {
                padding: 8px 16px;
                border: 1px solid rgba(226, 232, 240, 0.8);
                border-radius: 8px;
                background: white;
                color: #64748b;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
            }

            .notification-btn:hover {
                background: #f8fafc;
                border-color: #cbd5e1;
            }

            .notification-btn.primary {
                background: linear-gradient(135deg, #6366f1, #8b5cf6);
                color: white;
                border-color: transparent;
            }

            .notification-btn.primary:hover {
                background: linear-gradient(135deg, #5855f7, #7c3aed);
            }

            /* 深色模式支持 */
            @media (prefers-color-scheme: dark) {
                .notification {
                    background: rgba(30, 41, 59, 0.95);
                    border-color: rgba(71, 85, 105, 0.8);
                }

                .notification-title {
                    color: #f1f5f9;
                }

                .notification-message {
                    color: #cbd5e1;
                }

                .notification-close {
                    color: #94a3b8;
                }

                .notification-close:hover {
                    background: rgba(148, 163, 184, 0.2);
                    color: #cbd5e1;
                }

                .notification-btn {
                    background: #334155;
                    border-color: #475569;
                    color: #cbd5e1;
                }

                .notification-btn:hover {
                    background: #475569;
                }
            }

            /* 移动端适配 */
            @media (max-width: 640px) {
                .notification-container {
                    top: 10px;
                    right: 10px;
                    left: 10px;
                }

                .notification {
                    min-width: auto;
                    max-width: none;
                    transform: translateY(-100px);
                }

                .notification.show {
                    transform: translateY(0);
                }

                .notification.hide {
                    transform: translateY(-100px);
                }
            }
        `;
    }

    // 显示通知
    show(options = {}) {
        const {
            title = '提示',
            message = '',
            type = 'info', // info, success, warning, error
            duration = 5000,
            actions = null,
            closable = true
        } = options;

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;

        const icon = this.getIcon(type);
        
        notification.innerHTML = `
            <div class="notification-header">
                <div style="display: flex; align-items: flex-start;">
                    <div class="notification-icon">${icon}</div>
                    <div class="notification-content">
                        <h4 class="notification-title">${title}</h4>
                        <p class="notification-message">${message}</p>
                    </div>
                </div>
                ${closable ? `
                    <button class="notification-close" onclick="notificationSystem.hide(this.parentElement.parentElement)">
                        <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8 2.146 2.854Z"/>
                        </svg>
                    </button>
                ` : ''}
            </div>
            ${actions ? `<div class="notification-actions">${actions}</div>` : ''}
        `;

        this.container.appendChild(notification);

        // 触发显示动画
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        // 自动隐藏
        if (duration > 0) {
            setTimeout(() => {
                this.hide(notification);
            }, duration);
        }

        return notification;
    }

    // 隐藏通知
    hide(notification) {
        if (!notification) return;
        
        notification.classList.remove('show');
        notification.classList.add('hide');
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 400);
    }

    // 获取图标
    getIcon(type) {
        const icons = {
            info: `<svg fill="currentColor" style="color: #3b82f6;" viewBox="0 0 16 16">
                <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"/>
            </svg>`,
            success: `<svg fill="currentColor" style="color: #10b981;" viewBox="0 0 16 16">
                <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.061L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>
            </svg>`,
            warning: `<svg fill="currentColor" style="color: #f59e0b;" viewBox="0 0 16 16">
                <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
            </svg>`,
            error: `<svg fill="currentColor" style="color: #ef4444;" viewBox="0 0 16 16">
                <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"/>
            </svg>`
        };
        return icons[type] || icons.info;
    }

    // 快捷方法
    info(title, message, options = {}) {
        return this.show({ title, message, type: 'info', ...options });
    }

    success(title, message, options = {}) {
        return this.show({ title, message, type: 'success', ...options });
    }

    warning(title, message, options = {}) {
        return this.show({ title, message, type: 'warning', ...options });
    }

    error(title, message, options = {}) {
        return this.show({ title, message, type: 'error', ...options });
    }

    // 确认对话框
    confirm(title, message, onConfirm, onCancel) {
        const actions = `
            <button class="notification-btn" onclick="notificationSystem.hide(this.closest('.notification')); ${onCancel ? onCancel.toString() + '()' : ''}">取消</button>
            <button class="notification-btn primary" onclick="notificationSystem.hide(this.closest('.notification')); ${onConfirm.toString()}()">确认</button>
        `;

        return this.show({
            title,
            message,
            type: 'warning',
            duration: 0,
            actions,
            closable: true
        });
    }
}

// 创建全局实例
window.notificationSystem = new NotificationSystem();

// 兼容性方法，替换原生alert
window.showNotification = function(message, title = '提示', type = 'info') {
    return notificationSystem.show({
        title,
        message,
        type
    });
};

// 美化的alert替换
window.beautifulAlert = function(message, title = '提示') {
    return notificationSystem.info(title, message);
};