/**
 * 单页应用路由系统
 * 支持模块间的无刷新跳转和状态管理
 */

class FedRouter {
    constructor() {
        this.routes = new Map();
        this.currentRoute = null;
        this.history = [];
        this.maxHistoryLength = 50;
        this.init();
    }

    /**
     * 初始化路由系统
     */
    init() {
        this.setupRoutes();
        this.bindEvents();
        this.handleInitialRoute();
    }

    /**
     * 设置路由配置
     */
    setupRoutes() {
        // 定义模块路由
        this.routes.set('/', {
            module: 'homepage',
            path: '/frontend/homepage/index.html',
            title: '联邦学习平台 - 主页',
            description: '联邦学习平台主页'
        });

        this.routes.set('/homepage', {
            module: 'homepage',
            path: '/frontend/homepage/index.html',
            title: '联邦学习平台 - 主页',
            description: '联邦学习平台主页'
        });

        this.routes.set('/homepage/modules', {
            module: 'homepage',
            path: '/frontend/homepage/modules-select.html',
            title: '模块选择 - 联邦学习平台',
            description: '选择业务模块'
        });

        this.routes.set('/ai', {
            module: 'ai',
            path: '/frontend/ai/pages/dashboard.html',
            title: 'AI智能 - 联邦学习平台',
            description: 'AI模型训练和管理'
        });

        this.routes.set('/ai/dashboard', {
            module: 'ai',
            path: '/frontend/ai/pages/dashboard.html',
            title: 'AI控制台 - 联邦学习平台',
            description: 'AI训练监控和项目管理'
        });

        this.routes.set('/blockchain', {
            module: 'blockchain',
            path: '/frontend/blockchain/pages/dashboard.html',
            title: '区块链 - 联邦学习平台',
            description: '区块链网络和智能合约管理'
        });

        this.routes.set('/blockchain/dashboard', {
            module: 'blockchain',
            path: '/frontend/blockchain/pages/dashboard.html',
            title: '区块链控制台 - 联邦学习平台',
            description: '区块链监控和交易管理'
        });

        this.routes.set('/crypto', {
            module: 'crypto',
            path: '/frontend/crypto/pages/crypto-dashboard.html',
            title: '密钥加密 - 联邦学习平台',
            description: '密钥管理和数据加密'
        });

        this.routes.set('/crypto/dashboard', {
            module: 'crypto',
            path: '/frontend/crypto/pages/crypto-dashboard.html',
            title: '加密控制台 - 联邦学习平台',
            description: '密钥生成和证书管理'
        });
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 监听浏览器前进后退
        window.addEventListener('popstate', (event) => {
            this.handlePopState(event);
        });

        // 监听页面内链接点击
        document.addEventListener('click', (event) => {
            this.handleLinkClick(event);
        });

        // 监听页面卸载
        window.addEventListener('beforeunload', () => {
            this.saveState();
        });
    }

    /**
     * 处理初始路由
     */
    handleInitialRoute() {
        const currentPath = window.location.pathname;
        const route = this.findRouteByPath(currentPath);
        
        if (route) {
            this.currentRoute = route;
            this.updatePageState(route);
        }
    }

    /**
     * 根据路径查找路由
     */
    findRouteByPath(path) {
        // 简化路径匹配逻辑
        if (path.includes('/ai/')) return this.routes.get('/ai');
        if (path.includes('/blockchain/')) return this.routes.get('/blockchain');
        if (path.includes('/crypto/')) return this.routes.get('/crypto');
        if (path.includes('/homepage/modules')) return this.routes.get('/homepage/modules');
        if (path.includes('/homepage/')) return this.routes.get('/homepage');
        return this.routes.get('/');
    }

    /**
     * 处理链接点击
     */
    handleLinkClick(event) {
        const link = event.target.closest('a');
        
        if (!link || link.target === '_blank') return;
        
        const href = link.getAttribute('href');
        if (!href || href.startsWith('http') || href.startsWith('mailto:')) return;

        // 检查是否是内部模块链接
        if (this.isInternalLink(href)) {
            event.preventDefault();
            this.navigate(href);
        }
    }

    /**
     * 检查是否是内部链接
     */
    isInternalLink(href) {
        return href.startsWith('/frontend/') || 
               href.startsWith('../') || 
               href.includes('dashboard.html') ||
               href.includes('index.html') ||
               href.includes('modules-select.html');
    }

    /**
     * 导航到指定路径
     */
    navigate(path, pushState = true) {
        const route = this.findRouteByPath(path);
        
        if (!route) {
            console.warn(`Route not found for path: ${path}`);
            window.location.href = path;
            return;
        }

        // 添加到历史记录
        if (this.currentRoute) {
            this.addToHistory(this.currentRoute);
        }

        // 更新当前路由
        this.currentRoute = route;

        // 更新浏览器历史
        if (pushState) {
            history.pushState({ route: route }, route.title, path);
        }

        // 更新页面状态
        this.updatePageState(route);

        // 执行页面跳转
        this.performNavigation(route, path);
    }

    /**
     * 执行页面导航
     */
    performNavigation(route, originalPath) {
        // 显示加载状态
        this.showLoadingState();

        // 保存当前状态
        this.saveNavigationState(route, originalPath);

        // 执行跳转
        setTimeout(() => {
            window.location.href = originalPath;
        }, 500);
    }

    /**
     * 显示加载状态
     */
    showLoadingState() {
        const loadingHTML = `
            <div id="router-loading" class="fixed inset-0 bg-white bg-opacity-90 flex items-center justify-center z-50">
                <div class="text-center">
                    <div class="loading-spinner mx-auto mb-4"></div>
                    <p class="text-gray-600 text-sm">正在跳转到 ${this.currentRoute?.title || '目标页面'}</p>
                    <div class="mt-2 w-32 bg-gray-200 rounded-full h-1 mx-auto">
                        <div class="bg-blue-500 h-1 rounded-full loading-progress"></div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', loadingHTML);

        // 添加进度条动画
        const progressBar = document.querySelector('.loading-progress');
        if (progressBar) {
            progressBar.style.width = '0%';
            setTimeout(() => { progressBar.style.width = '30%'; }, 100);
            setTimeout(() => { progressBar.style.width = '60%'; }, 200);
            setTimeout(() => { progressBar.style.width = '90%'; }, 300);
            setTimeout(() => { progressBar.style.width = '100%'; }, 400);
        }
    }

    /**
     * 保存导航状态
     */
    saveNavigationState(route, path) {
        const navigationState = {
            route: route,
            path: path,
            timestamp: Date.now(),
            userAgent: navigator.userAgent,
            referrer: document.referrer
        };

        FedUtils.storage.set('navigation_state', navigationState);
        
        // 保存到会话历史
        const sessionHistory = FedUtils.storage.get('session_history') || [];
        sessionHistory.push({
            module: route.module,
            title: route.title,
            timestamp: Date.now()
        });

        // 限制历史记录长度
        if (sessionHistory.length > 20) {
            sessionHistory.splice(0, sessionHistory.length - 20);
        }

        FedUtils.storage.set('session_history', sessionHistory);
    }

    /**
     * 处理浏览器前进后退
     */
    handlePopState(event) {
        if (event.state && event.state.route) {
            this.currentRoute = event.state.route;
            this.updatePageState(event.state.route);
        }
    }

    /**
     * 更新页面状态
     */
    updatePageState(route) {
        // 更新页面标题
        document.title = route.title;

        // 更新meta描述
        let metaDescription = document.querySelector('meta[name="description"]');
        if (!metaDescription) {
            metaDescription = document.createElement('meta');
            metaDescription.name = 'description';
            document.head.appendChild(metaDescription);
        }
        metaDescription.content = route.description;

        // 触发路由变化事件
        this.dispatchRouteChangeEvent(route);
    }

    /**
     * 触发路由变化事件
     */
    dispatchRouteChangeEvent(route) {
        const event = new CustomEvent('routeChange', {
            detail: {
                route: route,
                timestamp: Date.now()
            }
        });
        window.dispatchEvent(event);
    }

    /**
     * 添加到历史记录
     */
    addToHistory(route) {
        this.history.push({
            ...route,
            timestamp: Date.now()
        });

        // 限制历史记录长度
        if (this.history.length > this.maxHistoryLength) {
            this.history.shift();
        }
    }

    /**
     * 获取导航历史
     */
    getHistory() {
        return [...this.history];
    }

    /**
     * 返回上一页
     */
    goBack() {
        if (this.history.length > 0) {
            const previousRoute = this.history.pop();
            this.navigate(previousRoute.path, false);
            history.back();
        } else {
            // 如果没有历史记录，返回主页
            this.navigate('/frontend/homepage/index.html');
        }
    }

    /**
     * 保存状态到本地存储
     */
    saveState() {
        const state = {
            currentRoute: this.currentRoute,
            history: this.history,
            timestamp: Date.now()
        };
        
        FedUtils.storage.set('router_state', state);
    }

    /**
     * 从本地存储恢复状态
     */
    restoreState() {
        const state = FedUtils.storage.get('router_state');
        
        if (state && Date.now() - state.timestamp < 24 * 60 * 60 * 1000) { // 24小时内有效
            this.currentRoute = state.currentRoute;
            this.history = state.history || [];
        }
    }

    /**
     * 获取当前模块
     */
    getCurrentModule() {
        return this.currentRoute ? this.currentRoute.module : 'homepage';
    }

    /**
     * 预加载模块资源
     */
    preloadModule(moduleName) {
        const route = this.routes.get(`/${moduleName}`);
        if (route) {
            // 创建隐藏的iframe预加载页面
            const iframe = document.createElement('iframe');
            iframe.src = route.path;
            iframe.style.display = 'none';
            iframe.onload = () => {
                console.log(`Module ${moduleName} preloaded`);
                setTimeout(() => iframe.remove(), 1000);
            };
            document.body.appendChild(iframe);
        }
    }
}

// 全局路由实例
let globalRouter;

// 页面加载时初始化路由系统
document.addEventListener('DOMContentLoaded', () => {
    globalRouter = new FedRouter();
    
    // 恢复之前的状态
    globalRouter.restoreState();
});

// 导出到全局
if (typeof window !== 'undefined') {
    window.FedRouter = FedRouter;
    window.globalRouter = globalRouter;
}