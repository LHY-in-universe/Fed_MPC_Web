/**
 * 兼容性工具函数库
 * 为保持向后兼容而创建的工具函数
 */

// 确保 showToast 函数可用
window.showToast = window.showToast || function(message, type = 'info', duration = 3000) {
    // 优先使用统一工具函数
    if (window.UnifiedUtils && window.UnifiedUtils.notify) {
        window.UnifiedUtils.notify.show(message, type, duration);
        return;
    }
    
    // 降级方案：简单的通知实现
    console.log(`Toast [${type}]: ${message}`);
    
    // 创建简单的toast元素
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm transition-all duration-300`;
    
    // 设置样式
    const colors = {
        'success': 'bg-green-500 text-white',
        'error': 'bg-red-500 text-white', 
        'warning': 'bg-yellow-500 text-white',
        'info': 'bg-blue-500 text-white'
    };
    
    toast.className += ` ${colors[type] || colors.info}`;
    toast.textContent = message;
    
    // 添加到页面
    document.body.appendChild(toast);
    
    // 自动隐藏
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, duration);
};

// 确保其他可能需要的函数存在
window.showSuccess = window.showSuccess || function(message) {
    window.showToast(message, 'success');
};

window.showError = window.showError || function(message) {
    window.showToast(message, 'error');
};

window.showWarning = window.showWarning || function(message) {
    window.showToast(message, 'warning');
};

window.showInfo = window.showInfo || function(message) {
    window.showToast(message, 'info');
};

console.log('✅ common-utils.js loaded successfully');