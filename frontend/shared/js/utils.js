/**
 * 联邦学习平台 - 工具函数库
 * 提供通用的工具函数和帮助方法
 */

// 工具函数命名空间
const FedUtils = {
    
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
        }
    },
    
    /**
     * 防抖和节流工具
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
     * 等待指定时间
     * @param {number} ms - 毫秒数
     * @returns {Promise} Promise对象
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
};

// 导出到全局
if (typeof window !== 'undefined') {
    window.FedUtils = FedUtils;
}

// 模块化导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FedUtils;
}