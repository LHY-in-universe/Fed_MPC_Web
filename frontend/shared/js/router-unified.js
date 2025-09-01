/**
 * 统一路由系统 - 完整整合版
 * 整合所有路由功能，支持模块间导航和状态管理
 * 包含：
 * - 智能路由匹配和管理
 * - 权限验证和身份认证
 * - 状态持久化和恢复
 * - 加载状态和进度指示
 * - 面包屑导航和SEO优化
 * - 历史记录管理
 * - 事件系统和API接口
 * - 向后兼容性支持
 */

class UnifiedRouter {
    constructor() {
        this.routes = new Map();
        this.currentRoute = null;
        this.history = [];
        this.maxHistoryLength = 50;
        this.loadingTimeout = null;
        this.navigationInProgress = false;
        
        this.init();
    }

    // ====================== 初始化系统 ======================
    init() {
        this.setupRoutes();
        this.bindEvents();
        this.handleInitialRoute();
        this.initializeModules();
    }

    setupRoutes() {
        // 主页路由
        this.addRoute('/', {
            module: 'homepage',
            path: 'homepage/index.html',
            title: '联邦学习平台',
            description: '联邦学习、区块链和密码学一体化平台',
            keywords: '联邦学习,AI,区块链,密码学',
            public: true
        });

        this.addRoute('/homepage', {
            module: 'homepage',
            path: 'homepage/index.html',
            title: '联邦学习平台 - 主页',
            description: '联邦学习、区块链和密码学一体化平台主页',
            keywords: '联邦学习,AI,区块链,密码学,主页',
            public: true
        });

        // AI 模块路由
        this.addRoute('/ai', {
            module: 'ai',
            path: 'ai/pages/dashboard.html',
            title: 'AI智能 - 联邦学习平台',
            description: 'AI模型训练和联邦学习管理',
            keywords: '联邦学习,AI,机器学习,模型训练',
            requireAuth: true,
            icon: 'ai'
        });

        this.addRoute('/ai/dashboard', {
            module: 'ai',
            path: '../ai/pages/dashboard.html',
            title: 'AI控制台',
            description: 'AI训练监控和项目管理中心',
            requireAuth: true
        });

        this.addRoute('/ai/training', {
            module: 'ai',
            path: '../ai/pages/training-dashboard.html',
            title: '训练管理',
            description: '联邦学习训练管理和监控',
            requireAuth: true
        });

        this.addRoute('/ai/federated-training', {
            module: 'ai',
            path: '../ai/pages/federated-training.html',
            title: '联邦训练',
            description: '联邦学习训练配置和执行',
            requireAuth: true
        });

        this.addRoute('/ai/local-training', {
            module: 'ai',
            path: '../ai/pages/local-training.html',
            title: '本地训练',
            description: '本地AI模型训练',
            requireAuth: true
        });

        this.addRoute('/ai/mpc-training', {
            module: 'ai',
            path: '../ai/pages/mpc-training.html',
            title: 'MPC训练',
            description: '多方安全计算训练',
            requireAuth: true
        });

        this.addRoute('/ai/models', {
            module: 'ai',
            path: '../ai/pages/model-dashboard.html',
            title: '模型管理',
            description: 'AI模型管理和部署中心',
            requireAuth: true
        });

        this.addRoute('/ai/datasets', {
            module: 'ai',
            path: '../ai/pages/dataset-dashboard.html',
            title: '数据集管理',
            description: '训练数据集管理和分析',
            requireAuth: true
        });

        this.addRoute('/ai/client-dashboard', {
            module: 'ai',
            path: '../ai/pages/client-dashboard.html',
            title: '客户端控制台',
            description: '联邦学习客户端管理',
            requireAuth: true,
            userType: 'client'
        });

        this.addRoute('/ai/server-dashboard', {
            module: 'ai',
            path: '../ai/pages/server-dashboard.html',
            title: '服务器控制台',
            description: '联邦学习服务器管理',
            requireAuth: true,
            userType: 'server'
        });

        // 区块链模块路由
        this.addRoute('/blockchain', {
            module: 'blockchain',
            path: '../blockchain/pages/dashboard.html',
            title: '区块链 - 联邦学习平台',
            description: '区块链网络和智能合约管理',
            keywords: '区块链,智能合约,分布式账本',
            requireAuth: true,
            icon: 'blockchain'
        });

        this.addRoute('/blockchain/dashboard', {
            module: 'blockchain',
            path: '../blockchain/pages/dashboard.html',
            title: '区块链控制台',
            description: '区块链监控和交易管理中心',
            requireAuth: true
        });

        this.addRoute('/blockchain/network', {
            module: 'blockchain',
            path: '../blockchain/pages/network-dashboard.html',
            title: '网络管理',
            description: '区块链网络节点监控和管理',
            requireAuth: true
        });

        this.addRoute('/blockchain/contracts', {
            module: 'blockchain',
            path: '../blockchain/pages/contract-dashboard.html',
            title: '智能合约',
            description: '智能合约管理和部署工具',
            requireAuth: true
        });

        this.addRoute('/blockchain/transactions', {
            module: 'blockchain',
            path: '../blockchain/pages/transaction-dashboard.html',
            title: '交易管理',
            description: '区块链交易监控和分析',
            requireAuth: true
        });

        // 密码学模块路由
        this.addRoute('/crypto', {
            module: 'crypto',
            path: '../crypto/pages/crypto-dashboard.html',
            title: '密钥加密 - 联邦学习平台',
            description: '密钥管理和数据加密工具',
            keywords: '密码学,加密,密钥管理,PKI',
            requireAuth: true,
            icon: 'crypto'
        });

        this.addRoute('/crypto/dashboard', {
            module: 'crypto',
            path: '../crypto/pages/crypto-dashboard.html',
            title: '加密控制台',
            description: '密钥生成和证书管理中心',
            requireAuth: true
        });

        this.addRoute('/crypto/keys', {
            module: 'crypto',
            path: '../crypto/pages/key-dashboard.html',
            title: '密钥管理',
            description: '密钥生成、管理和安全分发',
            requireAuth: true
        });

        this.addRoute('/crypto/encryption', {
            module: 'crypto',
            path: '../crypto/pages/encryption-dashboard.html',
            title: '数据加密',
            description: '数据加密和解密工具集',
            requireAuth: true
        });

        this.addRoute('/crypto/certificates', {
            module: 'crypto',
            path: '../crypto/pages/certificate-dashboard.html',
            title: '证书管理',
            description: 'PKI证书管理和数字签名验证',
            requireAuth: true
        });

        // 认证相关路由
        this.addRoute('/login', {
            module: 'auth',
            path: '../ai/pages/login.html',
            title: '用户登录',
            description: '用户身份验证和登录',
            keywords: '登录,身份验证,用户认证',
            public: true
        });

        this.addRoute('/user-type-select', {
            module: 'auth',
            path: '../ai/pages/user-type-select.html',
            title: '用户类型选择',
            description: '选择用户类型和角色',
            keywords: '用户类型,角色选择',
            public: true
        });

        this.addRoute('/federated-training-select', {
            module: 'ai',
            path: '../ai/pages/federated-training-select.html',
            title: '联邦训练选择',
            description: '选择联邦训练类型和参数',
            requireAuth: true
        });
    }

    // ====================== 路由管理 ======================
    addRoute(path, config) {
        this.routes.set(path, {
            ...config,
            path: path,
            fullPath: config.path || path,
            id: this.generateRouteId(path)
        });
    }

    generateRouteId(path) {
        return path.replace(/[/\-\.]/g, '_').toLowerCase();
    }

    getRoute(path) {
        // 直接匹配
        if (this.routes.has(path)) {
            return this.routes.get(path);
        }
        
        // 模糊匹配
        return this.findRouteByPattern(path);
    }

    findRouteByPattern(path) {
        // 智能路径匹配算法
        const cleanPath = path.toLowerCase().replace(/[/\-_]/g, '');
        
        // AI模块匹配
        if (path.includes('/ai/') || cleanPath.includes('ai')) {
            if (cleanPath.includes('training')) {
                if (cleanPath.includes('federated')) return this.routes.get('/ai/federated-training');
                if (cleanPath.includes('local')) return this.routes.get('/ai/local-training');
                if (cleanPath.includes('mpc')) return this.routes.get('/ai/mpc-training');
                if (cleanPath.includes('select')) return this.routes.get('/federated-training-select');
                return this.routes.get('/ai/training');
            }
            if (cleanPath.includes('model')) return this.routes.get('/ai/models');
            if (cleanPath.includes('dataset')) return this.routes.get('/ai/datasets');
            if (cleanPath.includes('client')) return this.routes.get('/ai/client-dashboard');
            if (cleanPath.includes('server')) return this.routes.get('/ai/server-dashboard');
            return this.routes.get('/ai');
        }
        
        // 区块链模块匹配
        if (path.includes('/blockchain/') || cleanPath.includes('blockchain')) {
            if (cleanPath.includes('network')) return this.routes.get('/blockchain/network');
            if (cleanPath.includes('contract')) return this.routes.get('/blockchain/contracts');
            if (cleanPath.includes('transaction')) return this.routes.get('/blockchain/transactions');
            return this.routes.get('/blockchain');
        }
        
        // 密码学模块匹配
        if (path.includes('/crypto/') || cleanPath.includes('crypto')) {
            if (cleanPath.includes('key')) return this.routes.get('/crypto/keys');
            if (cleanPath.includes('encryption')) return this.routes.get('/crypto/encryption');
            if (cleanPath.includes('certificate')) return this.routes.get('/crypto/certificates');
            return this.routes.get('/crypto');
        }
        
        // 认证匹配
        if (cleanPath.includes('login')) return this.routes.get('/login');
        if (cleanPath.includes('usertype') || cleanPath.includes('user-type')) {
            return this.routes.get('/user-type-select');
        }
        
        // 默认返回主页
        return this.routes.get('/homepage');
    }

    // ====================== 导航功能 ======================
    navigate(path, params = {}, pushState = true, force = false) {
        // 防重复导航
        if (this.navigationInProgress && !force) {
            console.warn('Navigation already in progress, skipping...');
            return;
        }

        const route = this.getRoute(path);
        
        if (!route) {
            console.warn(`Route not found for path: ${path}`);
            this.navigate('/homepage', {}, pushState, true);
            return;
        }

        // 权限检查
        if (!this.canAccess(route)) {
            console.warn(`Access denied for route: ${path}`);
            this.handleAccessDenied(route);
            return;
        }

        // 设置导航状态
        this.navigationInProgress = true;

        // 添加到历史记录
        if (this.currentRoute && pushState) {
            this.addToHistory(this.currentRoute);
        }

        // 更新当前路由
        const previousRoute = this.currentRoute;
        this.currentRoute = route;

        // 构建完整URL
        const fullUrl = this.buildFullUrl(route, params);

        // 更新浏览器历史
        if (pushState && fullUrl !== window.location.href) {
            history.pushState(
                { route: route, params: params }, 
                route.title, 
                fullUrl
            );
        }

        // 更新页面状态
        this.updatePageState(route);

        // 执行导航
        this.performNavigation(route, fullUrl, params, previousRoute);
    }

    buildFullUrl(route, params) {
        let fullUrl = route.fullPath;
        if (Object.keys(params).length > 0) {
            const searchParams = new URLSearchParams(params);
            fullUrl += (fullUrl.includes('?') ? '&' : '?') + searchParams.toString();
        }
        
        // 确保版本号统一
        const version = '20250826';
        if (!fullUrl.includes('?v=')) {
            fullUrl += (fullUrl.includes('?') ? '&' : '?') + `v=${version}`;
        }
        
        return fullUrl;
    }

    handleAccessDenied(route) {
        if (route.requireAuth && !this.isAuthenticated()) {
            // 保存原始目标路由
            sessionStorage.setItem('redirect_after_login', route.path);
            this.navigate('/login', {}, true, true);
        } else if (route.userType && !this.hasPermission(route.userType)) {
            this.navigate('/user-type-select', { 
                error: 'insufficient_permissions',
                required: route.userType 
            }, true, true);
        } else {
            this.navigate('/homepage', {}, true, true);
        }
    }

    performNavigation(route, fullUrl, params = {}, previousRoute = null) {
        // 保存导航状态
        this.saveNavigationState(route, fullUrl, params);

        // 触发导航前事件
        this.dispatchNavigationEvent('beforeNavigate', route, previousRoute);

        // 显示加载状态
        this.showLoadingState(route);

        // 执行跳转
        this.loadingTimeout = setTimeout(() => {
            try {
                if (this.isCurrentPageNavigation(fullUrl)) {
                    this.handleSPANavigation(route, params, previousRoute);
                } else {
                    window.location.href = fullUrl;
                }
            } catch (error) {
                console.error('Navigation error:', error);
                this.handleNavigationError(error, route);
            }
        }, 200);
    }

    isCurrentPageNavigation(url) {
        const currentPage = window.location.pathname.split('/').pop();
        const targetPage = url.split('/').pop().split('?')[0].split('#')[0];
        return currentPage === targetPage;
    }

    handleSPANavigation(route, params, previousRoute) {
        // 处理单页应用内部导航
        this.dispatchNavigationEvent('routeChange', route, previousRoute, params);
        
        // 延迟移除加载状态，提供更好的用户体验
        setTimeout(() => {
            this.hideLoadingState();
            this.navigationInProgress = false;
            this.dispatchNavigationEvent('navigationComplete', route, previousRoute);
        }, 300);
    }

    handleNavigationError(error, route) {
        console.error('Navigation failed:', error);
        this.hideLoadingState();
        this.navigationInProgress = false;
        
        // 回退到安全路由
        this.navigate('/homepage', { 
            error: 'navigation_failed',
            original_route: route.path 
        }, true, true);
    }

    // ====================== 加载状态管理 ======================
    showLoadingState(route) {
        if (document.querySelector('#router-loading')) return;
        
        const loadingHTML = `
            <div id="router-loading" class="router-loading-overlay">
                <div class="router-loading-container">
                    <div class="router-loading-spinner"></div>
                    <p class="router-loading-text">正在跳转到 ${route?.title || '目标页面'}</p>
                    <div class="router-loading-progress">
                        <div class="router-loading-progress-bar"></div>
                    </div>
                    <small class="router-loading-hint">联邦学习平台</small>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', loadingHTML);
        this.injectLoadingStyles();
        this.animateLoadingProgress();
    }

    injectLoadingStyles() {
        if (document.querySelector('#router-loading-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'router-loading-styles';
        style.textContent = `
            .router-loading-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(255, 255, 255, 0.95);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                backdrop-filter: blur(2px);
                animation: fadeIn 0.2s ease-out;
            }
            
            .router-loading-container {
                text-align: center;
                max-width: 300px;
                padding: 2rem;
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(0, 0, 0, 0.05);
            }
            
            .router-loading-spinner {
                width: 40px;
                height: 40px;
                border: 3px solid #f3f4f6;
                border-top: 3px solid #3b82f6;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 1rem;
            }
            
            .router-loading-text {
                color: #374151;
                font-size: 14px;
                font-weight: 500;
                margin: 0 0 1rem;
                line-height: 1.4;
            }
            
            .router-loading-progress {
                width: 200px;
                height: 3px;
                background: #e5e7eb;
                border-radius: 9999px;
                margin: 0 auto 0.5rem;
                overflow: hidden;
            }
            
            .router-loading-progress-bar {
                height: 100%;
                background: linear-gradient(90deg, #3b82f6, #1d4ed8);
                border-radius: 9999px;
                width: 0%;
                transition: width 0.3s ease;
                animation: shimmer 1.5s infinite;
            }
            
            .router-loading-hint {
                color: #6b7280;
                font-size: 12px;
                margin: 0;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            @keyframes shimmer {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(400%); }
            }
            
            @media (prefers-reduced-motion: reduce) {
                .router-loading-spinner { animation: none; }
                .router-loading-progress-bar { animation: none; }
            }
        `;
        document.head.appendChild(style);
    }

    animateLoadingProgress() {
        const progressBar = document.querySelector('.router-loading-progress-bar');
        if (!progressBar) return;
        
        // 模拟加载进度
        setTimeout(() => progressBar.style.width = '30%', 100);
        setTimeout(() => progressBar.style.width = '60%', 200);
        setTimeout(() => progressBar.style.width = '85%', 350);
        setTimeout(() => progressBar.style.width = '100%', 500);
    }

    hideLoadingState() {
        const loading = document.querySelector('#router-loading');
        if (loading) {
            loading.style.opacity = '0';
            setTimeout(() => {
                loading.remove();
                // 清理加载超时
                if (this.loadingTimeout) {
                    clearTimeout(this.loadingTimeout);
                    this.loadingTimeout = null;
                }
            }, 200);
        }
    }

    // ====================== 状态管理 ======================
    updatePageState(route) {
        // 更新页面标题
        document.title = route.title;

        // 更新meta标签
        this.updateMetaTags(route);

        // 更新面包屑导航
        this.updateBreadcrumbs(route);

        // 更新页面类标识
        document.body.className = document.body.className
            .replace(/\broute-\w+/g, '')
            .replace(/\bmodule-\w+/g, '') + 
            ` route-${route.id} module-${route.module}`;
    }

    updateMetaTags(route) {
        // 更新description
        this.updateMetaTag('description', route.description);
        
        // 更新keywords
        if (route.keywords) {
            this.updateMetaTag('keywords', route.keywords);
        }
        
        // 更新Open Graph标签
        this.updateMetaTag('og:title', route.title, 'property');
        this.updateMetaTag('og:description', route.description, 'property');
        this.updateMetaTag('og:url', window.location.href, 'property');
    }

    updateMetaTag(name, content, attribute = 'name') {
        let meta = document.querySelector(`meta[${attribute}="${name}"]`);
        if (!meta) {
            meta = document.createElement('meta');
            meta.setAttribute(attribute, name);
            document.head.appendChild(meta);
        }
        meta.content = content;
    }

    updateBreadcrumbs(route) {
        const breadcrumbsContainer = document.querySelector('.breadcrumbs, [data-breadcrumbs]');
        if (!breadcrumbsContainer) return;

        const breadcrumbs = this.generateBreadcrumbs(route);
        breadcrumbsContainer.innerHTML = breadcrumbs.map(crumb => 
            `<span class="breadcrumb-item ${crumb.active ? 'active' : ''}" 
                   ${!crumb.active ? `data-path="${crumb.path}"` : ''}>
                ${crumb.name}
            </span>`
        ).join('<span class="breadcrumb-separator"> > </span>');

        // 绑定面包屑点击事件
        breadcrumbsContainer.addEventListener('click', (e) => {
            const item = e.target.closest('.breadcrumb-item');
            if (item && item.dataset.path) {
                this.navigate(item.dataset.path);
            }
        });
    }

    generateBreadcrumbs(route) {
        const breadcrumbs = [];
        
        // 添加主页
        if (route.path !== '/homepage') {
            breadcrumbs.push({ name: '主页', path: '/homepage' });
        }
        
        // 添加模块
        if (route.module !== 'homepage') {
            const moduleNames = {
                'ai': 'AI智能',
                'blockchain': '区块链',
                'crypto': '密钥加密',
                'auth': '用户认证'
            };
            breadcrumbs.push({ 
                name: moduleNames[route.module] || route.module, 
                path: `/${route.module}` 
            });
        }
        
        // 添加当前页面
        breadcrumbs.push({ 
            name: route.title.replace(/ - .*$/, ''), 
            path: route.path, 
            active: true 
        });
        
        return breadcrumbs;
    }

    // ====================== 事件系统 ======================
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

        // 监听键盘快捷键
        document.addEventListener('keydown', (event) => {
            this.handleKeyboardShortcuts(event);
        });
    }

    handlePopState(event) {
        if (event.state && event.state.route) {
            this.navigationInProgress = false; // 重置导航状态
            this.currentRoute = event.state.route;
            this.updatePageState(event.state.route);
            this.dispatchNavigationEvent('popstate', event.state.route, null, event.state.params || {});
        }
    }

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

    handleKeyboardShortcuts(event) {
        // Alt + H: 返回主页
        if (event.altKey && event.key === 'h') {
            event.preventDefault();
            this.navigate('/homepage');
        }
        
        // Alt + B: 后退
        if (event.altKey && event.key === 'b') {
            event.preventDefault();
            this.goBack();
        }
    }

    isInternalLink(href) {
        return href.startsWith('../') || 
               href.startsWith('../') || 
               href.includes('dashboard.html') ||
               href.includes('index.html') ||
               this.routes.has(href) ||
               href.startsWith('/ai/') ||
               href.startsWith('/blockchain/') ||
               href.startsWith('/crypto/');
    }

    dispatchNavigationEvent(type, route, previousRoute = null, params = {}) {
        const event = new CustomEvent(`router:${type}`, {
            detail: {
                type: type,
                route: route,
                previousRoute: previousRoute,
                params: params,
                timestamp: Date.now(),
                router: this
            }
        });
        window.dispatchEvent(event);

        // 向后兼容的事件名
        if (type === 'routeChange') {
            const legacyEvent = new CustomEvent('routeChange', {
                detail: {
                    route: route,
                    params: params,
                    timestamp: Date.now()
                }
            });
            window.dispatchEvent(legacyEvent);
        }
    }

    // ====================== 权限管理 ======================
    canAccess(route) {
        if (route.public) return true;
        if (route.requireAuth && !this.isAuthenticated()) return false;
        if (route.userType && !this.hasPermission(route.userType)) return false;
        return true;
    }

    isAuthenticated() {
        // 检查多种认证方式
        return localStorage.getItem('user_token') !== null || 
               sessionStorage.getItem('user_session') !== null ||
               localStorage.getItem('auth_token') !== null ||
               this.checkCookieAuth();
    }

    checkCookieAuth() {
        return document.cookie.includes('auth_token=') || 
               document.cookie.includes('session_id=');
    }

    hasPermission(requiredType) {
        const userData = this.getCurrentUser();
        if (!userData) return false;
        
        // 支持多种用户类型检查
        return userData.userType === requiredType ||
               userData.role === requiredType ||
               (userData.roles && userData.roles.includes(requiredType));
    }

    getCurrentUser() {
        try {
            const sources = [
                localStorage.getItem('user_data'),
                sessionStorage.getItem('user_data'),
                localStorage.getItem('current_user')
            ];
            
            for (const source of sources) {
                if (source) {
                    const userData = JSON.parse(source);
                    if (userData) return userData;
                }
            }
            
            return null;
        } catch (error) {
            console.warn('Failed to parse user data:', error);
            return null;
        }
    }

    // ====================== 历史管理 ======================
    addToHistory(route) {
        this.history.push({
            ...route,
            timestamp: Date.now(),
            url: window.location.href
        });

        // 限制历史记录长度
        if (this.history.length > this.maxHistoryLength) {
            this.history.shift();
        }
    }

    getHistory() {
        return [...this.history];
    }

    goBack() {
        if (this.history.length > 0) {
            const previousRoute = this.history.pop();
            this.navigate(previousRoute.path, {}, false);
        } else {
            history.back();
        }
    }

    goForward() {
        history.forward();
    }

    clearHistory() {
        this.history = [];
        sessionStorage.removeItem('router_state');
        sessionStorage.removeItem('navigation_state');
    }

    // ====================== 状态持久化 ======================
    saveState() {
        const state = {
            currentRoute: this.currentRoute,
            history: this.history.slice(-10), // 只保存最近10条
            timestamp: Date.now(),
            version: '1.0.0'
        };
        
        try {
            sessionStorage.setItem('router_state', JSON.stringify(state));
        } catch (error) {
            console.warn('Failed to save router state:', error);
        }
    }

    restoreState() {
        try {
            const state = sessionStorage.getItem('router_state');
            
            if (state) {
                const parsedState = JSON.parse(state);
                
                // 验证状态有效性（24小时内）
                if (Date.now() - parsedState.timestamp < 24 * 60 * 60 * 1000) {
                    if (parsedState.currentRoute) {
                        this.currentRoute = parsedState.currentRoute;
                    }
                    if (parsedState.history) {
                        this.history = parsedState.history;
                    }
                }
            }
        } catch (error) {
            console.warn('Failed to restore router state:', error);
        }
    }

    saveNavigationState(route, url, params) {
        const navigationState = {
            route: route,
            url: url,
            params: params,
            timestamp: Date.now(),
            userAgent: navigator.userAgent,
            referrer: document.referrer,
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            }
        };

        try {
            localStorage.setItem('navigation_state', JSON.stringify(navigationState));
            
            // 更新会话历史
            this.updateSessionHistory(route);
        } catch (error) {
            console.warn('Failed to save navigation state:', error);
        }
    }

    updateSessionHistory(route) {
        try {
            const sessionHistory = JSON.parse(localStorage.getItem('session_history') || '[]');
            sessionHistory.push({
                module: route.module,
                title: route.title,
                path: route.path,
                timestamp: Date.now()
            });

            // 限制历史记录长度
            if (sessionHistory.length > 50) {
                sessionHistory.splice(0, sessionHistory.length - 50);
            }

            localStorage.setItem('session_history', JSON.stringify(sessionHistory));
        } catch (error) {
            console.warn('Failed to update session history:', error);
        }
    }

    // ====================== 初始化和模块管理 ======================
    handleInitialRoute() {
        this.restoreState();
        
        const currentPath = window.location.pathname;
        const route = this.findRouteByPattern(currentPath);
        
        if (route) {
            this.currentRoute = route;
            this.updatePageState(route);
            
            // 检查登录后重定向
            const redirectPath = sessionStorage.getItem('redirect_after_login');
            if (redirectPath && this.isAuthenticated()) {
                sessionStorage.removeItem('redirect_after_login');
                setTimeout(() => this.navigate(redirectPath), 1000);
            }
        }
    }

    initializeModules() {
        // 只对当前页面相关的模块进行初始化，避免404错误
        // 预加载关键模块已禁用，以避免P2PAI项目中不存在的路径产生404错误
        
        // 初始化模块特定功能
        this.initializeModuleSpecificFeatures();
    }

    initializeModuleSpecificFeatures() {
        // 根据当前模块初始化特定功能
        if (this.currentRoute) {
            switch (this.currentRoute.module) {
                case 'ai':
                    this.initializeAIFeatures();
                    break;
                case 'blockchain':
                    this.initializeBlockchainFeatures();
                    break;
                case 'crypto':
                    this.initializeCryptoFeatures();
                    break;
            }
        }
    }

    initializeAIFeatures() {
        // AI模块特定初始化
        this.preloadModule('ai');
    }

    initializeBlockchainFeatures() {
        // 区块链模块特定初始化
        this.preloadModule('blockchain');
    }

    initializeCryptoFeatures() {
        // 密码学模块特定初始化
        this.preloadModule('crypto');
    }

    // ====================== 公共 API ======================
    getCurrentRoute() {
        return this.currentRoute;
    }

    getCurrentModule() {
        return this.currentRoute ? this.currentRoute.module : 'homepage';
    }

    buildUrl(path, params = {}) {
        const route = this.getRoute(path);
        if (!route) return path;

        return this.buildFullUrl(route, params);
    }

    getAccessibleRoutes() {
        const accessibleRoutes = [];
        
        for (const [path, route] of this.routes.entries()) {
            if (this.canAccess(route)) {
                accessibleRoutes.push({
                    path: path,
                    ...route
                });
            }
        }

        return accessibleRoutes.sort((a, b) => {
            // 按模块和标题排序
            if (a.module !== b.module) {
                return a.module.localeCompare(b.module);
            }
            return a.title.localeCompare(b.title);
        });
    }

    getModuleRoutes(moduleName) {
        const moduleRoutes = [];
        for (const [path, route] of this.routes.entries()) {
            if (route.module === moduleName && this.canAccess(route)) {
                moduleRoutes.push({ path, ...route });
            }
        }
        return moduleRoutes;
    }

    preloadModule(moduleName) {
        const route = this.routes.get(`/${moduleName}`);
        if (route) {
            const link = document.createElement('link');
            link.rel = 'prefetch';
            link.href = route.fullPath;
            document.head.appendChild(link);
        }
    }

    // ====================== 工具方法 ======================
    refresh() {
        if (this.currentRoute) {
            this.navigate(this.currentRoute.path, {}, false, true);
        } else {
            window.location.reload();
        }
    }

    reset() {
        this.clearHistory();
        this.currentRoute = null;
        this.navigationInProgress = false;
        this.navigate('/homepage');
    }

    getRouteInfo(path) {
        const route = this.getRoute(path);
        if (!route) return null;

        return {
            ...route,
            accessible: this.canAccess(route),
            breadcrumbs: this.generateBreadcrumbs(route)
        };
    }

    validateRoute(path) {
        const route = this.getRoute(path);
        return {
            exists: !!route,
            accessible: route ? this.canAccess(route) : false,
            route: route
        };
    }
}

// ====================== 全局初始化 ======================
let globalUnifiedRouter;

// 页面加载时初始化
if (typeof window !== 'undefined') {
    const initRouter = () => {
        if (!globalUnifiedRouter) {
            globalUnifiedRouter = new UnifiedRouter();
            
            // 导出到全局
            window.UnifiedRouter = UnifiedRouter;
            window.globalRouter = globalUnifiedRouter;
            
            // 向后兼容
            window.router = globalUnifiedRouter;
            window.FedRouter = UnifiedRouter;
            
            console.log('Unified Router initialized successfully');
        }
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initRouter);
    } else {
        initRouter();
    }
}

// ====================== 全局便捷函数 ======================
if (typeof window !== 'undefined') {
    // 导航函数
    window.navigateTo = function(path, params = {}) {
        if (globalUnifiedRouter) {
            globalUnifiedRouter.navigate(path, params);
        } else {
            console.warn('Router not initialized');
        }
    };

    // URL构建函数
    window.buildUrl = function(path, params = {}) {
        if (globalUnifiedRouter) {
            return globalUnifiedRouter.buildUrl(path, params);
        }
        return path;
    };

    // 返回函数
    window.goBack = function() {
        if (globalUnifiedRouter) {
            globalUnifiedRouter.goBack();
        } else {
            history.back();
        }
    };

    // 智能路径计算函数
    function calculateRelativePath(currentPath, targetPath) {
        // 移除开头的斜杠
        currentPath = currentPath.replace(/^\/+/, '');
        targetPath = targetPath.replace(/^\/+/, '');
        
        // 计算当前页面相对于frontend根目录的深度
        const currentParts = currentPath.split('/').filter(part => part);
        let depth = 0;
        
        // 确定深度
        if (currentParts.includes('pages')) {
            // 在子目录的pages文件夹中，需要返回2级 (pages -> module -> frontend)
            const pagesIndex = currentParts.indexOf('pages');
            depth = pagesIndex + 1; // +1是因为还要跳出pages目录
        } else if (currentParts.length > 1) {
            // 在子目录中，但特殊处理homepage目录
            if (currentParts[0] === 'homepage') {
                depth = 1; // homepage目录只需返回1级
            } else {
                depth = currentParts.length - 1;
            }
        }
        
        // 构建相对路径
        let relativePath = '';
        for (let i = 0; i < depth; i++) {
            relativePath += '../';
        }
        relativePath += targetPath;
        
        return relativePath;
    }

    // 全局导航函数
    function smartNavigate(targetPath) {
        const currentPath = window.location.pathname;
        const relativePath = calculateRelativePath(currentPath, targetPath);
        
        console.log('Smart Navigate:', {
            from: currentPath,
            to: targetPath,
            calculated: relativePath
        });
        
        window.location.href = relativePath;
    }

    // 返回主页函数
    window.goHome = function() {
        if (globalUnifiedRouter) {
            globalUnifiedRouter.navigate('/homepage');
        } else {
            smartNavigate('homepage/index.html');
        }
    };

    // 模块导航函数
    window.goToAI = function() {
        if (globalUnifiedRouter) {
            globalUnifiedRouter.navigate('/ai');
        } else {
            smartNavigate('ai/pages/user-type-select.html');
        }
    };

    window.goToBlockchain = function() {
        if (globalUnifiedRouter) {
            globalUnifiedRouter.navigate('/blockchain');
        } else {
            smartNavigate('blockchain/pages/login.html');
        }
    };

    window.goToCrypto = function() {
        if (globalUnifiedRouter) {
            globalUnifiedRouter.navigate('/crypto');
        } else {
            smartNavigate('crypto/pages/login.html');
        }
    };

    // 创建通用导航函数
    window.navigateToPage = function(moduleName, pageName) {
        const targetPath = `${moduleName}/pages/${pageName}.html`;
        if (globalUnifiedRouter) {
            globalUnifiedRouter.navigate(`/${moduleName}/${pageName}`);
        } else {
            smartNavigate(targetPath);
        }
    };

    // 获取当前路由信息
    window.getCurrentRoute = function() {
        return globalUnifiedRouter ? globalUnifiedRouter.getCurrentRoute() : null;
    };

    // 获取当前模块
    window.getCurrentModule = function() {
        return globalUnifiedRouter ? globalUnifiedRouter.getCurrentModule() : 'homepage';
    };

    // 路由验证
    window.validateRoute = function(path) {
        return globalUnifiedRouter ? globalUnifiedRouter.validateRoute(path) : { exists: false };
    };
}

// ====================== 模块化支持 ======================
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UnifiedRouter;
}

// ====================== AMD支持 ======================
if (typeof define === 'function' && define.amd) {
    define('unified-router', [], function() {
        return UnifiedRouter;
    });
}

// ====================== 调试工具 ======================
if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
    window.routerDebug = {
        getRouter: () => globalUnifiedRouter,
        getRoutes: () => globalUnifiedRouter ? Array.from(globalUnifiedRouter.routes.entries()) : [],
        getCurrentRoute: () => globalUnifiedRouter ? globalUnifiedRouter.getCurrentRoute() : null,
        getHistory: () => globalUnifiedRouter ? globalUnifiedRouter.getHistory() : [],
        testRoute: (path) => globalUnifiedRouter ? globalUnifiedRouter.validateRoute(path) : null
    };
}