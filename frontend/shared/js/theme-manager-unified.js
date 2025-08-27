/**
 * 统一主题管理器 - 完整整合版
 * 整合所有主题管理功能，包含：
 * - 主题切换和状态管理
 * - 动画效果和过渡处理
 * - 跨浏览器兼容性
 * - 系统偏好检测
 * - 事件系统和API接口
 * - 向后兼容性支持
 * - 调试和开发工具
 */

class UnifiedThemeManager {
    constructor() {
        this.theme = this.getStoredTheme() || this.getSystemTheme();
        this.isTransitioning = false;
        this.animationDuration = 300;
        
        // 检测浏览器特性
        this.detectBrowserFeatures();
        
        // 初始化
        this.initializeTheme();
        this.setupEventListeners();
        this.setupAnimationContainer();
        
        // 添加CSS样式（如果不存在）
        this.injectRequiredStyles();
    }

    // ====================== 浏览器特性检测 ======================
    detectBrowserFeatures() {
        this.supportsViewTransition = 'startViewTransition' in document;
        this.supportsColorScheme = CSS.supports('color-scheme', 'dark light');
        this.supportsMask = CSS.supports('mask: radial-gradient(circle, black, transparent)') || 
                           CSS.supports('-webkit-mask: radial-gradient(circle, black, transparent)');
        this.supportsAnimations = window.getComputedStyle(document.body).animationName !== undefined;
        
        // 检测浏览器类型
        this.isFirefox = navigator.userAgent.toLowerCase().indexOf('firefox') > -1;
        this.isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
        this.isChrome = /Chrome/.test(navigator.userAgent) && /Google Inc/.test(navigator.vendor);
        this.isEdge = /Edg/.test(navigator.userAgent);
        
        // 检测用户偏好
        this.prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        
        if (this.prefersReducedMotion) {
            this.animationDuration = 100;
        }
        
        // 添加浏览器特定的类名
        document.documentElement.classList.add(
            this.isFirefox ? 'is-firefox' :
            this.isSafari ? 'is-safari' :
            this.isChrome ? 'is-chrome' :
            this.isEdge ? 'is-edge' : 'is-unknown'
        );
    }

    // ====================== 主题管理核心功能 ======================
    getStoredTheme() {
        return localStorage.getItem('theme');
    }

    getSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }

    initializeTheme() {
        // 设置 data-theme 属性
        document.documentElement.setAttribute('data-theme', this.theme);
        
        // 设置 color-scheme 属性（支持的浏览器）
        if (this.supportsColorScheme) {
            document.documentElement.style.colorScheme = this.theme;
        }
        
        // 添加主题类
        document.documentElement.classList.remove('theme-light', 'theme-dark');
        document.documentElement.classList.add(`theme-${this.theme}`);
        
        // 更新图标
        this.updateThemeToggleIcon();
        
        // 触发主题初始化事件
        this.dispatchThemeEvent('themeInitialized');
        
        // 开发调试信息
        if (this.isDevelopmentMode()) {
            console.log(`[ThemeManager] Initialized with ${this.theme} theme`);
        }
    }

    toggleTheme(buttonElement = null) {
        const newTheme = this.theme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme, buttonElement);
    }

    async setTheme(newTheme, buttonElement = null) {
        if (newTheme === this.theme || this.isTransitioning) return;

        const oldTheme = this.theme;
        this.isTransitioning = true;
        
        // 触发主题切换开始事件
        this.dispatchThemeEvent('themeChanging', { 
            oldTheme, 
            newTheme,
            hasAnimation: !!buttonElement && this.supportsAnimations && !this.prefersReducedMotion
        });
        
        try {
            // 如果提供了按钮元素且支持动画，使用动画切换
            if (buttonElement && this.supportsAnimations && !this.prefersReducedMotion) {
                await this.animatedThemeSwitch(newTheme, oldTheme, buttonElement);
            } else {
                // 降级到普通切换
                this.theme = newTheme;
                this.createThemeTransition(() => {
                    this.applyTheme(newTheme, oldTheme);
                });
            }
        } catch (error) {
            console.warn('[ThemeManager] Theme switching error:', error);
            // 确保主题切换完成
            this.theme = newTheme;
            this.applyTheme(newTheme, oldTheme);
        } finally {
            this.isTransitioning = false;
        }
    }

    applyTheme(newTheme, oldTheme) {
        // 更新 DOM 属性
        document.documentElement.setAttribute('data-theme', newTheme);
        
        if (this.supportsColorScheme) {
            document.documentElement.style.colorScheme = newTheme;
        }
        
        // 更新类名
        document.documentElement.classList.remove(`theme-${oldTheme}`);
        document.documentElement.classList.add(`theme-${newTheme}`);
        
        // 存储到 localStorage
        localStorage.setItem('theme', newTheme);
        
        // 更新图标
        this.updateThemeToggleIcon();
        
        // 强制重绘以修复某些浏览器的渲染问题
        this.forceRepaint();
        
        // 触发主题变更完成事件
        this.dispatchThemeEvent('themeChanged', { 
            oldTheme, 
            newTheme, 
            browser: this.getBrowserInfo() 
        });

        // 开发调试信息
        if (this.isDevelopmentMode()) {
            console.log(`[ThemeManager] Theme changed: ${oldTheme} → ${newTheme}`);
        }
    }

    // ====================== 动画系统 ======================
    setupAnimationContainer() {
        if (document.querySelector('.theme-animation-overlay')) return;
        
        const overlay = document.createElement('div');
        overlay.className = 'theme-animation-overlay';
        overlay.setAttribute('aria-hidden', 'true');
        document.body.appendChild(overlay);
        
        this.animationContainer = overlay;
    }

    async animatedThemeSwitch(newTheme, oldTheme, buttonElement) {
        const success = await this.executeThemeAnimation(
            buttonElement,
            oldTheme,
            newTheme,
            () => {
                this.theme = newTheme;
                this.applyTheme(newTheme, oldTheme);
            }
        );
        
        if (!success) {
            // 动画失败，使用普通切换
            this.theme = newTheme;
            this.applyTheme(newTheme, oldTheme);
        }
    }

    async executeThemeAnimation(button, fromTheme, toTheme, themeChangeCallback) {
        try {
            // 按钮点击动画
            this.animateButton(button);
            
            // 选择最佳动画方案
            let animationPromise;
            
            if (this.supportsViewTransition && !this.prefersReducedMotion && !this.isFirefox) {
                // 使用 View Transition API（现代浏览器，排除Firefox）
                animationPromise = this.createViewTransitionAnimation(themeChangeCallback);
            } else if (this.supportsMask && !this.prefersReducedMotion) {
                // 使用遮罩动画（支持的浏览器）
                animationPromise = this.createMaskTransition(fromTheme, toTheme, themeChangeCallback);
            } else {
                // 使用标准淡化效果
                animationPromise = this.createSimpleFade(themeChangeCallback);
            }
            
            await animationPromise;
            return true;
            
        } catch (error) {
            console.warn('[ThemeManager] Animation failed:', error);
            return false;
        }
    }

    createViewTransitionAnimation(themeChangeCallback) {
        if (!this.supportsViewTransition) {
            return Promise.resolve();
        }

        return document.startViewTransition(() => {
            themeChangeCallback();
        }).finished.catch(() => {
            // View Transition失败时的降级处理
            console.warn('[ThemeManager] View Transition failed, falling back to simple transition');
        });
    }

    createMaskTransition(fromTheme, toTheme, themeChangeCallback) {
        return new Promise((resolve) => {
            const curtain = document.createElement('div');
            curtain.className = `theme-curtain ${fromTheme}-to-${toTheme}`;
            
            this.animationContainer.appendChild(curtain);
            
            // 开始动画
            curtain.style.animation = `curtainOpen ${this.animationDuration}ms ease-in-out`;
            
            // 在动画中点切换主题
            setTimeout(() => {
                themeChangeCallback();
            }, this.animationDuration / 2);
            
            // 结束动画
            setTimeout(() => {
                curtain.style.animation = `curtainClose ${this.animationDuration}ms ease-in-out`;
                
                setTimeout(() => {
                    if (curtain.parentNode) {
                        curtain.parentNode.removeChild(curtain);
                    }
                    resolve();
                }, this.animationDuration);
            }, this.animationDuration);
        });
    }

    createSimpleFade(themeChangeCallback) {
        return new Promise((resolve) => {
            document.body.classList.add('theme-fade-transition', 'switching');
            
            setTimeout(() => {
                themeChangeCallback();
                document.body.classList.remove('switching');
            }, this.animationDuration / 2);
            
            setTimeout(() => {
                document.body.classList.remove('theme-fade-transition');
                resolve();
            }, this.animationDuration);
        });
    }

    animateButton(button) {
        if (!this.supportsAnimations) return;
        
        button.classList.add('switching');
        
        // 创建材料设计风格的涟漪效果
        if (button.getBoundingClientRect().width > 0) {
            this.createMaterialRipple(button);
        }
        
        setTimeout(() => {
            button.classList.remove('switching');
        }, 600);
    }

    createMaterialRipple(button) {
        const rect = button.getBoundingClientRect();
        const ripple = document.createElement('div');
        const size = Math.max(rect.width, rect.height) * 2;
        const pos = {
            x: rect.width / 2 - size / 2,
            y: rect.height / 2 - size / 2
        };
        
        ripple.className = 'theme-ripple-material';
        ripple.style.cssText = `
            width: ${size}px;
            height: ${size}px;
            left: ${pos.x}px;
            top: ${pos.y}px;
        `;
        
        // 确保按钮有正确的样式
        const originalPosition = button.style.position;
        const originalOverflow = button.style.overflow;
        
        button.style.position = button.style.position || 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);
        
        setTimeout(() => {
            if (ripple.parentNode) {
                ripple.parentNode.removeChild(ripple);
            }
            // 恢复原始样式
            if (originalPosition) {
                button.style.position = originalPosition;
            }
            if (originalOverflow) {
                button.style.overflow = originalOverflow;
            }
        }, 600);
    }

    // ====================== 过渡效果 ======================
    createThemeTransition(callback) {
        // 添加过渡类
        document.documentElement.classList.add('theme-transitioning');
        
        if (this.supportsViewTransition && !this.isFirefox) {
            // 使用 View Transition API（现代浏览器）
            document.startViewTransition(() => {
                callback();
            }).finished.finally(() => {
                this.cleanupTransition();
            }).catch(() => {
                // 降级处理
                this.createFallbackTransition(callback);
            });
        } else {
            // 降级处理：普通过渡
            this.createFallbackTransition(callback);
        }
    }

    createFallbackTransition(callback) {
        const duration = this.isFirefox ? 200 : this.animationDuration;
        
        // 应用新主题
        callback();
        
        // 清理过渡
        setTimeout(() => {
            this.cleanupTransition();
        }, duration);
    }

    cleanupTransition() {
        document.documentElement.classList.remove('theme-transitioning');
    }

    forceRepaint() {
        // 在某些浏览器中强制重绘以修复渲染问题
        if (this.isSafari || this.isFirefox) {
            const body = document.body;
            const display = body.style.display;
            body.style.display = 'none';
            body.offsetHeight; // 触发重排
            body.style.display = display;
        }
    }

    // ====================== UI 更新 ======================
    updateThemeToggleIcon() {
        const toggleButtons = document.querySelectorAll('.theme-toggle');
        toggleButtons.forEach(button => {
            const iconElement = button.querySelector('i, span, [data-theme-icon]');
            if (iconElement) {
                if (this.theme === 'dark') {
                    iconElement.innerHTML = '☀️'; // 浅色模式图标
                    iconElement.setAttribute('title', 'Switch to Light Mode');
                    button.setAttribute('aria-label', 'Switch to Light Mode');
                } else {
                    iconElement.innerHTML = '🌙'; // 深色模式图标  
                    iconElement.setAttribute('title', 'Switch to Dark Mode');
                    button.setAttribute('aria-label', 'Switch to Dark Mode');
                }
            }
        });
    }

    // ====================== 事件系统 ======================
    setupEventListeners() {
        // 监听系统主题变化
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            
            const handleSystemThemeChange = (e) => {
                if (!this.getStoredTheme()) {
                    const systemTheme = e.matches ? 'dark' : 'light';
                    this.setTheme(systemTheme);
                }
            };
            
            if (mediaQuery.addEventListener) {
                mediaQuery.addEventListener('change', handleSystemThemeChange);
            } else {
                mediaQuery.addListener(handleSystemThemeChange);
            }
        }

        // 主题切换按钮点击事件
        document.addEventListener('click', (e) => {
            const toggleButton = e.target.closest('.theme-toggle');
            if (toggleButton && !toggleButton.disabled) {
                e.preventDefault();
                e.stopPropagation();
                this.toggleTheme(toggleButton);
            }
        });

        // 键盘快捷键支持
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'D') {
                e.preventDefault();
                this.toggleTheme();
            }
        });

        // 监听动画偏好变化
        if (window.matchMedia) {
            const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
            const handleMotionChange = (e) => {
                this.prefersReducedMotion = e.matches;
                this.animationDuration = e.matches ? 100 : 300;
            };
            
            if (motionQuery.addEventListener) {
                motionQuery.addEventListener('change', handleMotionChange);
            } else {
                motionQuery.addListener(handleMotionChange);
            }
        }
    }

    dispatchThemeEvent(eventName, detail = {}) {
        const event = new CustomEvent(eventName, {
            detail: {
                theme: this.theme,
                timestamp: new Date().toISOString(),
                manager: 'UnifiedThemeManager',
                ...detail
            }
        });
        
        // 同时触发窗口和文档事件，确保兼容性
        window.dispatchEvent(event);
        document.dispatchEvent(event);
    }

    // ====================== 公共 API ======================
    getCurrentTheme() {
        return this.theme;
    }

    isDarkMode() {
        return this.theme === 'dark';
    }

    isLightMode() {
        return this.theme === 'light';
    }

    getBrowserInfo() {
        return {
            isFirefox: this.isFirefox,
            isSafari: this.isSafari,
            isChrome: this.isChrome,
            isEdge: this.isEdge,
            supportsViewTransition: this.supportsViewTransition,
            supportsColorScheme: this.supportsColorScheme,
            supportsMask: this.supportsMask,
            supportsAnimations: this.supportsAnimations,
            prefersReducedMotion: this.prefersReducedMotion,
            userAgent: navigator.userAgent
        };
    }

    resetToSystemTheme() {
        localStorage.removeItem('theme');
        const systemTheme = this.getSystemTheme();
        this.setTheme(systemTheme);
    }

    updateSettings(options = {}) {
        if (options.duration !== undefined) {
            this.animationDuration = Math.max(100, Math.min(2000, options.duration));
        }
        
        if (options.respectReducedMotion !== undefined && options.respectReducedMotion) {
            this.prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            if (this.prefersReducedMotion) {
                this.animationDuration = 100;
            }
        }
    }

    // 获取所有可用主题
    getAvailableThemes() {
        return ['light', 'dark'];
    }

    // 检查特定主题是否可用
    isThemeAvailable(themeName) {
        return this.getAvailableThemes().includes(themeName);
    }

    // ====================== 调试功能 ======================
    isDevelopmentMode() {
        return window.location.hostname === 'localhost' || 
               window.location.hostname === '127.0.0.1' || 
               window.location.search.includes('debug=true');
    }

    setDebugMode(enabled) {
        if (enabled) {
            document.documentElement.classList.add('theme-debug');
            console.log('%c[ThemeManager] Debug Mode: Enabled', 'color: #00ff00; font-weight: bold;');
            console.log('Current Theme:', this.theme);
            console.log('Browser Features:', this.getBrowserInfo());
            console.log('Animation Duration:', this.animationDuration + 'ms');
            console.log('Prefers Reduced Motion:', this.prefersReducedMotion);
        } else {
            document.documentElement.classList.remove('theme-debug');
            console.log('%c[ThemeManager] Debug Mode: Disabled', 'color: #ff0000; font-weight: bold;');
        }
    }

    // 性能监控
    getPerformanceInfo() {
        return {
            theme: this.theme,
            isTransitioning: this.isTransitioning,
            animationDuration: this.animationDuration,
            totalThemeToggles: this.totalToggles || 0,
            lastToggleTime: this.lastToggleTime || null,
            averageToggleTime: this.averageToggleTime || 0
        };
    }

    // ====================== 样式注入 ======================
    injectRequiredStyles() {
        if (document.querySelector('#unified-theme-animations-css')) return;
        
        const style = document.createElement('style');
        style.id = 'unified-theme-animations-css';
        style.textContent = `
            /* Material Ripple Animation */
            @keyframes materialRipple {
                0% { transform: scale(0); opacity: 0.3; }
                100% { transform: scale(1); opacity: 0; }
            }
            
            .theme-ripple-material {
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.3);
                transform: scale(0);
                animation: materialRipple 0.6s cubic-bezier(0.4, 0, 0.2, 1);
                pointer-events: none;
                z-index: 1;
            }
            
            [data-theme="dark"] .theme-ripple-material {
                background: rgba(0, 0, 0, 0.2);
            }
            
            /* Fade Transition */
            .theme-fade-transition {
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            .theme-fade-transition.switching {
                opacity: 0.85;
                transform: scale(0.99);
            }
            
            /* Debug Mode Styles */
            .theme-debug::before {
                content: 'Theme Debug: ' attr(data-theme);
                position: fixed;
                top: 10px;
                right: 10px;
                background: var(--bg-primary, #333);
                color: var(--text-primary, #fff);
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
                z-index: 10000;
                pointer-events: none;
            }
            
            /* Reduced Motion Support */
            @media (prefers-reduced-motion: reduce) {
                .theme-fade-transition,
                .theme-ripple-material {
                    animation: none !important;
                    transition: none !important;
                }
            }
        `;
        
        document.head.appendChild(style);
    }

    // ====================== 清理资源 ======================
    cleanup() {
        if (this.animationContainer && this.animationContainer.parentNode) {
            this.animationContainer.parentNode.removeChild(this.animationContainer);
        }
        
        // 清理样式
        const styleElement = document.querySelector('#unified-theme-animations-css');
        if (styleElement) {
            styleElement.remove();
        }
        
        // 清理类名
        document.documentElement.classList.remove('theme-debug', 'theme-transitioning');
    }
}

// ====================== 全局初始化 ======================
function initializeUnifiedThemeManager() {
    if (window.unifiedThemeManager) {
        return window.unifiedThemeManager;
    }
    
    window.unifiedThemeManager = new UnifiedThemeManager();
    initializeCompatibilityAliases();
    
    return window.unifiedThemeManager;
}

// 设置向后兼容别名
function initializeCompatibilityAliases() {
    // 向后兼容
    window.themeManager = window.unifiedThemeManager;
    window.enhancedThemeManager = window.unifiedThemeManager;
    window.themeAnimationManager = window.unifiedThemeManager;
    
    // 兼容老式API
    window.toggleTheme = () => window.unifiedThemeManager.toggleTheme();
    window.getCurrentTheme = () => window.unifiedThemeManager.getCurrentTheme();
    window.setTheme = (theme) => window.unifiedThemeManager.setTheme(theme);
}

// 等待DOM加载完成后创建全局统一主题管理器实例
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initializeUnifiedThemeManager();
    });
} else {
    // 如果DOM已经加载完成，立即初始化
    initializeUnifiedThemeManager();
}

// ====================== 开发环境调试支持 ======================
if (window.location.hostname === 'localhost' || 
    window.location.hostname === '127.0.0.1' || 
    window.location.search.includes('debug=true')) {
    
    window.debugTheme = () => {
        if (window.unifiedThemeManager) {
            window.unifiedThemeManager.setDebugMode(true);
        }
    };
    
    window.resetTheme = () => {
        if (window.unifiedThemeManager) {
            window.unifiedThemeManager.resetToSystemTheme();
        }
    };
    
    window.getThemeInfo = () => {
        if (window.unifiedThemeManager) {
            return {
                ...window.unifiedThemeManager.getBrowserInfo(),
                ...window.unifiedThemeManager.getPerformanceInfo()
            };
        }
        return null;
    };
}

// ====================== 页面卸载时清理 ======================
window.addEventListener('beforeunload', () => {
    if (window.unifiedThemeManager) {
        window.unifiedThemeManager.cleanup();
    }
});

// ====================== 导出模块（如果需要） ======================
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UnifiedThemeManager;
}

if (typeof define === 'function' && define.amd) {
    define(() => UnifiedThemeManager);
}