/**
 * API客户端 - 统一的前后端数据交互接口
 * 提供认证、请求拦截、错误处理等功能
 */

class ApiClient {
    constructor() {
        this.baseURL = 'http://127.0.0.1:5000/api';
        this.token = localStorage.getItem('token');
        this.user = JSON.parse(localStorage.getItem('user') || '{}');
        
        // 请求拦截器配置
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
        
        // 如果有token，添加到headers
        if (this.token) {
            this.defaultHeaders['Authorization'] = `Bearer ${this.token}`;
        }
        
        // 如果有用户信息，添加业务类型和用户类型
        if (this.user.businessType) {
            this.defaultHeaders['X-Business-Type'] = this.user.businessType;
        }
        if (this.user.userType) {
            this.defaultHeaders['X-User-Type'] = this.user.userType;
        }
    }

    // 更新认证信息
    updateAuth(token, user) {
        this.token = token;
        this.user = user;
        
        if (token) {
            this.defaultHeaders['Authorization'] = `Bearer ${token}`;
        } else {
            delete this.defaultHeaders['Authorization'];
        }
        
        if (user.businessType) {
            this.defaultHeaders['X-Business-Type'] = user.businessType;
        }
        if (user.userType) {
            this.defaultHeaders['X-User-Type'] = user.userType;
        }
    }

    // 通用请求方法
    async request(method, endpoint, data = null, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const config = {
            method: method.toUpperCase(),
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options
        };

        // 添加请求体
        if (data && ['POST', 'PUT', 'PATCH'].includes(config.method)) {
            if (data instanceof FormData) {
                // FormData情况下不设置Content-Type，让浏览器自动设置
                delete config.headers['Content-Type'];
                config.body = data;
            } else {
                config.body = JSON.stringify(data);
            }
        }

        try {
            console.log(`🌐 API请求: ${config.method} ${url}`, data);
            
            const response = await fetch(url, config);
            const responseData = await response.json().catch(() => ({}));

            if (!response.ok) {
                throw new ApiError(
                    responseData.message || responseData.error || '请求失败',
                    response.status,
                    responseData
                );
            }

            console.log(`✅ API响应:`, responseData);
            return responseData;

        } catch (error) {
            console.error(`❌ API错误:`, error);
            
            // 处理网络错误
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new ApiError('网络连接失败，请检查服务器状态', 0);
            }
            
            // 处理认证错误
            if (error.status === 401) {
                this.handleAuthError();
            }
            
            throw error;
        }
    }

    // HTTP方法快捷方式
    get(endpoint, options = {}) {
        return this.request('GET', endpoint, null, options);
    }

    post(endpoint, data, options = {}) {
        return this.request('POST', endpoint, data, options);
    }

    put(endpoint, data, options = {}) {
        return this.request('PUT', endpoint, data, options);
    }

    patch(endpoint, data, options = {}) {
        return this.request('PATCH', endpoint, data, options);
    }

    delete(endpoint, options = {}) {
        return this.request('DELETE', endpoint, null, options);
    }

    // 处理认证错误
    handleAuthError() {
        console.warn('认证失败，清除本地存储并跳转到登录页');
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('loginTime');
        
        // 根据当前业务类型跳转到相应的登录页
        const currentPath = window.location.pathname;
        if (currentPath.includes('/ai/')) {
            window.location.href = '../pages/login.html';
        } else if (currentPath.includes('/blockchain/')) {
            window.location.href = '../pages/login.html';
        } else if (currentPath.includes('/crypto/')) {
            window.location.href = '../pages/login.html';
        } else {
            window.location.href = '/homepage/index.html';
        }
    }

    // 文件上传
    async uploadFile(endpoint, file, additionalData = {}) {
        const formData = new FormData();
        formData.append('file', file);
        
        // 添加额外数据
        Object.keys(additionalData).forEach(key => {
            formData.append(key, additionalData[key]);
        });

        return this.request('POST', endpoint, formData);
    }

    // 健康检查
    async healthCheck() {
        return this.get('/health');
    }

    // 获取系统状态
    async getSystemStatus() {
        return this.get('/status');
    }

    // ==================== 认证相关API ====================
    
    // 用户登录
    async login(credentials) {
        return this.post('/auth/login', credentials);
    }

    // 用户注册
    async register(userData) {
        return this.post('/auth/register', userData);
    }

    // 用户登出
    async logout() {
        return this.post('/auth/logout');
    }

    // 刷新token
    async refreshToken() {
        return this.post('/auth/refresh');
    }

    // 验证token
    async verifyToken() {
        return this.get('/auth/verify');
    }

    // ==================== AI模块API ====================
    
    // 获取训练项目列表
    async getAiProjects() {
        return this.get('/ai/projects');
    }

    // 创建训练项目
    async createAiProject(projectData) {
        return this.post('/ai/projects', projectData);
    }

    // 获取项目详情
    async getAiProject(projectId) {
        return this.get(`/ai/projects/${projectId}`);
    }

    // 获取训练会话列表
    async getTrainingSessions() {
        return this.get('/ai/training/sessions');
    }

    // 创建训练会话
    async createTrainingSession(sessionData) {
        return this.post('/ai/training/sessions', sessionData);
    }

    // 加入训练会话
    async joinTrainingSession(sessionId) {
        return this.post(`/ai/training/sessions/${sessionId}/join`);
    }

    // 获取模型列表
    async getAiModels() {
        return this.get('/ai/models');
    }

    // 上传模型文件
    async uploadModel(file, metadata) {
        return this.uploadFile('/ai/models/upload', file, metadata);
    }

    // 获取数据集列表
    async getDatasets() {
        return this.get('/ai/datasets');
    }

    // 上传数据集
    async uploadDataset(file, metadata) {
        return this.uploadFile('/ai/datasets/upload', file, metadata);
    }

    // ==================== 区块链模块API ====================
    
    // 获取交易列表
    async getTransactions() {
        return this.get('/blockchain/transactions');
    }

    // 创建交易
    async createTransaction(transactionData) {
        return this.post('/blockchain/transactions', transactionData);
    }

    // 获取交易详情
    async getTransaction(txHash) {
        return this.get(`/blockchain/transactions/${txHash}`);
    }

    // 获取智能合约列表
    async getContracts() {
        return this.get('/blockchain/contracts');
    }

    // 部署智能合约
    async deployContract(contractData) {
        return this.post('/blockchain/contracts', contractData);
    }

    // 调用智能合约
    async callContract(contractAddress, method, params) {
        return this.post(`/blockchain/contracts/${contractAddress}/call`, {
            method,
            params
        });
    }

    // 获取网络状态
    async getBlockchainNetworkStatus() {
        return this.get('/blockchain/network/status');
    }

    // ==================== 密钥加密模块API ====================
    
    // 获取密钥列表
    async getKeys() {
        return this.get('/crypto/keys');
    }

    // 生成密钥对
    async generateKeyPair(keyData) {
        return this.post('/crypto/keys/generate', keyData);
    }

    // 导入密钥
    async importKey(file, metadata) {
        return this.uploadFile('/crypto/keys/import', file, metadata);
    }

    // 获取证书列表
    async getCertificates() {
        return this.get('/crypto/certificates');
    }

    // 创建证书
    async createCertificate(certData) {
        return this.post('/crypto/certificates', certData);
    }

    // 导入证书
    async importCertificate(file, metadata) {
        return this.uploadFile('/crypto/certificates/import', file, metadata);
    }

    // 加密数据
    async encryptData(data, keyId) {
        return this.post('/crypto/encryption/encrypt', { data, keyId });
    }

    // 解密数据
    async decryptData(encryptedData, keyId) {
        return this.post('/crypto/encryption/decrypt', { encryptedData, keyId });
    }

    // ==================== 客户端/服务器特定API ====================
    
    // 客户端状态报告
    async reportClientStatus(statusData) {
        return this.post('/client/status', statusData);
    }

    // 获取服务器统计信息
    async getServerStats() {
        return this.get('/server/stats');
    }

    // 获取连接的客户端列表
    async getConnectedClients() {
        return this.get('/server/clients');
    }

    // 踢出客户端
    async kickClient(clientId) {
        return this.post(`/server/clients/${clientId}/kick`);
    }
}

// 自定义API错误类
class ApiError extends Error {
    constructor(message, status = 500, details = null) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.details = details;
    }
}

// 创建全局API客户端实例
window.apiClient = new ApiClient();

// 导出API客户端类
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ApiClient, ApiError };
}