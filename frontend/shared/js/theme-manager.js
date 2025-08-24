/**
 * 主题管理器
 * 处理深色/浅色模式切换和主题状态持久化
 */

class ThemeManager {
    constructor() {
        this.theme = this.getStoredTheme() || this.getSystemTheme();
        this.initializeTheme();
        this.setupEventListeners();
    }

    // 获取存储的主题
    getStoredTheme() {
        return localStorage.getItem('theme');
    }

    // 获取系统主题偏好
    getSystemTheme() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    // 初始化主题
    initializeTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);
        this.updateThemeToggleIcon();
    }

    // 切换主题
    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', this.theme);
        localStorage.setItem('theme', this.theme);
        this.updateThemeToggleIcon();
        
        // 触发主题变更事件
        window.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { theme: this.theme }
        }));
    }

    // 更新主题切换按钮图标
    updateThemeToggleIcon() {
        const toggleButtons = document.querySelectorAll('.theme-toggle');
        toggleButtons.forEach(button => {
            const icon = button.querySelector('i, span');
            if (icon) {
                if (this.theme === 'dark') {
                    icon.innerHTML = '☀️'; // 浅色模式图标
                    button.title = 'Switch to Light Mode';
                } else {
                    icon.innerHTML = '🌙'; // 深色模式图标
                    button.title = 'Switch to Dark Mode';
                }
            }
        });
    }

    // 设置事件监听器
    setupEventListeners() {
        // 监听系统主题变化
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!this.getStoredTheme()) {
                this.theme = e.matches ? 'dark' : 'light';
                this.initializeTheme();
            }
        });

        // 主题切换按钮点击事件
        document.addEventListener('click', (e) => {
            if (e.target.closest('.theme-toggle')) {
                this.toggleTheme();
            }
        });
    }

    // 获取当前主题
    getCurrentTheme() {
        return this.theme;
    }

    // 检查是否为深色模式
    isDarkMode() {
        return this.theme === 'dark';
    }
}

// 创建全局主题管理器实例
window.themeManager = new ThemeManager();