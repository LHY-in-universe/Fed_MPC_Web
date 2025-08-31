/**
 * 防白闪脚本 - 在页面加载前立即应用主题
 * 防止深色模式下的白色闪烁问题
 */
(function() {
    'use strict';
    
    try {
        // 获取保存的主题或系统偏好
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        const theme = savedTheme || (prefersDark ? 'dark' : 'light');
        
        // 立即设置主题属性到html元素
        document.documentElement.setAttribute('data-theme', theme);
        
        // 为body添加主题相关的class（如果需要）
        if (theme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
        
        console.log('🎨 防白闪: 主题已设置为', theme);
        
    } catch (error) {
        console.warn('⚠️ 防白闪脚本失败:', error);
        // 降级到深色主题作为默认
        document.documentElement.setAttribute('data-theme', 'dark');
        document.documentElement.classList.add('dark');
    }
})();