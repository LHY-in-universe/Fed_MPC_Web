/**
 * 模块间导航和路由系统
 * 提供统一的导航组件和路由管理
 */

class NavigationSystem {
    constructor() {
        this.currentModule = this.detectCurrentModule();
        this.init();
    }

    /**
     * 检测当前模块
     */
    detectCurrentModule() {
        const path = window.location.pathname;
        if (path.includes('/ai/')) return 'ai';
        if (path.includes('/blockchain/')) return 'blockchain';
        if (path.includes('/crypto/')) return 'crypto';
        if (path.includes('/homepage/')) return 'homepage';
        return 'homepage';
    }

    /**
     * 初始化导航系统
     */
    init() {
        this.createNavigationBar();
        this.setupRouting();
        this.highlightCurrentModule();
    }

    /**
     * 创建顶部导航栏
     */
    createNavigationBar() {
        const existingNav = document.querySelector('#main-navigation');
        if (existingNav) {
            existingNav.remove();
        }

        const navHTML = `
            <nav id="main-navigation" class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div class="flex justify-between items-center h-16">
                        <!-- Logo -->
                        <div class="flex-shrink-0 flex items-center">
                            <a href="/frontend/homepage/index.html" class="text-xl font-bold text-gray-900">
                                联邦学习平台
                            </a>
                        </div>

                        <!-- 主导航 -->
                        <div class="hidden md:block">
                            <div class="ml-10 flex items-baseline space-x-4">
                                <a href="/frontend/homepage/index.html" 
                                   data-module="homepage"
                                   class="nav-link px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200">
                                    主页
                                </a>
                                <a href="/frontend/ai/pages/dashboard.html" 
                                   data-module="ai"
                                   class="nav-link px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200">
                                    AI智能
                                </a>
                                <a href="/frontend/blockchain/pages/dashboard.html" 
                                   data-module="blockchain"
                                   class="nav-link px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200">
                                    区块链
                                </a>
                                <a href="/frontend/crypto/pages/crypto-dashboard.html" 
                                   data-module="crypto"
                                   class="nav-link px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200">
                                    密钥加密
                                </a>
                            </div>
                        </div>

                        <!-- 移动端菜单按钮 -->
                        <div class="md:hidden">
                            <button id="mobile-menu-button" class="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100">
                                <svg class="h-6 w-6" stroke="currentColor" fill="none" viewBox="0 0 24 24">
                                    <path class="inline" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- 移动端菜单 -->
                <div id="mobile-menu" class="md:hidden hidden">
                    <div class="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-gray-50">
                        <a href="/frontend/homepage/index.html" 
                           data-module="homepage"
                           class="nav-link-mobile block px-3 py-2 rounded-md text-base font-medium transition-colors duration-200">
                            主页
                        </a>
                        <a href="/frontend/ai/pages/dashboard.html" 
                           data-module="ai"
                           class="nav-link-mobile block px-3 py-2 rounded-md text-base font-medium transition-colors duration-200">
                            AI智能
                        </a>
                        <a href="/frontend/blockchain/pages/dashboard.html" 
                           data-module="blockchain"
                           class="nav-link-mobile block px-3 py-2 rounded-md text-base font-medium transition-colors duration-200">
                            区块链
                        </a>
                        <a href="/frontend/crypto/pages/crypto-dashboard.html" 
                           data-module="crypto"
                           class="nav-link-mobile block px-3 py-2 rounded-md text-base font-medium transition-colors duration-200">
                            密钥加密
                        </a>
                    </div>
                </div>
            </nav>
        `;

        // 插入导航栏到页面顶部
        document.body.insertAdjacentHTML('afterbegin', navHTML);
        
        // 绑定移动端菜单切换事件
        this.setupMobileMenu();
    }

    /**
     * 设置移动端菜单
     */
    setupMobileMenu() {
        const mobileMenuButton = document.getElementById('mobile-menu-button');
        const mobileMenu = document.getElementById('mobile-menu');
        
        if (mobileMenuButton && mobileMenu) {
            mobileMenuButton.addEventListener('click', () => {
                mobileMenu.classList.toggle('hidden');
            });
        }
    }

    /**
     * 高亮当前模块
     */
    highlightCurrentModule() {
        // 移除所有高亮
        document.querySelectorAll('.nav-link, .nav-link-mobile').forEach(link => {
            link.classList.remove('bg-gray-900', 'text-white', 'bg-gray-100', 'text-gray-900');
            link.classList.add('text-gray-600', 'hover:text-gray-900', 'hover:bg-gray-100');
        });

        // 高亮当前模块
        const currentLinks = document.querySelectorAll(`[data-module="${this.currentModule}"]`);
        currentLinks.forEach(link => {
            link.classList.remove('text-gray-600', 'hover:text-gray-900', 'hover:bg-gray-100');
            link.classList.add('bg-gray-900', 'text-white');
        });
    }

    /**
     * 设置路由系统
     */
    setupRouting() {
        // 监听页面加载完成
        document.addEventListener('DOMContentLoaded', () => {
            this.initPageSpecificFeatures();
        });

        // 监听导航点击
        document.addEventListener('click', (e) => {
            const navLink = e.target.closest('.nav-link, .nav-link-mobile');
            if (navLink) {
                this.handleNavigation(navLink);
            }
        });
    }

    /**
     * 处理导航跳转
     */
    handleNavigation(link) {
        const module = link.getAttribute('data-module');
        const href = link.getAttribute('href');
        
        // 保存跳转信息到localStorage
        FedUtils.storage.set('navigation_history', {
            from: this.currentModule,
            to: module,
            timestamp: Date.now()
        });

        // 显示加载状态
        this.showNavigationLoading();
    }

    /**
     * 显示导航加载状态
     */
    showNavigationLoading() {
        const loadingHTML = `
            <div id="navigation-loading" class="fixed inset-0 bg-white bg-opacity-75 flex items-center justify-center z-50">
                <div class="text-center">
                    <div class="loading-spinner mx-auto mb-4"></div>
                    <p class="text-gray-600">正在加载模块...</p>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', loadingHTML);
        
        // 2秒后自动移除加载状态
        setTimeout(() => {
            const loading = document.getElementById('navigation-loading');
            if (loading) loading.remove();
        }, 2000);
    }

    /**
     * 初始化页面特定功能
     */
    initPageSpecificFeatures() {
        // 根据当前模块初始化特定功能
        switch (this.currentModule) {
            case 'ai':
                this.initAIFeatures();
                break;
            case 'blockchain':
                this.initBlockchainFeatures();
                break;
            case 'crypto':
                this.initCryptoFeatures();
                break;
            case 'homepage':
                this.initHomepageFeatures();
                break;
        }
    }

    /**
     * 初始化AI模块功能
     */
    initAIFeatures() {
        console.log('Initializing AI module features');
        // 可以在这里添加AI模块特定的初始化逻辑
    }

    /**
     * 初始化区块链模块功能
     */
    initBlockchainFeatures() {
        console.log('Initializing Blockchain module features');
        // 可以在这里添加区块链模块特定的初始化逻辑
    }

    /**
     * 初始化密钥加密模块功能
     */
    initCryptoFeatures() {
        console.log('Initializing Crypto module features');
        // 可以在这里添加密钥加密模块特定的初始化逻辑
    }

    /**
     * 初始化主页模块功能
     */
    initHomepageFeatures() {
        console.log('Initializing Homepage module features');
        // 可以在这里添加主页模块特定的初始化逻辑
    }

    /**
     * 获取面包屑导航
     */
    getBreadcrumb() {
        const breadcrumbMap = {
            'homepage': '主页',
            'ai': '主页 > AI智能',
            'blockchain': '主页 > 区块链',
            'crypto': '主页 > 密钥加密'
        };
        
        return breadcrumbMap[this.currentModule] || '主页';
    }

    /**
     * 创建面包屑导航
     */
    createBreadcrumb() {
        const breadcrumb = this.getBreadcrumb();
        const breadcrumbHTML = `
            <nav class="bg-gray-50 px-4 py-3" aria-label="Breadcrumb">
                <div class="max-w-7xl mx-auto">
                    <div class="flex items-center space-x-2 text-sm text-gray-600">
                        ${breadcrumb.split(' > ').map((item, index, array) => {
                            if (index === array.length - 1) {
                                return `<span class="font-medium text-gray-900">${item}</span>`;
                            } else {
                                return `<span>${item}</span><svg class="w-4 h-4 mx-2" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path></svg>`;
                            }
                        }).join('')}
                    </div>
                </div>
            </nav>
        `;

        const navigation = document.querySelector('#main-navigation');
        if (navigation) {
            navigation.insertAdjacentHTML('afterend', breadcrumbHTML);
        }
    }
}

// 全局导航系统实例
let globalNavigation;

// 页面加载时初始化导航系统
document.addEventListener('DOMContentLoaded', () => {
    globalNavigation = new NavigationSystem();
    
    // 如果不是主页，创建面包屑导航
    if (globalNavigation.currentModule !== 'homepage') {
        globalNavigation.createBreadcrumb();
    }
});

// 导出到全局
if (typeof window !== 'undefined') {
    window.NavigationSystem = NavigationSystem;
    window.globalNavigation = globalNavigation;
}