/**
 * 服务器控制台脚本 - 优化重构版
 * 大幅减少代码重复，使用模板化方法
 */

let networkChart;
let isEnglish = localStorage.getItem('language') === 'en';

// Listen for language changes and update charts
window.addEventListener('languageChanged', function(event) {
    isEnglish = event.detail.language === 'en';
    
    // Reinitialize charts with new language
    if (networkChart) {
        networkChart.destroy();
        initializeNetworkChart();
    }
});

// ====================== 数据模板系统 ======================
const ViewTemplates = {
    systemStatus: (isEnglish) => ({
        title: isEnglish ? 'System Status Details' : '系统状态详情',
        content: `
            <div class="space-y-6">
                <div class="grid grid-cols-2 gap-4">
                    ${generateStatusCard('CPU Usage', 'CPU使用率', '45%', 'text-green-600', isEnglish)}
                    ${generateStatusCard('Memory Usage', '内存使用率', '67%', 'text-yellow-600', isEnglish)}
                    ${generateStatusCard('Disk Usage', '磁盘使用率', '23%', 'text-green-600', isEnglish)}
                    ${generateStatusCard('Network', '网络状态', 'Online', '在线', isEnglish)}
                </div>
                <div class="mt-4">
                    <h4 class="font-semibold mb-2">${isEnglish ? 'System Information' : '系统信息'}</h4>
                    <div class="bg-gray-50 dark:bg-gray-700 p-3 rounded text-sm">
                        <p>OS: Ubuntu 20.04 LTS</p>
                        <p>Python: 3.8.10</p>
                        <p>PyTorch: 1.9.0</p>
                        <p>${isEnglish ? 'Uptime' : '运行时间'}: 7 days 14 hours</p>
                    </div>
                </div>
            </div>
        `
    }),

    connectedClients: (isEnglish) => ({
        title: isEnglish ? 'Connected Clients' : '已连接客户端',
        content: `
            <div class="space-y-4">
                ${generateClientList([
                    { id: 'client-001', name: 'Client Alpha', status: 'active', lastSeen: '2分钟前' },
                    { id: 'client-002', name: 'Client Beta', status: 'training', lastSeen: '1分钟前' },
                    { id: 'client-003', name: 'Client Gamma', status: 'idle', lastSeen: '5分钟前' }
                ], isEnglish)}
            </div>
        `
    }),

    activeSessions: (isEnglish) => ({
        title: isEnglish ? 'Active Training Sessions' : '活跃训练会话',
        content: `
            <div class="space-y-4">
                ${generateSessionList([
                    { id: 'session-1', model: 'ResNet-50', participants: 5, progress: 65, status: 'training' },
                    { id: 'session-2', model: 'BERT-base', participants: 3, progress: 23, status: 'training' },
                    { id: 'session-3', model: 'GPT-2', participants: 8, progress: 89, status: 'finalizing' }
                ], isEnglish)}
            </div>
        `
    }),

    modelManagement: (isEnglish) => ({
        title: isEnglish ? 'Model Management' : '模型管理',
        content: `
            <div class="space-y-4">
                ${generateModelList([
                    { name: 'ResNet-50', version: 'v1.2', size: '98MB', accuracy: '94.2%', status: 'active' },
                    { name: 'BERT-base', version: 'v2.1', size: '438MB', accuracy: '89.7%', status: 'training' },
                    { name: 'GPT-2', version: 'v1.0', size: '774MB', accuracy: '91.5%', status: 'idle' }
                ], isEnglish)}
            </div>
        `
    }),

    networkPerformance: (isEnglish) => ({
        title: isEnglish ? 'Network Performance' : '网络性能',
        content: `
            <div class="space-y-4">
                <div class="grid grid-cols-2 gap-4">
                    ${generateMetricCard('Latency', '延迟', '45ms', 'text-green-600', isEnglish)}
                    ${generateMetricCard('Bandwidth', '带宽', '125.3 MB/s', 'text-blue-600', isEnglish)}
                    ${generateMetricCard('Packet Loss', '丢包率', '0.02%', 'text-green-600', isEnglish)}
                    ${generateMetricCard('Connections', '连接数', '234', 'text-yellow-600', isEnglish)}
                </div>
                <div class="mt-4">
                    <h4 class="font-semibold mb-2">${isEnglish ? 'Network Statistics' : '网络统计'}</h4>
                    <canvas id="networkMiniChart" width="400" height="200"></canvas>
                </div>
            </div>
        `
    }),

    systemLogs: (isEnglish) => ({
        title: isEnglish ? 'System Logs' : '系统日志',
        content: `
            <div class="space-y-2">
                ${generateLogEntries([
                    { time: '14:23:45', level: 'INFO', message: 'Client client-001 connected successfully' },
                    { time: '14:22:31', level: 'INFO', message: 'Training session session-1 started' },
                    { time: '14:21:18', level: 'WARN', message: 'High memory usage detected: 85%' },
                    { time: '14:20:02', level: 'INFO', message: 'Model ResNet-50 updated to version 1.2' },
                    { time: '14:19:45', level: 'ERROR', message: 'Connection timeout for client-005' }
                ], isEnglish)}
            </div>
        `
    })
};

// ====================== 模板生成函数 ======================
function generateStatusCard(titleEn, titleZh, value, colorClass, isEnglish) {
    const title = isEnglish ? titleEn : titleZh;
    return `
        <div class="bg-white dark:bg-gray-800 p-4 rounded-lg border">
            <div class="text-sm text-gray-600 dark:text-gray-300">${title}</div>
            <div class="text-2xl font-semibold ${colorClass}">${value}</div>
        </div>
    `;
}

function generateClientList(clients, isEnglish) {
    return clients.map(client => `
        <div class="bg-white dark:bg-gray-800 p-4 rounded-lg border flex justify-between items-center">
            <div>
                <div class="font-semibold">${client.name}</div>
                <div class="text-sm text-gray-600">${isEnglish ? 'ID' : '客户端ID'}: ${client.id}</div>
            </div>
            <div class="text-right">
                <div class="px-2 py-1 rounded text-xs ${getStatusColor(client.status)}">
                    ${getStatusText(client.status, isEnglish)}
                </div>
                <div class="text-sm text-gray-500 mt-1">${client.lastSeen}</div>
            </div>
        </div>
    `).join('');
}

function generateSessionList(sessions, isEnglish) {
    return sessions.map(session => `
        <div class="bg-white dark:bg-gray-800 p-4 rounded-lg border">
            <div class="flex justify-between items-start mb-2">
                <div class="font-semibold">${session.model}</div>
                <div class="px-2 py-1 rounded text-xs ${getStatusColor(session.status)}">
                    ${getStatusText(session.status, isEnglish)}
                </div>
            </div>
            <div class="text-sm text-gray-600 mb-2">
                ${isEnglish ? 'Participants' : '参与者'}: ${session.participants} | 
                ${isEnglish ? 'Progress' : '进度'}: ${session.progress}%
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-blue-600 h-2 rounded-full" style="width: ${session.progress}%"></div>
            </div>
        </div>
    `).join('');
}

function generateModelList(models, isEnglish) {
    return models.map(model => `
        <div class="bg-white dark:bg-gray-800 p-4 rounded-lg border">
            <div class="flex justify-between items-start">
                <div>
                    <div class="font-semibold">${model.name}</div>
                    <div class="text-sm text-gray-600">
                        ${isEnglish ? 'Version' : '版本'}: ${model.version} | 
                        ${isEnglish ? 'Size' : '大小'}: ${model.size}
                    </div>
                    <div class="text-sm text-gray-600">
                        ${isEnglish ? 'Accuracy' : '准确率'}: ${model.accuracy}
                    </div>
                </div>
                <div class="px-2 py-1 rounded text-xs ${getStatusColor(model.status)}">
                    ${getStatusText(model.status, isEnglish)}
                </div>
            </div>
        </div>
    `).join('');
}

function generateMetricCard(titleEn, titleZh, value, colorClass, isEnglish) {
    return generateStatusCard(titleEn, titleZh, value, colorClass, isEnglish);
}

function generateLogEntries(logs, isEnglish) {
    return logs.map(log => `
        <div class="text-sm font-mono bg-gray-50 dark:bg-gray-700 p-2 rounded">
            <span class="text-gray-500">[${log.time}]</span>
            <span class="font-semibold ${getLevelColor(log.level)}">[${log.level}]</span>
            <span class="ml-2">${log.message}</span>
        </div>
    `).join('');
}

// ====================== 工具函数 ======================
function getStatusColor(status) {
    const colors = {
        active: 'bg-green-100 text-green-800',
        training: 'bg-blue-100 text-blue-800',
        idle: 'bg-gray-100 text-gray-800',
        finalizing: 'bg-yellow-100 text-yellow-800',
        offline: 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
}

function getStatusText(status, isEnglish) {
    const texts = {
        active: { en: 'Active', zh: '活跃' },
        training: { en: 'Training', zh: '训练中' },
        idle: { en: 'Idle', zh: '空闲' },
        finalizing: { en: 'Finalizing', zh: '完成中' },
        offline: { en: 'Offline', zh: '离线' }
    };
    return texts[status] ? texts[status][isEnglish ? 'en' : 'zh'] : status;
}

function getLevelColor(level) {
    const colors = {
        INFO: 'text-blue-600',
        WARN: 'text-yellow-600',
        ERROR: 'text-red-600',
        DEBUG: 'text-gray-600'
    };
    return colors[level] || 'text-gray-600';
}

// ====================== 统一模态框系统 ======================
function showModal(templateKey) {
    const template = ViewTemplates[templateKey];
    if (!template) {
        console.error('Unknown template:', templateKey);
        return;
    }

    const data = template(isEnglish);
    const modal = document.getElementById('detailModal');
    const title = document.getElementById('modalTitle');
    const content = document.getElementById('modalContent');

    title.textContent = data.title;
    content.innerHTML = data.content;
    modal.classList.remove('hidden');
    
    // 如果是网络性能视图，初始化mini图表
    if (templateKey === 'networkPerformance') {
        setTimeout(() => initNetworkMiniChart(), 100);
    }
}

function closeModal() {
    const modal = document.getElementById('detailModal');
    modal.classList.add('hidden');
}

// ====================== 视图函数 - 大幅简化 ======================
function viewSystemStatus() { showModal('systemStatus'); }
function viewConnectedClients() { showModal('connectedClients'); }
function viewActiveSessions() { showModal('activeSessions'); }
function viewModelManagementDetails() { showModal('modelManagement'); }
function viewNetworkPerformanceDetails() { showModal('networkPerformance'); }
function viewSystemLogsDetails() { showModal('systemLogs'); }

// 合并相似功能的函数
function viewPendingTrainingRequests() { viewActiveSessions(); }
function viewActiveTrainingSessionsDetails() { viewActiveSessions(); }
function viewClientManagementDetails() { viewConnectedClients(); }
function viewPendingRequests() { viewSystemLogsDetails(); }

// ====================== 初始化函数 ======================
document.addEventListener('DOMContentLoaded', function() {
    initializeServerDashboard();
    initializeNetworkChart();
    startLogUpdates();
});

function initializeServerDashboard() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const userInfo = document.getElementById('userInfo');
    
    // 详细的身份验证检查
    const authResult = checkAuthentication();
    if (!authResult.success) {
        showSecurityError(authResult);
        return;
    }
    
    if (user.name) {
        userInfo.textContent = `${isEnglish ? 'Welcome' : '欢迎'}，${user.name}`;
    }
}

/**
 * 检查用户身份验证状态
 */
function checkAuthentication() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const userType = localStorage.getItem('aiUserType');
    const token = localStorage.getItem('token');
    const loginTime = localStorage.getItem('loginTime');
    
    console.log('🔐 安全验证检查:');
    console.log('- 用户信息:', user);
    console.log('- 用户类型:', userType);
    console.log('- 登录令牌:', token ? '存在' : '缺失');
    console.log('- 登录时间:', loginTime);
    
    // 检查用户是否已登录
    if (!user.name && !user.email) {
        return {
            success: false,
            error: 'NO_LOGIN',
            message: isEnglish ? 'User not logged in' : '用户未登录',
            details: isEnglish ? 'Please login first to access the server dashboard' : '请先登录以访问服务器控制台',
            redirect: './login.html',
            debugInfo: {
                userObject: user,
                hasName: !!user.name,
                hasEmail: !!user.email,
                localStorage: {
                    user: localStorage.getItem('user'),
                    token: localStorage.getItem('token')
                }
            }
        };
    }
    
    // 检查用户类型权限
    const currentUserType = userType || user.type;
    if (currentUserType !== 'server') {
        return {
            success: false,
            error: 'INSUFFICIENT_PERMISSIONS',
            message: isEnglish ? 'Access denied: Server administrator permission required' : '权限不足：需要服务器管理员权限',
            details: isEnglish ? 
                `Current user type: ${currentUserType || 'unknown'}, Required: server` :
                `当前用户类型: ${currentUserType || '未知'}，需要: server`,
            redirect: './user-type-select.html',
            debugInfo: {
                currentUserType,
                requiredType: 'server',
                aiUserType: userType,
                userObjectType: user.type,
                localStorage: {
                    aiUserType: localStorage.getItem('aiUserType'),
                    userType: localStorage.getItem('userType'),
                    businessType: localStorage.getItem('businessType')
                }
            }
        };
    }
    
    // 检查登录会话有效性
    if (loginTime) {
        const loginDate = new Date(loginTime);
        const now = new Date();
        const timeDiff = now - loginDate;
        const hoursDiff = timeDiff / (1000 * 60 * 60);
        
        if (hoursDiff > 24) {
            return {
                success: false,
                error: 'SESSION_EXPIRED',
                message: isEnglish ? 'Login session expired' : '登录会话已过期',
                details: isEnglish ? 
                    `Session expired ${Math.floor(hoursDiff)}h ago, please login again` :
                    `会话已过期${Math.floor(hoursDiff)}小时，请重新登录`,
                redirect: './login.html',
                debugInfo: {
                    loginTime,
                    currentTime: now.toISOString(),
                    hoursDiff: Math.floor(hoursDiff)
                }
            }
        }
    }
    
    console.log('✅ 安全验证通过');
    return { success: true };
}

/**
 * 显示安全错误信息
 */
function showSecurityError(authResult) {
    console.error('❌ 安全验证失败:', authResult);
    
    // 创建错误显示容器
    const errorContainer = document.createElement('div');
    errorContainer.id = 'securityErrorModal';
    errorContainer.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    errorContainer.innerHTML = `
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
            <div class="flex items-center mb-4">
                <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mr-4">
                    <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                </div>
                <div>
                    <h3 class="text-lg font-semibold text-red-600">${isEnglish ? 'Security Verification Failed' : '安全验证失败'}</h3>
                    <p class="text-sm text-gray-500">${authResult.error}</p>
                </div>
            </div>
            
            <div class="mb-6">
                <p class="text-gray-900 dark:text-gray-100 font-medium mb-2">${authResult.message}</p>
                <p class="text-gray-600 dark:text-gray-300 text-sm mb-4">${authResult.details}</p>
                
                <div class="bg-gray-50 dark:bg-gray-700 rounded p-3 text-xs">
                    <div class="font-medium text-gray-700 dark:text-gray-300 mb-2">${isEnglish ? 'Debug Information:' : '调试信息:'}</div>
                    <pre class="text-gray-600 dark:text-gray-400 whitespace-pre-wrap">${JSON.stringify(authResult.debugInfo, null, 2)}</pre>
                </div>
            </div>
            
            <div class="flex space-x-3">
                <button onclick="redirectToFix()" class="flex-1 bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 text-sm">
                    ${isEnglish ? 'Go to Login' : '前往登录'}
                </button>
                <button onclick="closeErrorModal()" class="flex-1 bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600 text-sm">
                    ${isEnglish ? 'Close' : '关闭'}
                </button>
                <button onclick="showFixGuide()" class="flex-1 bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 text-sm">
                    ${isEnglish ? 'Fix Guide' : '修复指南'}
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(errorContainer);
    
    // 存储重定向信息供按钮使用
    window.securityErrorRedirect = authResult.redirect;
    window.securityErrorInfo = authResult;
    
    // 5秒后自动重定向(可选)
    setTimeout(() => {
        if (document.getElementById('securityErrorModal')) {
            console.log('⏰ 5秒后自动重定向到:', authResult.redirect);
            window.location.href = authResult.redirect;
        }
    }, 5000);
}

// 错误模态框相关函数
function redirectToFix() {
    if (window.securityErrorRedirect) {
        window.location.href = window.securityErrorRedirect;
    }
}

function closeErrorModal() {
    const modal = document.getElementById('securityErrorModal');
    if (modal) {
        modal.remove();
    }
}

function showFixGuide() {
    const errorInfo = window.securityErrorInfo;
    let guideMessage = '';
    
    switch(errorInfo.error) {
        case 'NO_LOGIN':
            guideMessage = isEnglish ? 
                'Steps to fix:\n1. Go to homepage\n2. Select AI module\n3. Choose user type\n4. Login with credentials' :
                '修复步骤:\n1. 前往主页\n2. 选择AI模块\n3. 选择用户类型\n4. 使用账号密码登录';
            break;
        case 'INSUFFICIENT_PERMISSIONS':
            guideMessage = isEnglish ?
                'Steps to fix:\n1. Go to user type selection\n2. Choose "Server Administrator"\n3. Login again' :
                '修复步骤:\n1. 前往用户类型选择\n2. 选择"总服务器"\n3. 重新登录';
            break;
        case 'SESSION_EXPIRED':
            guideMessage = isEnglish ?
                'Steps to fix:\n1. Clear browser cache\n2. Login again\n3. Session will be valid for 24 hours' :
                '修复步骤:\n1. 清除浏览器缓存\n2. 重新登录\n3. 会话有效期为24小时';
            break;
        default:
            guideMessage = isEnglish ?
                'Please contact administrator for assistance' :
                '请联系管理员获取帮助';
    }
    
    alert(guideMessage);
}

function initializeNetworkChart() {
    const ctx = document.getElementById('networkChart');
    if (!ctx) return;
    
    networkChart = new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: Array.from({length: 20}, (_, i) => i + 1),
            datasets: [{
                label: isEnglish ? 'Network Latency (ms)' : '网络延迟 (ms)',
                data: Array.from({length: 20}, () => 50 + Math.random() * 50),
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4
            }, {
                label: isEnglish ? 'Bandwidth Usage (%)' : '带宽使用率 (%)',
                data: Array.from({length: 20}, () => 30 + Math.random() * 40),
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

function initNetworkMiniChart() {
    const ctx = document.getElementById('networkMiniChart');
    if (!ctx) return;
    
    new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: Array.from({length: 10}, (_, i) => i + 1),
            datasets: [{
                label: isEnglish ? 'Network Activity' : '网络活动',
                data: Array.from({length: 10}, () => Math.random() * 100),
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { x: { display: false }, y: { display: false } }
        }
    });
}

// ====================== 数据更新 ======================
function startLogUpdates() {
    // 模拟日志更新
    setInterval(updateNetworkChart, 5000);
}

function updateNetworkChart() {
    if (networkChart) {
        const newLatencyData = networkChart.data.datasets[0].data.slice(1);
        newLatencyData.push(50 + Math.random() * 50);
        networkChart.data.datasets[0].data = newLatencyData;

        const newBandwidthData = networkChart.data.datasets[1].data.slice(1);
        newBandwidthData.push(30 + Math.random() * 40);
        networkChart.data.datasets[1].data = newBandwidthData;

        networkChart.update('none');
    }
}

function logout() {
    localStorage.clear();
    window.location.href = './login.html';
}

console.log('✅ Server Dashboard (Optimized) loaded successfully');