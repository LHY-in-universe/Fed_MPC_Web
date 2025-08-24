/**
 * 区块链交易监控组件
 * 实时显示交易状态、Gas费用、确认进度等信息
 */

class TransactionMonitor {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.transactions = [];
        this.updateInterval = null;
        this.networkStats = {};
        
        this.init();
    }
    
    init() {
        this.createLayout();
        this.bindEvents();
        this.startMonitoring();
        this.loadInitialData();
    }
    
    createLayout() {
        this.container.innerHTML = `
            <div class="blockchain-card">
                <div class="card-header">
                    <h3>交易监控</h3>
                    <div class="monitor-controls">
                        <button id="sendTransaction" class="blockchain-btn">发送交易</button>
                        <button id="refreshTransactions" class="blockchain-btn blockchain-btn-secondary">刷新</button>
                        <div class="network-selector">
                            <select id="networkSelect" class="form-select">
                                <option value="mainnet">主网</option>
                                <option value="testnet" selected>测试网</option>
                                <option value="local">本地网络</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <!-- 网络统计 -->
                <div class="row mb-4">
                    <div class="col-md-3">
                        <div class="network-stats">
                            <div class="stat-value" id="blockHeight">0</div>
                            <div class="stat-label">当前区块高度</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="network-stats">
                            <div class="stat-value" id="gasPrice">0</div>
                            <div class="stat-label">Gas价格 (Gwei)</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="network-stats">
                            <div class="stat-value" id="pendingTxs">0</div>
                            <div class="stat-label">待处理交易</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="network-stats">
                            <div class="stat-value" id="tps">0.0</div>
                            <div class="stat-label">TPS</div>
                        </div>
                    </div>
                </div>
                
                <!-- 交易池状态 -->
                <div class="row mb-4">
                    <div class="col-12">
                        <div class="blockchain-card">
                            <h5>交易池状态</h5>
                            <div class="mempool-visual" id="mempoolVisual">
                                <div class="mempool-legend">
                                    <span class="legend-item"><span class="status-indicator status-pending"></span>待处理</span>
                                    <span class="legend-item"><span class="status-indicator status-mining"></span>打包中</span>
                                    <span class="legend-item"><span class="status-indicator status-confirmed"></span>已确认</span>
                                </div>
                                <div class="mempool-grid" id="mempoolGrid"></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 交易列表 -->
                <div class="row">
                    <div class="col-12">
                        <div class="transaction-list">
                            <div class="list-header">
                                <h5>最近交易</h5>
                                <div class="list-filters">
                                    <select id="statusFilter" class="form-select">
                                        <option value="">所有状态</option>
                                        <option value="pending">待处理</option>
                                        <option value="confirmed">已确认</option>
                                        <option value="failed">失败</option>
                                    </select>
                                    <input type="text" id="searchTx" class="form-control" placeholder="搜索交易哈希...">
                                </div>
                            </div>
                            <div class="transaction-items" id="transactionItems"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 发送交易模态框 -->
            <div class="modal fade" id="sendTransactionModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">发送交易</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="transactionForm">
                                <div class="mb-3">
                                    <label class="form-label">接收地址</label>
                                    <input type="text" class="form-control" id="recipientAddress" 
                                           placeholder="0x..." required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">金额 (ETH)</label>
                                    <input type="number" class="form-control" id="amount" 
                                           placeholder="0.0" step="0.001" min="0" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Gas限制</label>
                                    <input type="number" class="form-control" id="gasLimit" 
                                           value="21000" min="21000">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Gas价格 (Gwei)</label>
                                    <input type="number" class="form-control" id="gasPrice" 
                                           value="20" min="1">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">数据 (可选)</label>
                                    <textarea class="form-control" id="txData" rows="3" 
                                              placeholder="0x..."></textarea>
                                </div>
                                <div class="gas-estimation">
                                    <div class="alert alert-info">
                                        <strong>预估费用:</strong> <span id="estimatedFee">0.00042 ETH</span>
                                        <br><strong>预计确认时间:</strong> <span id="estimatedTime">~2分钟</span>
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="submit" form="transactionForm" class="blockchain-btn">发送交易</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.bindEvents();
    }
    
    bindEvents() {
        document.getElementById('sendTransaction').addEventListener('click', () => this.showSendTransactionModal());
        document.getElementById('refreshTransactions').addEventListener('click', () => this.refreshTransactions());
        document.getElementById('networkSelect').addEventListener('change', (e) => this.switchNetwork(e.target.value));
        document.getElementById('statusFilter').addEventListener('change', (e) => this.filterTransactions());
        document.getElementById('searchTx').addEventListener('input', (e) => this.searchTransactions());
        
        const transactionForm = document.getElementById('transactionForm');
        if (transactionForm) {
            transactionForm.addEventListener('submit', (e) => this.sendTransaction(e));
            
            // Gas价格和限制变化时重新计算费用
            document.getElementById('gasLimit').addEventListener('input', () => this.updateGasEstimation());
            document.getElementById('gasPrice').addEventListener('input', () => this.updateGasEstimation());
        }
    }
    
    async loadInitialData() {
        try {
            // 加载网络统计
            await this.updateNetworkStats();
            
            // 加载交易历史
            await this.loadTransactionHistory();
            
            // 更新内存池状态
            await this.updateMempoolStatus();
        } catch (error) {
            console.error('加载初始数据失败:', error);
        }
    }
    
    startMonitoring() {
        this.updateInterval = setInterval(() => {
            this.updateNetworkStats();
            this.updateMempoolStatus();
            this.updateTransactionStatuses();
        }, 5000); // 每5秒更新一次
    }
    
    stopMonitoring() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
    
    async updateNetworkStats() {
        try {
            const response = await fetch('/api/blockchain/network/stats', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const result = await response.json();
            if (result.success) {
                this.networkStats = result.data;
                this.updateNetworkStatsUI();
            }
        } catch (error) {
            console.error('更新网络统计失败:', error);
        }
    }
    
    updateNetworkStatsUI() {
        document.getElementById('blockHeight').textContent = this.networkStats.block_height || '0';
        document.getElementById('gasPrice').textContent = this.networkStats.gas_price || '0';
        document.getElementById('pendingTxs').textContent = this.networkStats.pending_transactions || '0';
        document.getElementById('tps').textContent = (this.networkStats.tps || 0).toFixed(1);
    }
    
    async loadTransactionHistory() {
        try {
            const response = await fetch('/api/blockchain/transactions/history', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const result = await response.json();
            if (result.success) {
                this.transactions = result.data;
                this.renderTransactions();
            }
        } catch (error) {
            console.error('加载交易历史失败:', error);
        }
    }
    
    renderTransactions() {
        const container = document.getElementById('transactionItems');
        if (!container) return;
        
        if (this.transactions.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📊</div>
                    <h4>暂无交易记录</h4>
                    <p>发送第一笔交易来开始监控</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.transactions.map(tx => `
            <div class="transaction-card">
                <div class="transaction-header">
                    <div class="tx-hash">
                        <span class="hash-address" title="${tx.hash}">${this.truncateHash(tx.hash)}</span>
                        <button class="btn btn-sm btn-outline-secondary" onclick="this.copyToClipboard('${tx.hash}')">
                            <i class="bi bi-copy"></i>
                        </button>
                    </div>
                    <div class="tx-status">
                        <span class="confirmation-badge ${tx.status}">${this.getStatusText(tx.status)}</span>
                        ${tx.confirmations ? `<span class="block-height">${tx.confirmations}/12</span>` : ''}
                    </div>
                </div>
                <div class="transaction-details">
                    <div class="detail-row">
                        <span class="label">发送方:</span>
                        <span class="hash-address" title="${tx.from_address}">${this.truncateHash(tx.from_address)}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">接收方:</span>
                        <span class="hash-address" title="${tx.to_address}">${this.truncateHash(tx.to_address)}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">金额:</span>
                        <span class="amount">${tx.amount} ETH</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Gas费用:</span>
                        <span class="gas-info">
                            <i class="gas-icon">⛽</i>
                            ${tx.gas_fee} ETH
                        </span>
                    </div>
                    <div class="detail-row">
                        <span class="label">时间:</span>
                        <span class="timestamp">${new Date(tx.timestamp).toLocaleString()}</span>
                    </div>
                </div>
                <div class="transaction-actions">
                    <button class="btn btn-sm btn-outline-primary" onclick="this.viewTransactionDetails('${tx.hash}')">
                        查看详情
                    </button>
                    ${tx.status === 'pending' ? `
                        <button class="btn btn-sm btn-outline-warning" onclick="this.speedUpTransaction('${tx.hash}')">
                            加速交易
                        </button>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }
    
    async updateMempoolStatus() {
        try {
            const response = await fetch('/api/blockchain/transactions/mempool', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const result = await response.json();
            if (result.success) {
                this.renderMempoolVisual(result.data);
            }
        } catch (error) {
            console.error('更新内存池状态失败:', error);
        }
    }
    
    renderMempoolVisual(mempoolData) {
        const container = document.getElementById('mempoolGrid');
        if (!container) return;
        
        const maxItems = 50;
        const items = mempoolData.transactions.slice(0, maxItems);
        
        container.innerHTML = items.map((tx, index) => `
            <div class="mempool-item ${tx.status}" 
                 data-tx-hash="${tx.hash}"
                 title="Gas: ${tx.gas_price} Gwei | 金额: ${tx.amount} ETH">
                <span class="status-indicator status-${tx.status}"></span>
            </div>
        `).join('');
        
        // 如果交易数量超过显示限制，显示更多指示器
        if (mempoolData.transactions.length > maxItems) {
            const moreCount = mempoolData.transactions.length - maxItems;
            container.innerHTML += `
                <div class="mempool-more">
                    +${moreCount}
                </div>
            `;
        }
    }
    
    showSendTransactionModal() {
        const modal = new bootstrap.Modal(document.getElementById('sendTransactionModal'));
        this.updateGasEstimation();
        modal.show();
    }
    
    async sendTransaction(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const transactionData = {
            to_address: formData.get('recipientAddress'),
            amount: parseFloat(formData.get('amount')),
            gas_limit: parseInt(formData.get('gasLimit')),
            gas_price: parseInt(formData.get('gasPrice')),
            data: formData.get('txData') || null
        };
        
        try {
            const response = await fetch('/api/blockchain/transactions/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(transactionData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('sendTransactionModal'));
                modal.hide();
                
                // 重置表单
                event.target.reset();
                
                // 刷新交易列表
                await this.refreshTransactions();
                
                this.showNotification('交易已提交', 'success');
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('发送交易失败:', error);
            this.showNotification(`发送交易失败: ${error.message}`, 'error');
        }
    }
    
    async refreshTransactions() {
        await this.loadTransactionHistory();
        await this.updateNetworkStats();
        await this.updateMempoolStatus();
        this.showNotification('数据已刷新', 'info');
    }
    
    switchNetwork(network) {
        // 切换网络逻辑
        this.currentNetwork = network;
        this.refreshTransactions();
        this.showNotification(`已切换到${this.getNetworkName(network)}`, 'info');
    }
    
    filterTransactions() {
        const status = document.getElementById('statusFilter').value;
        const filteredTransactions = status 
            ? this.transactions.filter(tx => tx.status === status)
            : this.transactions;
        
        this.renderFilteredTransactions(filteredTransactions);
    }
    
    searchTransactions() {
        const query = document.getElementById('searchTx').value.toLowerCase();
        const filteredTransactions = query 
            ? this.transactions.filter(tx => tx.hash.toLowerCase().includes(query))
            : this.transactions;
        
        this.renderFilteredTransactions(filteredTransactions);
    }
    
    renderFilteredTransactions(transactions) {
        const originalTransactions = this.transactions;
        this.transactions = transactions;
        this.renderTransactions();
        this.transactions = originalTransactions;
    }
    
    updateGasEstimation() {
        const gasLimit = parseInt(document.getElementById('gasLimit').value) || 21000;
        const gasPrice = parseInt(document.getElementById('gasPrice').value) || 20;
        
        const estimatedFee = (gasLimit * gasPrice) / 1e9; // 转换为ETH
        const estimatedTime = gasPrice >= 30 ? '~1分钟' : gasPrice >= 20 ? '~2分钟' : '~5分钟';
        
        document.getElementById('estimatedFee').textContent = `${estimatedFee.toFixed(6)} ETH`;
        document.getElementById('estimatedTime').textContent = estimatedTime;
    }
    
    // 工具方法
    truncateHash(hash) {
        return `${hash.substring(0, 6)}...${hash.substring(hash.length - 4)}`;
    }
    
    getStatusText(status) {
        const statusMap = {
            pending: '待处理',
            confirmed: '已确认',
            failed: '失败',
            mining: '打包中'
        };
        return statusMap[status] || status;
    }
    
    getNetworkName(network) {
        const networkMap = {
            mainnet: '主网',
            testnet: '测试网',
            local: '本地网络'
        };
        return networkMap[network] || network;
    }
    
    showNotification(message, type) {
        // 简单的通知实现
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
    
    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('已复制到剪贴板', 'success');
        }).catch(err => {
            console.error('复制失败:', err);
        });
    }
    
    viewTransactionDetails(hash) {
        // 打开交易详情模态框或跳转到详情页面
        window.open(`/blockchain/transaction/${hash}`, '_blank');
    }
    
    speedUpTransaction(hash) {
        // 实现交易加速功能
        this.showNotification('交易加速功能开发中', 'info');
    }
    
    async updateTransactionStatuses() {
        // 更新待处理交易的状态
        const pendingTxs = this.transactions.filter(tx => tx.status === 'pending');
        
        for (const tx of pendingTxs) {
            try {
                const response = await fetch(`/api/blockchain/transactions/status/${tx.hash}`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });
                
                const result = await response.json();
                if (result.success && result.data.status !== tx.status) {
                    // 更新本地状态
                    tx.status = result.data.status;
                    tx.confirmations = result.data.confirmations;
                }
            } catch (error) {
                console.error(`更新交易状态失败 ${tx.hash}:`, error);
            }
        }
        
        this.renderTransactions();
    }
    
    destroy() {
        this.stopMonitoring();
    }
}

// 导出组件
window.TransactionMonitor = TransactionMonitor;