/**
 * 联邦学习平台认证系统
 * 管理用户登录状态、权限验证和路由跳转
 */

class AuthSystem {
    constructor() {
        this.userData = null;
        this.sessionTimeout = 24 * 60 * 60 * 1000; // 24 hours in milliseconds
        this.init();
    }

    init() {
        this.loadUserData();
        this.setupSessionCheck();
    }

    /**
     * 加载用户数据
     */
    loadUserData() {
        const storedData = localStorage.getItem('userData');
        if (storedData) {
            try {
                this.userData = JSON.parse(storedData);
                // 检查会话是否过期
                if (this.isSessionExpired()) {
                    this.logout();
                    return;
                }
            } catch (error) {
                console.error('Failed to parse user data:', error);
                this.logout();
            }
        }
    }

    /**
     * 检查会话是否过期
     */
    isSessionExpired() {
        if (!this.userData || !this.userData.loginTime) {
            return true;
        }

        const loginTime = new Date(this.userData.loginTime);
        const currentTime = new Date();
        const sessionDuration = currentTime - loginTime;

        return sessionDuration > this.sessionTimeout;
    }

    /**
     * 用户登录
     */
    login(userData) {
        // 添加登录时间
        userData.loginTime = new Date().toISOString();
        
        // 存储用户数据
        localStorage.setItem('userData', JSON.stringify(userData));
        this.userData = userData;

        // 根据用户类型跳转到相应页面
        this.redirectAfterLogin();
    }

    /**
     * 登录后重定向
     */
    redirectAfterLogin() {
        if (!this.userData) return;

        const { userType } = this.userData;
        
        if (userType === 'client') {
            window.location.href = '../client/dashboard.html';
        } else if (userType === 'server') {
            window.location.href = '../server/admin-dashboard.html';
        }
    }

    /**
     * 用户登出
     */
    logout() {
        // 清除本地存储
        localStorage.removeItem('userData');
        localStorage.removeItem('clientProjects');
        localStorage.removeItem('rememberClient');
        localStorage.removeItem('rememberServer');
        
        this.userData = null;
        
        // 跳转到首页
        window.location.href = this.getIndexPath();
    }

    /**
     * 获取首页路径（根据当前页面位置计算）
     */
    getIndexPath() {
        const currentPath = window.location.pathname;
        
        if (currentPath.includes('/login/')) {
            return '../index.html';
        } else if (currentPath.includes('/client/') || currentPath.includes('/server/')) {
            return '../index.html';
        } else {
            return './index.html';
        }
    }

    /**
     * 检查用户是否已登录
     */
    isLoggedIn() {
        return this.userData !== null && !this.isSessionExpired();
    }

    /**
     * 获取当前用户数据
     */
    getCurrentUser() {
        return this.userData;
    }

    /**
     * 验证用户权限
     */
    hasPermission(requiredUserType) {
        if (!this.isLoggedIn()) {
            return false;
        }

        return this.userData.userType === requiredUserType;
    }

    /**
     * 页面访问权限检查
     */
    checkPageAccess(requiredUserType) {
        if (!this.isLoggedIn()) {
            // 未登录，跳转到首页
            window.location.href = this.getIndexPath();
            return false;
        }

        if (!this.hasPermission(requiredUserType)) {
            // 权限不足，跳转到相应的仪表盘
            if (this.userData.userType === 'client') {
                window.location.href = '../client/dashboard.html';
            } else if (this.userData.userType === 'server') {
                window.location.href = '../server/admin-dashboard.html';
            }
            return false;
        }

        return true;
    }

    /**
     * 设置会话检查
     */
    setupSessionCheck() {
        // 每5分钟检查一次会话状态
        setInterval(() => {
            if (this.userData && this.isSessionExpired()) {
                alert('会话已过期，请重新登录');
                this.logout();
            }
        }, 5 * 60 * 1000);

        // 页面可见性变化时检查会话
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible' && this.userData && this.isSessionExpired()) {
                alert('会话已过期，请重新登录');
                this.logout();
            }
        });
    }

    /**
     * 更新用户数据
     */
    updateUserData(updatedData) {
        if (this.userData) {
            this.userData = { ...this.userData, ...updatedData };
            localStorage.setItem('userData', JSON.stringify(this.userData));
        }
    }

    /**
     * 获取业务类型配置
     */
    getBusinessConfig() {
        if (!this.userData) return null;

        const businessType = this.userData.businessType;
        
        if (businessType === 'ai') {
            return {
                type: 'ai',
                name: 'AI大模型业务',
                primaryColor: '#f093fb',
                secondaryColor: '#f5576c',
                icon: 'lightbulb'
            };
        } else if (businessType === 'blockchain') {
            return {
                type: 'blockchain',
                name: '金融区块链业务',
                primaryColor: '#4facfe',
                secondaryColor: '#00f2fe',
                icon: 'currency-dollar'
            };
        }

        return null;
    }

    /**
     * 检查是否为演示账号
     */
    isDemoUser() {
        return this.userData && this.userData.isDemo === true;
    }

    /**
     * 生成API请求头
     */
    getAuthHeaders() {
        if (!this.isLoggedIn()) {
            return {};
        }

        return {
            'Authorization': `Bearer ${this.generateToken()}`,
            'Content-Type': 'application/json',
            'X-User-Type': this.userData.userType,
            'X-Business-Type': this.userData.businessType
        };
    }

    /**
     * 生成临时token（用于API请求）
     */
    generateToken() {
        if (!this.userData) return '';
        
        // 简单的token生成（实际应用中应该使用更安全的方法）
        const payload = {
            userId: this.userData.username || this.userData.adminId,
            userType: this.userData.userType,
            loginTime: this.userData.loginTime
        };
        
        return btoa(JSON.stringify(payload));
    }

    /**
     * 记住登录状态
     */
    setRememberLogin(remember, userType) {
        if (remember) {
            localStorage.setItem(`remember${userType.charAt(0).toUpperCase() + userType.slice(1)}`, 'true');
        } else {
            localStorage.removeItem(`remember${userType.charAt(0).toUpperCase() + userType.slice(1)}`);
        }
    }

    /**
     * 检查是否记住登录
     */
    shouldRememberLogin(userType) {
        return localStorage.getItem(`remember${userType.charAt(0).toUpperCase() + userType.slice(1)}`) === 'true';
    }
}

// 创建全局认证实例
window.authSystem = new AuthSystem();

// 页面加载完成后初始化认证检查
document.addEventListener('DOMContentLoaded', function() {
    // 为登录页面添加便捷方法
    if (window.location.pathname.includes('/login/')) {
        window.loginUser = function(userData, remember = false) {
            authSystem.setRememberLogin(remember, userData.userType);
            authSystem.login(userData);
        };
    }
    
    // 为客户端页面添加权限检查
    if (window.location.pathname.includes('/client/')) {
        if (!authSystem.checkPageAccess('client')) {
            return;
        }
    }
    
    // 为服务器页面添加权限检查
    if (window.location.pathname.includes('/server/')) {
        if (!authSystem.checkPageAccess('server')) {
            return;
        }
    }
});

// 导出认证系统（用于模块化）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthSystem;
}