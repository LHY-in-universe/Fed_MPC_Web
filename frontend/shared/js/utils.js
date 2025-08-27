/**
 * 联邦学习平台 - 统一工具函数库
 * 合并通用工具函数和加密模块专用工具函数
 */

// 统一工具函数命名空间
const UnifiedUtils = {
    
    /**
     * 时间和日期工具
     */
    time: {
        /**
         * 格式化时间戳为可读格式
         * @param {number|string|Date} timestamp - 时间戳
         * @param {string} format - 格式类型 ('datetime', 'date', 'time', 'relative')
         * @returns {string} 格式化后的时间字符串
         */
        format(timestamp, format = 'datetime') {
            const date = new Date(timestamp);
            
            if (isNaN(date.getTime())) {
                return '无效时间';
            }
            
            const now = new Date();
            const diff = now - date;
            
            switch (format) {
                case 'datetime':
                    return date.toLocaleString('zh-CN', {
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit'
                    });
                    
                case 'date':
                    return date.toLocaleDateString('zh-CN', {
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit'
                    });
                    
                case 'time':
                    return date.toLocaleTimeString('zh-CN', {
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit'
                    });
                    
                case 'relative':
                    return this.getRelativeTime(diff);
                    
                default:
                    return date.toString();
            }
        },
        
        /**
         * 获取相对时间描述
         * @param {number} diff - 时间差（毫秒）
         * @returns {string} 相对时间描述
         */
        getRelativeTime(diff) {
            const seconds = Math.floor(diff / 1000);
            const minutes = Math.floor(seconds / 60);
            const hours = Math.floor(minutes / 60);
            const days = Math.floor(hours / 24);
            
            if (seconds < 60) return `${seconds}秒前`;
            if (minutes < 60) return `${minutes}分钟前`;
            if (hours < 24) return `${hours}小时前`;
            if (days < 30) return `${days}天前`;
            
            return this.format(new Date(Date.now() - diff), 'date');
        },
        
        /**
         * 获取当前时间戳
         * @returns {string} ISO格式的时间字符串
         */
        now() {
            return new Date().toISOString();
        }
    },
    
    /**
     * 数据格式化工具
     */
    format: {
        /**
         * 格式化文件大小
         * @param {number} bytes - 字节数
         * @returns {string} 格式化后的文件大小
         */
        fileSize(bytes) {
            if (bytes === 0) return '0 B';
            
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            
            return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
        },
        
        /**
         * 格式化数字（添加千分位分隔符）
         * @param {number} num - 数字
         * @returns {string} 格式化后的数字字符串
         */
        number(num) {
            return num.toLocaleString('zh-CN');
        },
        
        /**
         * 格式化百分比
         * @param {number} value - 数值（0-100 或 0-1）
         * @param {number} decimals - 小数位数
         * @param {boolean} isDecimal - 输入是否为小数（0-1）
         * @returns {string} 格式化后的百分比
         */
        percentage(value, decimals = 1, isDecimal = false) {
            const percent = isDecimal ? value * 100 : value;
            return `${percent.toFixed(decimals)}%`;
        },
        
        /**
         * 格式化货币
         * @param {number} amount - 金额
         * @param {string} currency - 货币符号
         * @returns {string} 格式化后的货币字符串
         */
        currency(amount, currency = '¥') {
            return `${currency}${this.number(amount.toFixed(2))}`;
        },
        
        /**
         * 格式化密钥指纹
         * @param {string} fingerprint - 密钥指纹
         * @returns {string} 格式化后的指纹
         */
        fingerprint(fingerprint) {
            if (!fingerprint) return '';
            // 每4个字符添加一个空格
            return fingerprint.toUpperCase().replace(/(.{4})/g, '$1 ').trim();
        },
        
        /**
         * 格式化JSON显示
         * @param {any} obj - 要格式化的对象
         * @param {number} indent - 缩进空格数
         * @returns {string} 格式化后的JSON字符串
         */
        json(obj, indent = 2) {
            return JSON.stringify(obj, null, indent);
        }
    },
    
    /**
     * 本地存储工具
     */
    storage: {
        /**
         * 设置本地存储
         * @param {string} key - 键名
         * @param {any} value - 值
         * @param {number} expiry - 过期时间（小时）
         */
        set(key, value, expiry = null) {
            const item = {
                value: value,
                timestamp: Date.now(),
                expiry: expiry ? Date.now() + (expiry * 60 * 60 * 1000) : null
            };
            localStorage.setItem(key, JSON.stringify(item));
        },
        
        /**
         * 获取本地存储
         * @param {string} key - 键名
         * @returns {any|null} 存储的值或null
         */
        get(key) {
            try {
                const item = JSON.parse(localStorage.getItem(key));
                if (!item) return null;
                
                // 检查是否过期
                if (item.expiry && Date.now() > item.expiry) {
                    this.remove(key);
                    return null;
                }
                
                return item.value;
            } catch (error) {
                console.error('Error getting localStorage item:', error);
                return null;
            }
        },
        
        /**
         * 移除本地存储
         * @param {string} key - 键名
         */
        remove(key) {
            localStorage.removeItem(key);
        },
        
        /**
         * 清空本地存储
         */
        clear() {
            localStorage.clear();
        },
        
        /**
         * 获取存储大小
         * @returns {number} 存储大小（字节）
         */
        getSize() {
            let total = 0;
            for (let key in localStorage) {
                if (localStorage.hasOwnProperty(key)) {
                    total += localStorage[key].length + key.length;
                }
            }
            return total;
        }
    },
    
    /**
     * DOM操作工具
     */
    dom: {
        /**
         * 创建元素
         * @param {string} tag - 标签名
         * @param {Object} attributes - 属性对象
         * @param {string|Element} content - 内容
         * @returns {Element} 创建的元素
         */
        create(tag, attributes = {}, content = '') {
            const element = document.createElement(tag);
            
            // 设置属性
            Object.keys(attributes).forEach(key => {
                if (key === 'className') {
                    element.className = attributes[key];
                } else if (key === 'dataset') {
                    Object.keys(attributes[key]).forEach(dataKey => {
                        element.dataset[dataKey] = attributes[key][dataKey];
                    });
                } else {
                    element.setAttribute(key, attributes[key]);
                }
            });
            
            // 设置内容
            if (typeof content === 'string') {
                element.innerHTML = content;
            } else if (content instanceof Element) {
                element.appendChild(content);
            }
            
            return element;
        },
        
        /**
         * 查询元素
         * @param {string} selector - CSS选择器
         * @param {Element} parent - 父元素
         * @returns {Element|null} 找到的元素
         */
        query(selector, parent = document) {
            return parent.querySelector(selector);
        },
        
        /**
         * 查询所有元素
         * @param {string} selector - CSS选择器
         * @param {Element} parent - 父元素
         * @returns {NodeList} 找到的元素列表
         */
        queryAll(selector, parent = document) {
            return parent.querySelectorAll(selector);
        },
        
        /**
         * 添加事件监听器
         * @param {Element|string} element - 元素或选择器
         * @param {string} event - 事件类型
         * @param {Function} handler - 事件处理函数
         * @param {Object} options - 选项
         */
        on(element, event, handler, options = {}) {
            const target = typeof element === 'string' ? this.query(element) : element;
            if (target) {
                target.addEventListener(event, handler, options);
            }
        },
        
        /**
         * 移除事件监听器
         * @param {Element|string} element - 元素或选择器
         * @param {string} event - 事件类型
         * @param {Function} handler - 事件处理函数
         */
        off(element, event, handler) {
            const target = typeof element === 'string' ? this.query(element) : element;
            if (target) {
                target.removeEventListener(event, handler);
            }
        }
    },
    
    /**
     * 网络请求工具
     */
    http: {
        /**
         * 发送HTTP请求
         * @param {string} url - 请求URL
         * @param {Object} options - 请求选项
         * @returns {Promise} 请求Promise
         */
        async request(url, options = {}) {
            const defaultOptions = {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            };
            
            // 合并选项
            const mergedOptions = { ...defaultOptions, ...options };
            
            // 添加认证头
            if (window.authSystem && window.authSystem.isLoggedIn()) {
                const authHeaders = window.authSystem.getAuthHeaders();
                mergedOptions.headers = { ...mergedOptions.headers, ...authHeaders };
            }
            
            try {
                const response = await fetch(url, mergedOptions);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    return await response.json();
                } else {
                    return await response.text();
                }
            } catch (error) {
                console.error('HTTP request failed:', error);
                throw error;
            }
        },
        
        /**
         * GET请求
         * @param {string} url - 请求URL
         * @param {Object} params - 查询参数
         * @returns {Promise} 请求Promise
         */
        get(url, params = {}) {
            const queryString = new URLSearchParams(params).toString();
            const fullUrl = queryString ? `${url}?${queryString}` : url;
            return this.request(fullUrl);
        },
        
        /**
         * POST请求
         * @param {string} url - 请求URL
         * @param {Object} data - 请求数据
         * @returns {Promise} 请求Promise
         */
        post(url, data = {}) {
            return this.request(url, {
                method: 'POST',
                body: JSON.stringify(data)
            });
        },
        
        /**
         * PUT请求
         * @param {string} url - 请求URL
         * @param {Object} data - 请求数据
         * @returns {Promise} 请求Promise
         */
        put(url, data = {}) {
            return this.request(url, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
        },
        
        /**
         * DELETE请求
         * @param {string} url - 请求URL
         * @returns {Promise} 请求Promise
         */
        delete(url) {
            return this.request(url, {
                method: 'DELETE'
            });
        }
    },
    
    /**
     * 验证工具
     */
    validate: {
        /**
         * 验证邮箱格式
         * @param {string} email - 邮箱地址
         * @returns {boolean} 是否有效
         */
        email(email) {
            const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return regex.test(email);
        },
        
        /**
         * 验证URL格式
         * @param {string} url - URL地址
         * @returns {boolean} 是否有效
         */
        url(url) {
            try {
                new URL(url);
                return true;
            } catch {
                return false;
            }
        },
        
        /**
         * 验证手机号格式
         * @param {string} phone - 手机号
         * @returns {boolean} 是否有效
         */
        phone(phone) {
            const regex = /^1[3-9]\d{9}$/;
            return regex.test(phone);
        },
        
        /**
         * 验证必填项
         * @param {any} value - 值
         * @returns {boolean} 是否有效
         */
        required(value) {
            if (value === null || value === undefined) return false;
            if (typeof value === 'string') return value.trim().length > 0;
            if (Array.isArray(value)) return value.length > 0;
            return true;
        },
        
        /**
         * 验证密钥名称
         * @param {string} name - 密钥名称
         * @returns {Object} 验证结果
         */
        keyName(name) {
            const MIN_LENGTH = 1;
            const MAX_LENGTH = 100;
            const PATTERN = /^[a-zA-Z0-9\u4e00-\u9fa5_\s-]+$/;
            
            if (!name || name.length < MIN_LENGTH) {
                return { valid: false, message: `密钥名称不能少于${MIN_LENGTH}个字符` };
            }
            
            if (name.length > MAX_LENGTH) {
                return { valid: false, message: `密钥名称不能超过${MAX_LENGTH}个字符` };
            }
            
            if (!PATTERN.test(name)) {
                return { valid: false, message: '密钥名称只能包含字母、数字、中文、下划线、空格和连字符' };
            }
            
            return { valid: true };
        },
        
        /**
         * 验证密码强度
         * @param {string} passphrase - 密码
         * @returns {Object} 验证结果
         */
        passphrase(passphrase) {
            if (!passphrase) {
                return { valid: true, strength: 0 }; // 密码可选
            }
            
            const MIN_LENGTH = 8;
            const MAX_LENGTH = 128;
            let strength = 0;
            const messages = [];
            
            if (passphrase.length < MIN_LENGTH) {
                messages.push(`密码长度不能少于${MIN_LENGTH}个字符`);
            } else {
                strength += 1;
            }
            
            if (passphrase.length > MAX_LENGTH) {
                messages.push(`密码长度不能超过${MAX_LENGTH}个字符`);
            }
            
            // 检查复杂度
            const patterns = [
                /[a-z]/,    // 小写字母
                /[A-Z]/,    // 大写字母
                /[0-9]/,    // 数字
                /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/ // 特殊字符
            ];
            let complexityScore = 0;
            
            patterns.forEach(pattern => {
                if (pattern.test(passphrase)) complexityScore++;
            });
            
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
        },
        
        /**
         * 验证表单
         * @param {Element} formElement - 表单元素
         * @returns {Object} 验证结果
         */
        form(formElement) {
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
    },
    
    /**
     * 文件处理工具
     */
    file: {
        /**
         * 读取文件内容
         * @param {File} file - 文件对象
         * @returns {Promise} 文件内容Promise
         */
        readContent(file) {
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
        },
        
        /**
         * 验证文件类型
         * @param {File} file - 文件对象
         * @param {Array} allowedTypes - 允许的文件类型
         * @returns {boolean} 是否有效
         */
        validateType(file, allowedTypes) {
            const extension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
            return allowedTypes.includes(extension);
        },
        
        /**
         * 验证文件大小
         * @param {File} file - 文件对象
         * @param {number} maxSize - 最大大小（字节）
         * @returns {boolean} 是否有效
         */
        validateSize(file, maxSize) {
            return file.size <= maxSize;
        },
        
        /**
         * 下载文件
         * @param {string} content - 文件内容
         * @param {string} filename - 文件名
         * @param {string} contentType - 内容类型
         */
        download(content, filename, contentType = 'text/plain') {
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
    },
    
    /**
     * 通知工具
     */
    notify: {
        /**
         * 显示通知消息
         * @param {string} message - 消息内容
         * @param {string} type - 消息类型
         * @param {number} duration - 显示时长
         */
        show(message, type = 'info', duration = 3000) {
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
        },
        
        success(message, duration = 3000) {
            this.show(message, 'success', duration);
        },
        
        error(message, duration = 3000) {
            this.show(message, 'error', duration);
        },
        
        warning(message, duration = 3000) {
            this.show(message, 'warning', duration);
        },
        
        info(message, duration = 3000) {
            this.show(message, 'info', duration);
        }
    },
    
    /**
     * UI工具
     */
    ui: {
        /**
         * 设置加载状态
         * @param {Element} element - 目标元素
         * @param {boolean} loading - 是否加载中
         */
        setLoading(element, loading = true) {
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
        },
        
        /**
         * 获取状态颜色
         * @param {string} status - 状态
         * @param {string} module - 模块类型
         * @returns {string} 颜色值
         */
        getStatusColor(status, module = 'general') {
            const statusColors = {
                general: {
                    'active': '#10b981',
                    'inactive': '#6b7280',
                    'success': '#10b981',
                    'error': '#ef4444',
                    'warning': '#f59e0b',
                    'info': '#3b82f6'
                },
                crypto: {
                    'active': '#10b981',
                    'expired': '#f59e0b',
                    'revoked': '#ef4444',
                    'archived': '#6b7280'
                }
            };
            
            return statusColors[module]?.[status.toLowerCase()] || '#6b7280';
        }
    },
    
    /**
     * 工具函数
     */
    
    /**
     * 防抖函数
     * @param {Function} func - 要防抖的函数
     * @param {number} wait - 等待时间（毫秒）
     * @returns {Function} 防抖后的函数
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    /**
     * 节流函数
     * @param {Function} func - 要节流的函数
     * @param {number} limit - 限制时间（毫秒）
     * @returns {Function} 节流后的函数
     */
    throttle(func, limit) {
        let lastFunc;
        let lastRan;
        return function(...args) {
            if (!lastRan) {
                func(...args);
                lastRan = Date.now();
            } else {
                clearTimeout(lastFunc);
                lastFunc = setTimeout(() => {
                    if ((Date.now() - lastRan) >= limit) {
                        func(...args);
                        lastRan = Date.now();
                    }
                }, limit - (Date.now() - lastRan));
            }
        };
    },
    
    /**
     * 深度克隆对象
     * @param {any} obj - 要克隆的对象
     * @returns {any} 克隆后的对象
     */
    deepClone(obj) {
        if (obj === null || typeof obj !== 'object') return obj;
        if (obj instanceof Date) return new Date(obj);
        if (obj instanceof Array) return obj.map(item => this.deepClone(item));
        if (typeof obj === 'object') {
            const clonedObj = {};
            Object.keys(obj).forEach(key => {
                clonedObj[key] = this.deepClone(obj[key]);
            });
            return clonedObj;
        }
        return obj;
    },
    
    /**
     * 生成随机ID
     * @param {number} length - ID长度
     * @returns {string} 随机ID
     */
    generateId(length = 8) {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let result = '';
        for (let i = 0; i < length; i++) {
            result += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return result;
    },
    
    /**
     * 生成随机字符串
     * @param {number} length - 字符串长度
     * @returns {string} 随机字符串
     */
    generateRandomString(length = 16) {
        const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let result = '';
        
        for (let i = 0; i < length; i++) {
            result += charset.charAt(Math.floor(Math.random() * charset.length));
        }
        
        return result;
    },
    
    /**
     * 等待指定时间
     * @param {number} ms - 毫秒数
     * @returns {Promise} Promise对象
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },
    
    /**
     * 复制文本到剪贴板
     * @param {string} text - 要复制的文本
     * @returns {Promise} 复制结果
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.notify.success('已复制到剪贴板');
            return true;
        } catch (error) {
            console.error('复制失败:', error);
            this.notify.error('复制失败');
            return false;
        }
    },
    
    /**
     * 安全地解析JSON
     * @param {string} str - JSON字符串
     * @param {any} defaultValue - 默认值
     * @returns {any} 解析结果
     */
    safeParseJSON(str, defaultValue = null) {
        try {
            return JSON.parse(str);
        } catch (error) {
            console.warn('JSON解析失败:', error);
            return defaultValue;
        }
    }
};

// 冻结工具对象，防止修改
Object.freeze(UnifiedUtils);

// 导出到全局
if (typeof window !== 'undefined') {
    window.UnifiedUtils = UnifiedUtils;
    // 保持向后兼容
    window.FedUtils = UnifiedUtils;
    window.CryptoUtils = {
        // 映射到统一工具函数
        formatFileSize: UnifiedUtils.format.fileSize,
        formatDateTime: UnifiedUtils.time.format,
        validateKeyName: UnifiedUtils.validate.keyName,
        validatePassphrase: UnifiedUtils.validate.passphrase,
        formatFingerprint: UnifiedUtils.format.fingerprint,
        downloadFile: UnifiedUtils.file.download,
        showNotification: UnifiedUtils.notify.show,
        readFileContent: UnifiedUtils.file.readContent,
        validateFileType: UnifiedUtils.file.validateType,
        validateFileSize: UnifiedUtils.file.validateSize,
        copyToClipboard: UnifiedUtils.copyToClipboard,
        generateRandomString: UnifiedUtils.generateRandomString,
        debounce: UnifiedUtils.debounce,
        setLoading: UnifiedUtils.ui.setLoading,
        validateForm: UnifiedUtils.validate.form,
        formatJSON: UnifiedUtils.format.json,
        safeParseJSON: UnifiedUtils.safeParseJSON
    };
}

// 模块化导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UnifiedUtils;
}