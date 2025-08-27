/**
 * API配置文件
 * 管理后端API接口的基础URL和公共方法
 */

class ApiManager {
    constructor() {
        this.baseURL = 'http://127.0.0.1:5001/api';
        this.token = localStorage.getItem('authToken');
    }

    // 设置认证token
    setToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem('authToken', token);
        } else {
            localStorage.removeItem('authToken');
        }
    }

    // 获取请求头
    getHeaders(additionalHeaders = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...additionalHeaders
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        return headers;
    }

    // 通用请求方法
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: this.getHeaders(options.headers),
            ...options
        };

        try {
            console.log(`API Request: ${options.method || 'GET'} ${url}`);
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }

            console.log(`API Response:`, data);
            return data;
        } catch (error) {
            console.error(`API Error for ${url}:`, error);
            throw error;
        }
    }

    // GET请求
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    // POST请求
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // PUT请求
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // DELETE请求
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    // 认证相关API
    async login(loginData) {
        const result = await this.post('/auth/login', loginData);
        if (result.success && result.token) {
            this.setToken(result.token);
        }
        return result;
    }

    async verifyToken() {
        return this.get('/auth/verify');
    }

    async logout() {
        const result = await this.post('/auth/logout', {});
        this.setToken(null);
        return result;
    }

    // 业务模块API
    async getAIDashboard() {
        return this.get('/ai/dashboard');
    }

    async getBlockchainDashboard() {
        return this.get('/blockchain/dashboard');
    }

    async getCryptoDashboard() {
        return this.get('/crypto/dashboard');
    }

    // 健康检查
    async healthCheck() {
        return this.get('/health');
    }
}

// 创建全局API管理器实例
window.apiManager = new ApiManager();

// 页面加载时检查后端连接
document.addEventListener('DOMContentLoaded', async function() {
    try {
        const health = await window.apiManager.healthCheck();
        console.log('✅ 后端连接成功:', health);
    } catch (error) {
        console.error('❌ 后端连接失败:', error);
        // 可以显示一个提示给用户
        if (document.querySelector('.backend-status')) {
            document.querySelector('.backend-status').textContent = '后端服务连接失败';
        }
    }
});