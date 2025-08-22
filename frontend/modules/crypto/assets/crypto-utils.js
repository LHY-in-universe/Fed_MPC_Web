/**
 * 密钥加密签名模块 - 工具函数
 * 提供加密模块专用的工具函数
 */

class CryptoUtils {
    
    /**
     * API请求工具
     */
    static async apiRequest(endpoint, options = {}) {
        const baseUrl = CryptoConstants.API.BASE_URL;
        const url = `${baseUrl}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...authSystem.getAuthHeaders()
            }
        };
        
        const requestOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };
        
        try {
            const response = await fetch(url, requestOptions);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || `HTTP ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API请求失败:', error);
            throw error;
        }
    }
    
    /**
     * 格式化文件大小
     */
    static formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    /**
     * 格式化时间
     */
    static formatDateTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }
    
    /**
     * 验证密钥名称
     */
    static validateKeyName(name) {
        const rules = CryptoConstants.VALIDATION.KEY_NAME;
        
        if (!name || name.length < rules.MIN_LENGTH) {
            return { valid: false, message: `密钥名称不能少于${rules.MIN_LENGTH}个字符` };
        }
        
        if (name.length > rules.MAX_LENGTH) {
            return { valid: false, message: `密钥名称不能超过${rules.MAX_LENGTH}个字符` };
        }
        
        if (!rules.PATTERN.test(name)) {
            return { valid: false, message: '密钥名称只能包含字母、数字、中文、下划线、空格和连字符' };
        }
        
        return { valid: true };
    }
    
    /**
     * 验证密码强度
     */
    static validatePassphrase(passphrase) {
        if (!passphrase) {
            return { valid: true, strength: 0 }; // 密码可选
        }
        
        const rules = CryptoConstants.VALIDATION.PASSPHRASE;
        let strength = 0;
        const messages = [];
        
        if (passphrase.length < rules.MIN_LENGTH) {
            messages.push(`密码长度不能少于${rules.MIN_LENGTH}个字符`);
        } else {
            strength += 1;
        }
        
        if (passphrase.length > rules.MAX_LENGTH) {
            messages.push(`密码长度不能超过${rules.MAX_LENGTH}个字符`);
        }
        
        // 检查复杂度
        const patterns = rules.REQUIRED_PATTERNS;
        let complexityScore = 0;
        
        if (patterns[0].test(passphrase)) complexityScore++; // 小写字母
        if (patterns[1].test(passphrase)) complexityScore++; // 大写字母
        if (patterns[2].test(passphrase)) complexityScore++; // 数字
        if (patterns[3].test(passphrase)) complexityScore++; // 特殊字符
        
        strength += complexityScore;
        
        let strengthText = '';
        if (strength <= 2) {
            strengthText = '弱';
        } else if (strength <= 3) {
            strengthText = '中等';
        } else if (strength <= 4) {
            strengthText = '强';
        } else {
            strengthText = '很强';
        }
        
        return {
            valid: messages.length === 0 && complexityScore >= 3,
            strength: strength,
            strengthText: strengthText,
            messages: messages
        };
    }
    
    /**
     * 生成密钥指纹显示格式
     */
    static formatFingerprint(fingerprint) {
        if (!fingerprint) return '';
        
        // 每4个字符添加一个空格
        return fingerprint.toUpperCase().replace(/(.{4})/g, '$1 ').trim();
    }
    
    /**
     * 获取密钥状态颜色
     */
    static getKeyStatusColor(status) {
        const statusConfig = CryptoConstants.KEY_STATUS[status.toUpperCase()];
        return statusConfig ? statusConfig.color : '#6b7280';
    }
    
    /**
     * 获取密钥状态图标
     */
    static getKeyStatusIcon(status) {
        const statusConfig = CryptoConstants.KEY_STATUS[status.toUpperCase()];
        return statusConfig ? statusConfig.icon : 'question-mark-circle';
    }
    
    /**
     * 下载文件
     */
    static downloadFile(content, filename, contentType = 'text/plain') {
        const blob = new Blob([content], { type: contentType });
        const url = window.URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.style.display = 'none';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        window.URL.revokeObjectURL(url);
    }
    
    /**
     * 显示通知消息
     */
    static showNotification(message, type = 'info', duration = 3000) {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm transition-all duration-300 transform translate-x-full`;
        
        // 设置样式
        const colors = {
            'success': 'bg-green-500 text-white',
            'error': 'bg-red-500 text-white',
            'warning': 'bg-yellow-500 text-white',
            'info': 'bg-blue-500 text-white'
        };
        
        notification.className += ` ${colors[type] || colors.info}`;
        notification.textContent = message;
        
        // 添加到页面
        document.body.appendChild(notification);
        
        // 显示动画
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);
        
        // 自动隐藏
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, duration);
    }
    
    /**
     * 读取文件内容
     */
    static readFileContent(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                resolve(e.target.result);
            };
            
            reader.onerror = function(e) {
                reject(new Error('文件读取失败'));
            };
            
            reader.readAsArrayBuffer(file);
        });
    }
    
    /**
     * 验证文件类型
     */
    static validateFileType(file, allowedTypes) {
        const extension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
        return allowedTypes.includes(extension);
    }
    
    /**
     * 验证文件大小
     */
    static validateFileSize(file, maxSize) {
        return file.size <= maxSize;
    }
    
    /**
     * 复制文本到剪贴板
     */
    static async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showNotification('已复制到剪贴板', 'success');
            return true;
        } catch (error) {
            console.error('复制失败:', error);
            this.showNotification('复制失败', 'error');
            return false;
        }
    }
    
    /**
     * 生成随机字符串
     */
    static generateRandomString(length = 16) {
        const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let result = '';
        
        for (let i = 0; i < length; i++) {
            result += charset.charAt(Math.floor(Math.random() * charset.length));
        }
        
        return result;
    }
    
    /**
     * 防抖函数
     */
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    /**
     * 加载状态管理
     */
    static setLoading(element, loading = true) {
        if (loading) {
            element.disabled = true;
            element.dataset.originalText = element.textContent;
            element.innerHTML = `
                <svg class="animate-spin -ml-1 mr-3 h-4 w-4 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                处理中...
            `;
        } else {
            element.disabled = false;
            element.textContent = element.dataset.originalText || '提交';
        }
    }
    
    /**
     * 表单验证
     */
    static validateForm(formElement) {
        const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;
        const errors = [];
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                errors.push(`${input.dataset.label || '字段'}不能为空`);
                input.classList.add('border-red-500');
            } else {
                input.classList.remove('border-red-500');
            }
        });
        
        return { isValid, errors };
    }
    
    /**
     * 格式化JSON显示
     */
    static formatJSON(obj, indent = 2) {
        return JSON.stringify(obj, null, indent);
    }
    
    /**
     * 安全地解析JSON
     */
    static safeParseJSON(str, defaultValue = null) {
        try {
            return JSON.parse(str);
        } catch (error) {
            console.warn('JSON解析失败:', error);
            return defaultValue;
        }
    }
}

// 导出到全局
if (typeof window !== 'undefined') {
    window.CryptoUtils = CryptoUtils;
}

// 模块化导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CryptoUtils;
}