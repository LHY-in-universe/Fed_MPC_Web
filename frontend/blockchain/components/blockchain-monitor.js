/**
 * 区块链网络监控组件
 * 实时显示区块链网络状态、节点信息、网络性能等
 */

class BlockchainMonitor {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.networkData = {};
        this.blockChart = null;
        this.updateInterval = null;
        this.selectedNetwork = 'testnet';
        
        this.init();
    }
    
    init() {
        this.createLayout();
        this.bindEvents();
        this.initCharts();
        this.startMonitoring();
        this.loadInitialData();
    }
    
    createLayout() {
        this.container.innerHTML = `
            <div class="blockchain-monitor">
                <div class="monitor-header">
                    <h3>区块链网络监控</h3>
                    <div class="monitor-controls">
                        <select id="networkSelector" class="form-select">
                            <option value="mainnet">主网</option>
                            <option value="testnet" selected>测试网</option>
                            <option value="local">本地网络</option>
                        </select>
                        <button id="refreshNetwork" class="blockchain-btn blockchain-btn-secondary">刷新</button>
                        <button id="exportData" class="btn btn-outline-secondary">导出数据</button>
                    </div>
                </div>
                
                <!-- 网络概览 -->
                <div class="network-overview mb-4">
                    <div class="row">
                        <div class="col-md-2">
                            <div class="network-stats">
                                <div class="stat-value" id="blockHeight">0</div>
                                <div class="stat-label">最新区块</div>
                                <div class="stat-trend" id="blockTrend">↑</div>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="network-stats">
                                <div class="stat-value" id="networkHashrate">0 H/s</div>
                                <div class="stat-label">全网算力</div>
                                <div class="stat-trend" id="hashrateTrend">↑</div>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="network-stats">
                                <div class="stat-value" id="difficulty">0</div>
                                <div class="stat-label">挖矿难度</div>
                                <div class="stat-trend" id="difficultyTrend">→</div>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="network-stats">
                                <div class="stat-value" id="avgBlockTime">0s</div>
                                <div class="stat-label">平均出块时间</div>
                                <div class="stat-trend" id="blockTimeTrend">→</div>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="network-stats">
                                <div class="stat-value" id="totalNodes">0</div>
                                <div class="stat-label">网络节点</div>
                                <div class="stat-trend" id="nodesTrend">↑</div>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="network-stats">
                                <div class="stat-value" id="tpsRate">0.0</div>
                                <div class="stat-label">TPS</div>
                                <div class="stat-trend" id="tpsTrend">↑</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 图表区域 -->
                <div class="row mb-4">
                    <div class="col-md-8">
                        <div class="blockchain-card">
                            <div class="card-header">
                                <h5>区块生成趋势</h5>
                                <div class="chart-controls">
                                    <select id="chartTimeRange" class="form-select form-select-sm">
                                        <option value="1h">1小时</option>
                                        <option value="6h">6小时</option>
                                        <option value="24h" selected>24小时</option>
                                        <option value="7d">7天</option>
                                    </select>
                                </div>
                            </div>
                            <div class="chart-container">
                                <canvas id="blockChart" width="800" height="300"></canvas>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="blockchain-card">
                            <h5>网络健康度</h5>
                            <div class="network-health">
                                <div class="health-item">
                                    <div class="health-label">整体状态</div>
                                    <div class="health-indicator">
                                        <div class="health-circle healthy" id="overallHealth"></div>
                                        <span id="overallHealthText">健康</span>
                                    </div>
                                </div>
                                <div class="health-item">
                                    <div class="health-label">节点连通性</div>
                                    <div class="health-bar">
                                        <div class="health-progress" id="nodeConnectivity" style="width: 95%"></div>
                                        <span class="health-percentage">95%</span>
                                    </div>
                                </div>
                                <div class="health-item">
                                    <div class="health-label">交易处理能力</div>
                                    <div class="health-bar">
                                        <div class="health-progress" id="txProcessing" style="width: 87%"></div>
                                        <span class="health-percentage">87%</span>
                                    </div>
                                </div>
                                <div class="health-item">
                                    <div class="health-label">网络同步率</div>
                                    <div class="health-bar">
                                        <div class="health-progress" id="syncRate" style="width: 99%"></div>
                                        <span class="health-percentage">99%</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 节点分布 -->
                <div class="row mb-4">
                    <div class="col-md-6">
                        <div class="blockchain-card">
                            <h5>节点地理分布</h5>
                            <div class="node-distribution" id="nodeDistribution">
                                <div class="distribution-item">
                                    <div class="region-name">北美</div>
                                    <div class="node-count">342 节点</div>
                                    <div class="distribution-bar">
                                        <div class="distribution-fill" style="width: 45%"></div>
                                    </div>
                                </div>
                                <div class="distribution-item">
                                    <div class="region-name">欧洲</div>
                                    <div class="node-count">298 节点</div>
                                    <div class="distribution-bar">
                                        <div class="distribution-fill" style="width: 39%"></div>
                                    </div>
                                </div>
                                <div class="distribution-item">
                                    <div class="region-name">亚洲</div>
                                    <div class="node-count">215 节点</div>
                                    <div class="distribution-bar">
                                        <div class="distribution-fill" style="width: 28%"></div>
                                    </div>
                                </div>
                                <div class="distribution-item">
                                    <div class="region-name">其他</div>
                                    <div class="node-count">87 节点</div>
                                    <div class="distribution-bar">
                                        <div class="distribution-fill" style="width: 11%"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="blockchain-card">
                            <h5>节点类型分布</h5>
                            <div class="node-types" id="nodeTypes">
                                <div class="type-item">
                                    <div class="type-icon">🔗</div>
                                    <div class="type-info">
                                        <div class="type-name">全节点</div>
                                        <div class="type-count">156</div>
                                        <div class="type-percentage">65%</div>
                                    </div>
                                </div>
                                <div class="type-item">
                                    <div class="type-icon">⚡</div>
                                    <div class="type-info">
                                        <div class="type-name">轻节点</div>
                                        <div class="type-count">72</div>
                                        <div class="type-percentage">30%</div>
                                    </div>
                                </div>
                                <div class="type-item">
                                    <div class="type-icon">⛏️</div>
                                    <div class="type-info">
                                        <div class="type-name">矿工节点</div>
                                        <div class="type-count">12</div>
                                        <div class="type-percentage">5%</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 最新区块 -->
                <div class="row mb-4">
                    <div class="col-12">
                        <div class="blockchain-card">
                            <div class="card-header">
                                <h5>最新区块</h5>
                                <div class="block-controls">
                                    <button id="autoRefreshBlocks" class="btn btn-sm btn-outline-primary">
                                        <i class="bi bi-arrow-repeat"></i> 自动刷新
                                    </button>
                                </div>
                            </div>
                            <div class="latest-blocks" id="latestBlocks">
                                <!-- 区块列表将动态生成 -->
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- MPC计算监控 -->
                <div class="row">
                    <div class="col-12">
                        <div class="blockchain-card">
                            <h5>多方计算(MPC)监控</h5>
                            <div class="mpc-monitor">
                                <div class="mpc-stats">
                                    <div class="mpc-stat-item">
                                        <div class="mpc-stat-value" id="activeMPCTasks">0</div>
                                        <div class="mpc-stat-label">活跃计算任务</div>
                                    </div>
                                    <div class="mpc-stat-item">
                                        <div class="mpc-stat-value" id="completedMPCTasks">0</div>
                                        <div class="mpc-stat-label">已完成任务</div>
                                    </div>
                                    <div class="mpc-stat-item">
                                        <div class="mpc-stat-value" id="mpcParticipants">0</div>
                                        <div class="mpc-stat-label">参与方数量</div>
                                    </div>
                                </div>
                                <div class="mpc-tasks" id="mpcTasks">
                                    <!-- MPC任务列表 -->
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    bindEvents() {
        document.getElementById('networkSelector').addEventListener('change', (e) => this.switchNetwork(e.target.value));
        document.getElementById('refreshNetwork').addEventListener('click', () => this.refreshNetworkData());
        document.getElementById('exportData').addEventListener('click', () => this.exportNetworkData());
        document.getElementById('chartTimeRange').addEventListener('change', (e) => this.updateChartTimeRange(e.target.value));
        document.getElementById('autoRefreshBlocks').addEventListener('click', () => this.toggleAutoRefresh());
    }
    
    initCharts() {
        const ctx = document.getElementById('blockChart').getContext('2d');
        this.blockChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '区块高度',
                    data: [],
                    borderColor: 'rgb(30, 58, 138)',
                    backgroundColor: 'rgba(30, 58, 138, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: '交易数量',
                    data: [],
                    borderColor: 'rgb(16, 185, 129)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '区块高度'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: '交易数量'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                    }
                }
            }
        });
    }
    
    startMonitoring() {
        this.updateInterval = setInterval(() => {
            this.updateNetworkStats();
            this.updateLatestBlocks();
            this.updateMPCTasks();
        }, 10000); // 每10秒更新一次
    }
    
    stopMonitoring() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
    
    async loadInitialData() {
        try {
            await this.updateNetworkStats();
            await this.updateLatestBlocks();
            await this.updateMPCTasks();
            await this.loadBlockHistory();
        } catch (error) {
            console.error('加载初始数据失败:', error);
        }
    }
    
    async updateNetworkStats() {
        try {
            const response = await fetch(`/api/blockchain/network/stats?network=${this.selectedNetwork}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const result = await response.json();
            if (result.success) {
                this.networkData = result.data;
                this.updateNetworkStatsUI();
            }
        } catch (error) {
            console.error('更新网络统计失败:', error);
        }
    }
    
    updateNetworkStatsUI() {
        const data = this.networkData;
        
        // 更新统计数据
        document.getElementById('blockHeight').textContent = data.block_height || '0';
        document.getElementById('networkHashrate').textContent = this.formatHashrate(data.hashrate || 0);
        document.getElementById('difficulty').textContent = this.formatNumber(data.difficulty || 0);
        document.getElementById('avgBlockTime').textContent = `${data.avg_block_time || 0}s`;
        document.getElementById('totalNodes').textContent = data.total_nodes || '0';
        document.getElementById('tpsRate').textContent = (data.tps || 0).toFixed(1);
        
        // 更新趋势指示器
        this.updateTrendIndicators(data);
        
        // 更新网络健康度
        this.updateNetworkHealth(data);
    }
    
    updateTrendIndicators(data) {
        const trends = {
            blockTrend: data.block_trend || 'up',
            hashrateTrend: data.hashrate_trend || 'up',
            difficultyTrend: data.difficulty_trend || 'stable',
            blockTimeTrend: data.block_time_trend || 'stable',
            nodesTrend: data.nodes_trend || 'up',
            tpsTrend: data.tps_trend || 'up'
        };
        
        Object.entries(trends).forEach(([elementId, trend]) => {
            const element = document.getElementById(elementId);
            if (element) {
                element.textContent = trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→';
                element.className = `stat-trend ${trend}`;
            }
        });
    }
    
    updateNetworkHealth(data) {
        const healthScore = data.health_score || 0.95;
        const healthText = healthScore > 0.9 ? '健康' : healthScore > 0.7 ? '良好' : '警告';
        const healthClass = healthScore > 0.9 ? 'healthy' : healthScore > 0.7 ? 'warning' : 'danger';
        
        const healthElement = document.getElementById('overallHealth');
        const healthTextElement = document.getElementById('overallHealthText');
        
        if (healthElement) {
            healthElement.className = `health-circle ${healthClass}`;
        }
        if (healthTextElement) {
            healthTextElement.textContent = healthText;
        }
        
        // 更新健康度进度条
        this.updateHealthBars(data);
    }
    
    updateHealthBars(data) {
        const metrics = {
            nodeConnectivity: data.node_connectivity || 0.95,
            txProcessing: data.tx_processing_capacity || 0.87,
            syncRate: data.sync_rate || 0.99
        };
        
        Object.entries(metrics).forEach(([id, value]) => {
            const element = document.getElementById(id);
            const percentage = Math.round(value * 100);
            
            if (element) {
                element.style.width = `${percentage}%`;
                element.parentNode.querySelector('.health-percentage').textContent = `${percentage}%`;
            }
        });
    }
    
    async updateLatestBlocks() {
        try {
            const response = await fetch(`/api/blockchain/blocks/latest?network=${this.selectedNetwork}&limit=5`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const result = await response.json();
            if (result.success) {
                this.renderLatestBlocks(result.data);
            }
        } catch (error) {
            console.error('更新最新区块失败:', error);
        }
    }
    
    renderLatestBlocks(blocks) {
        const container = document.getElementById('latestBlocks');
        if (!container) return;
        
        container.innerHTML = blocks.map(block => `
            <div class="block-item">
                <div class="block-header">
                    <div class="block-number">
                        <span class="block-height">#${block.height}</span>
                        <span class="block-time">${this.formatTimestamp(block.timestamp)}</span>
                    </div>
                    <div class="block-stats">
                        <span class="tx-count">${block.tx_count} 交易</span>
                        <span class="block-size">${this.formatBytes(block.size)}</span>
                    </div>
                </div>
                <div class="block-details">
                    <div class="block-hash">
                        <span class="hash-label">区块哈希:</span>
                        <span class="hash-address" title="${block.hash}">${this.truncateHash(block.hash)}</span>
                    </div>
                    <div class="block-miner">
                        <span class="miner-label">矿工:</span>
                        <span class="hash-address" title="${block.miner}">${this.truncateHash(block.miner)}</span>
                    </div>
                    <div class="block-reward">
                        <span class="reward-label">奖励:</span>
                        <span class="reward-value">${block.reward} ETH</span>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    async loadBlockHistory() {
        try {
            const timeRange = document.getElementById('chartTimeRange').value;
            const response = await fetch(`/api/blockchain/blocks/history?network=${this.selectedNetwork}&range=${timeRange}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const result = await response.json();
            if (result.success) {
                this.updateBlockChart(result.data);
            }
        } catch (error) {
            console.error('加载区块历史失败:', error);
        }
    }
    
    updateBlockChart(data) {
        const labels = data.map(item => new Date(item.timestamp).toLocaleTimeString());
        const blockHeights = data.map(item => item.height);
        const txCounts = data.map(item => item.tx_count);
        
        this.blockChart.data.labels = labels;
        this.blockChart.data.datasets[0].data = blockHeights;
        this.blockChart.data.datasets[1].data = txCounts;
        this.blockChart.update();
    }
    
    async updateMPCTasks() {
        try {
            const response = await fetch('/api/blockchain/mpc/status', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const result = await response.json();
            if (result.success) {
                this.updateMPCStats(result.data);
                this.renderMPCTasks(result.data.tasks);
            }
        } catch (error) {
            console.error('更新MPC任务失败:', error);
        }
    }
    
    updateMPCStats(data) {
        document.getElementById('activeMPCTasks').textContent = data.active_tasks || '0';
        document.getElementById('completedMPCTasks').textContent = data.completed_tasks || '0';
        document.getElementById('mpcParticipants').textContent = data.total_participants || '0';
    }
    
    renderMPCTasks(tasks) {
        const container = document.getElementById('mpcTasks');
        if (!container) return;
        
        if (!tasks || tasks.length === 0) {
            container.innerHTML = '<p class="text-muted">暂无MPC计算任务</p>';
            return;
        }
        
        container.innerHTML = tasks.map(task => `
            <div class="mpc-task-item">
                <div class="task-header">
                    <div class="task-id">任务 #${task.id}</div>
                    <div class="mpc-status ${task.status}">${this.getMPCStatusText(task.status)}</div>
                </div>
                <div class="task-info">
                    <div class="task-detail">
                        <span class="label">类型:</span>
                        <span class="value">${task.type}</span>
                    </div>
                    <div class="task-detail">
                        <span class="label">参与方:</span>
                        <span class="value">${task.participants}</span>
                    </div>
                    <div class="task-detail">
                        <span class="label">进度:</span>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${task.progress}%"></div>
                            <span class="progress-text">${task.progress}%</span>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    switchNetwork(network) {
        this.selectedNetwork = network;
        this.refreshNetworkData();
    }
    
    async refreshNetworkData() {
        await this.loadInitialData();
        this.showNotification(`${this.getNetworkName(this.selectedNetwork)}数据已刷新`, 'info');
    }
    
    updateChartTimeRange(timeRange) {
        this.loadBlockHistory();
    }
    
    toggleAutoRefresh() {
        const button = document.getElementById('autoRefreshBlocks');
        
        if (this.updateInterval) {
            this.stopMonitoring();
            button.innerHTML = '<i class="bi bi-arrow-repeat"></i> 开始自动刷新';
            button.classList.remove('btn-primary');
            button.classList.add('btn-outline-primary');
        } else {
            this.startMonitoring();
            button.innerHTML = '<i class="bi bi-pause"></i> 停止自动刷新';
            button.classList.remove('btn-outline-primary');
            button.classList.add('btn-primary');
        }
    }
    
    exportNetworkData() {
        const data = {
            network: this.selectedNetwork,
            timestamp: new Date().toISOString(),
            stats: this.networkData,
            export_time: new Date().toLocaleString()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        
        a.href = url;
        a.download = `blockchain-network-data-${this.selectedNetwork}-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('网络数据已导出', 'success');
    }
    
    // 工具方法
    formatHashrate(hashrate) {
        if (hashrate >= 1e12) return `${(hashrate / 1e12).toFixed(1)} TH/s`;
        if (hashrate >= 1e9) return `${(hashrate / 1e9).toFixed(1)} GH/s`;
        if (hashrate >= 1e6) return `${(hashrate / 1e6).toFixed(1)} MH/s`;
        if (hashrate >= 1e3) return `${(hashrate / 1e3).toFixed(1)} KH/s`;
        return `${hashrate} H/s`;
    }
    
    formatNumber(num) {
        if (num >= 1e9) return `${(num / 1e9).toFixed(1)}B`;
        if (num >= 1e6) return `${(num / 1e6).toFixed(1)}M`;
        if (num >= 1e3) return `${(num / 1e3).toFixed(1)}K`;
        return num.toString();
    }
    
    formatBytes(bytes) {
        if (bytes >= 1e6) return `${(bytes / 1e6).toFixed(1)} MB`;
        if (bytes >= 1e3) return `${(bytes / 1e3).toFixed(1)} KB`;
        return `${bytes} B`;
    }
    
    formatTimestamp(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diff = Math.floor((now - time) / 1000);
        
        if (diff < 60) return `${diff}秒前`;
        if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`;
        return time.toLocaleDateString();
    }
    
    truncateHash(hash) {
        return `${hash.substring(0, 6)}...${hash.substring(hash.length - 4)}`;
    }
    
    getNetworkName(network) {
        const names = {
            mainnet: '主网',
            testnet: '测试网',
            local: '本地网络'
        };
        return names[network] || network;
    }
    
    getMPCStatusText(status) {
        const statuses = {
            computing: '计算中',
            completed: '已完成',
            error: '出错',
            pending: '等待中'
        };
        return statuses[status] || status;
    }
    
    showNotification(message, type) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999;';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alert);
        
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 5000);
    }
    
    destroy() {
        this.stopMonitoring();
        if (this.blockChart) {
            this.blockChart.destroy();
        }
    }
}

// 导出组件
window.BlockchainMonitor = BlockchainMonitor;