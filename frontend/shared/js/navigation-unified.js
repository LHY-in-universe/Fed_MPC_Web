/**
 * 统一导航系统
 * 合并 emergency-navigation.js 和 navigation-support.js
 * 提供可靠且智能的导航功能
 */

(function() {
    'use strict';
    
    console.log('🚀 Unified Navigation: 初始化中...');
    
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
    
    // 智能导航函数（主要方法）
    function smartNavigate(targetPath) {
        try {
            const currentPath = window.location.pathname;
            const relativePath = calculateRelativePath(currentPath, targetPath);
            
            console.log('Smart Navigate:', {
                from: currentPath,
                to: targetPath,
                calculated: relativePath
            });
            
            window.location.href = relativePath;
        } catch (error) {
            console.warn('Smart navigate failed, using emergency method:', error);
            emergencyNavigate(targetPath);
        }
    }
    
    // 紧急导航方法（备用方法）
    function emergencyNavigate(targetPath) {
        try {
            const currentPath = window.location.pathname;
            console.log('🚨 Emergency Navigate:', {from: currentPath, to: targetPath});
            
            // 简单粗暴的路径判断
            let calculatedPath;
            if (currentPath.includes('/ai/pages/')) {
                calculatedPath = '../../' + targetPath;
            } else if (currentPath.includes('/blockchain/pages/')) {
                calculatedPath = '../../' + targetPath;
            } else if (currentPath.includes('/crypto/pages/')) {
                calculatedPath = '../../' + targetPath;
            } else if (currentPath.includes('/homepage/')) {
                calculatedPath = '../' + targetPath;
            } else {
                calculatedPath = targetPath;
            }
            
            console.log('Emergency path:', calculatedPath);
            window.location.href = calculatedPath;
            
        } catch (error) {
            console.error('Emergency navigation failed:', error);
            // 最后的备用方案
            const baseUrl = window.location.origin + window.location.pathname.split('/').slice(0, -2).join('/') + '/';
            const fallbackUrl = baseUrl + targetPath;
            console.log('Using fallback URL:', fallbackUrl);
            window.location.href = fallbackUrl;
        }
    }
    
    // 定义所有导航函数
    function defineNavigationFunctions() {
        // 主页导航
        window.goHome = window.goHome || function() {
            console.log('🏠 goHome() called');
            smartNavigate('homepage/index.html');
        };
        
        // AI模块导航
        window.goToAI = window.goToAI || function() {
            console.log('🤖 goToAI() called');
            smartNavigate('ai/pages/user-type-select.html');
        };
        
        // 区块链模块导航
        window.goToBlockchain = window.goToBlockchain || function() {
            console.log('⛓️ goToBlockchain() called');
            smartNavigate('blockchain/pages/login.html');
        };
        
        // 密码学模块导航
        window.goToCrypto = window.goToCrypto || function() {
            console.log('🔐 goToCrypto() called');
            smartNavigate('crypto/pages/login.html');
        };
        
        // 通用页面导航
        window.navigateToPage = window.navigateToPage || function(moduleName, pageName) {
            console.log(`📄 navigateToPage(${moduleName}, ${pageName}) called`);
            const targetPath = `${moduleName}/pages/${pageName}`;
            smartNavigate(targetPath);
        };
        
        // 返回功能
        window.goBack = window.goBack || function() {
            console.log('⬅️ goBack() called');
            if (window.history.length > 1) {
                window.history.back();
            } else {
                window.goHome();
            }
        };
        
        console.log('✅ All navigation functions defined');
    }
    
    // 验证导航函数
    function validateNavigationFunctions() {
        const functions = ['goHome', 'goToAI', 'goToBlockchain', 'goToCrypto', 'goBack'];
        const status = {};
        
        functions.forEach(func => {
            status[func] = typeof window[func] === 'function';
        });
        
        console.log('🔍 Navigation functions status:', status);
        return Object.values(status).every(Boolean);
    }
    
    // 初始化函数
    function initializeUnifiedNavigation() {
        defineNavigationFunctions();
        
        // 添加点击事件监听器用于错误处理
        document.addEventListener('click', function(e) {
            const target = e.target.closest('[onclick*="go"], [onclick*="navigate"]');
            if (target) {
                // 确保函数存在
                if (!validateNavigationFunctions()) {
                    console.warn('Navigation functions missing, redefining...');
                    defineNavigationFunctions();
                }
            }
        });
        
        // 导出全局API
        window.UnifiedNavigation = {
            smartNavigate: smartNavigate,
            emergencyNavigate: emergencyNavigate,
            calculateRelativePath: calculateRelativePath,
            defineNavigationFunctions: defineNavigationFunctions,
            validateNavigationFunctions: validateNavigationFunctions
        };
        
        console.log('🎉 Unified Navigation initialized successfully');
    }
    
    // 页面加载时初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeUnifiedNavigation);
    } else {
        initializeUnifiedNavigation();
    }
    
    // 窗口加载完成后再次确保（兼容性）
    window.addEventListener('load', function() {
        setTimeout(() => {
            if (!validateNavigationFunctions()) {
                console.warn('Re-initializing navigation functions...');
                defineNavigationFunctions();
            }
        }, 100);
    });
    
})();