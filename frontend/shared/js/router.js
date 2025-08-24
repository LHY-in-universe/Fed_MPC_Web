/**
 * 联邦学习平台路由系统
 * 处理页面间导航和URL管理
 */

class Router {
    constructor() {
        this.routes = new Map();
        this.currentRoute = null;
        this.init();
    }

    init() {
        // 监听浏览器前进后退事件
        window.addEventListener('popstate', (event) => {
            this.handlePopState(event);
        });

        // 初始化路由表
        this.setupRoutes();
    }

    /**
     * 设置路由表
     */
    setupRoutes() {
        // 主要页面路由
        this.addRoute('/', {
            path: './index.html',
            name: '首页',
            public: true
        });

        this.addRoute('/index.html', {
            path: './index.html',
            name: '首页',
            public: true
        });

        // 登录相关路由
        this.addRoute('/login/business-type', {
            path: './login/business-type.html',
            name: '选择登录类型',
            public: true
        });

        this.addRoute('/login/client', {
            path: './login/client-login.html',
            name: '客户端登录',
            public: true
        });

        this.addRoute('/login/server', {
            path: './login/server-login.html',
            name: '服务器登录',
            public: true
        });

        // 客户端路由
        this.addRoute('/client/dashboard', {
            path: './client/dashboard.html',
            name: '客户端仪表盘',
            requireAuth: true,
            userType: 'client'
        });

        // 服务器路由
        this.addRoute('/server/admin-dashboard', {
            path: './server/admin-dashboard.html',
            name: '管理员仪表盘',
            requireAuth: true,
            userType: 'server'
        });

        this.addRoute('/server/clients', {
            path: './server/admin-dashboard.html#clients',
            name: '客户端管理',
            requireAuth: true,
            userType: 'server'
        });

        this.addRoute('/server/models', {
            path: './server/admin-dashboard.html#models',
            name: '模型管理',
            requireAuth: true,
            userType: 'server'
        });
    }

    /**
     * 添加路由
     */
    addRoute(path, config) {
        this.routes.set(path, config);
    }

    /**
     * 获取路由
     */
    getRoute(path) {
        return this.routes.get(path);
    }

    /**
     * 导航到指定路径
     */
    navigateTo(path, params = {}) {
        const route = this.getRoute(path);
        
        if (!route) {
            console.error(`Route not found: ${path}`);
            this.navigateTo('/');
            return;
        }

        // 检查认证要求
        if (route.requireAuth && !window.authSystem.isLoggedIn()) {
            this.navigateTo('/');
            return;
        }

        // 检查用户类型要求
        if (route.userType && !window.authSystem.hasPermission(route.userType)) {
            this.redirectToUserDashboard();
            return;
        }

        // 构建完整URL
        let fullUrl = route.path;
        
        // 添加查询参数
        if (Object.keys(params).length > 0) {
            const searchParams = new URLSearchParams(params);
            fullUrl += (fullUrl.includes('?') ? '&' : '?') + searchParams.toString();
        }

        // 执行导航
        this.executeNavigation(fullUrl, route);
    }

    /**
     * 执行导航
     */
    executeNavigation(url, route) {
        // 更新浏览器历史
        if (url !== window.location.href) {
            window.history.pushState({ route: route }, route.name, url);
        }

        // 如果是当前页面内的导航（SPA模式）
        if (this.isCurrentPageNavigation(url)) {
            this.handleSPANavigation(url, route);
        } else {
            // 完整页面跳转
            window.location.href = url;
        }

        this.currentRoute = route;
    }

    /**
     * 检查是否为当前页面内导航
     */
    isCurrentPageNavigation(url) {
        const currentPage = window.location.pathname.split('/').pop();
        const targetPage = url.split('/').pop().split('?')[0].split('#')[0];
        
        return currentPage === targetPage;
    }

    /**
     * 处理SPA内部导航
     */
    handleSPANavigation(url, route) {
        // 处理hash变化
        if (url.includes('#')) {
            const hash = url.split('#')[1];
            this.handleHashNavigation(hash);
        }
    }

    /**
     * 处理hash导航
     */
    handleHashNavigation(hash) {
        // 触发自定义事件，让页面组件响应
        const event = new CustomEvent('routeChange', {
            detail: { hash: hash }
        });
        window.dispatchEvent(event);
    }

    /**
     * 重定向到用户仪表盘
     */
    redirectToUserDashboard() {
        const userData = window.authSystem.getCurrentUser();
        
        if (!userData) {
            this.navigateTo('/');
            return;
        }

        if (userData.userType === 'client') {
            window.location.href = '../client/dashboard.html';
        } else if (userData.userType === 'server') {
            window.location.href = '../server/admin-dashboard.html';
        } else {
            this.navigateTo('/');
        }
    }

    /**
     * 处理浏览器前进后退
     */
    handlePopState(event) {
        if (event.state && event.state.route) {
            this.currentRoute = event.state.route;
            // 重新加载页面内容
            window.location.reload();
        }
    }

    /**
     * 获取当前路由
     */
    getCurrentRoute() {
        return this.currentRoute;
    }

    /**
     * 构建URL
     */
    buildUrl(path, params = {}) {
        const route = this.getRoute(path);
        if (!route) return path;

        let url = route.path;
        
        if (Object.keys(params).length > 0) {
            const searchParams = new URLSearchParams(params);
            url += (url.includes('?') ? '&' : '?') + searchParams.toString();
        }

        return url;
    }

    /**
     * 解析URL参数
     */
    parseParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const params = {};
        
        for (const [key, value] of urlParams.entries()) {
            params[key] = value;
        }

        return params;
    }

    /**
     * 获取业务类型相关的路径前缀
     */
    getBusinessPath(businessType) {
        const basePaths = {
            ai: './ai/',
            blockchain: './blockchain/'
        };

        return basePaths[businessType] || './';
    }

    /**
     * 面包屑导航
     */
    getBreadcrumbs() {
        const currentPath = window.location.pathname;
        const breadcrumbs = [];

        // 根据当前路径生成面包屑
        const pathSegments = currentPath.split('/').filter(segment => segment);
        
        let buildPath = '';
        for (let i = 0; i < pathSegments.length; i++) {
            buildPath += '/' + pathSegments[i];
            const route = this.getRoute(buildPath) || this.routes.get('/' + pathSegments[i]);
            
            if (route) {
                breadcrumbs.push({
                    name: route.name,
                    path: buildPath,
                    isLast: i === pathSegments.length - 1
                });
            }
        }

        return breadcrumbs;
    }

    /**
     * 检查路由权限
     */
    canAccess(path) {
        const route = this.getRoute(path);
        
        if (!route) return false;
        if (route.public) return true;
        if (route.requireAuth && !window.authSystem.isLoggedIn()) return false;
        if (route.userType && !window.authSystem.hasPermission(route.userType)) return false;

        return true;
    }

    /**
     * 获取用户可访问的路由列表
     */
    getAccessibleRoutes() {
        const accessibleRoutes = [];
        
        for (const [path, route] of this.routes.entries()) {
            if (this.canAccess(path)) {
                accessibleRoutes.push({
                    path: path,
                    ...route
                });
            }
        }

        return accessibleRoutes;
    }
}

// 创建全局路由实例
window.router = new Router();

// 便捷的导航函数
window.navigateTo = function(path, params = {}) {
    window.router.navigateTo(path, params);
};

// 便捷的URL构建函数
window.buildUrl = function(path, params = {}) {
    return window.router.buildUrl(path, params);
};

// 导出路由系统（用于模块化）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Router;
}