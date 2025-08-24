/**
 * 智能合约管理组件
 * 部署、管理和交互智能合约
 */

class ContractManager {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.contracts = [];
        this.templates = [];
        this.selectedContract = null;
        
        this.init();
    }
    
    init() {
        this.createLayout();
        this.bindEvents();
        this.loadInitialData();
    }
    
    createLayout() {
        this.container.innerHTML = `
            <div class="contract-manager">
                <div class="manager-header">
                    <h3>智能合约管理</h3>
                    <div class="manager-controls">
                        <button id="deployContract" class="blockchain-btn">部署合约</button>
                        <button id="importContract" class="blockchain-btn blockchain-btn-secondary">导入合约</button>
                        <button id="refreshContracts" class="btn btn-outline-secondary">
                            <i class="bi bi-arrow-clockwise"></i> 刷新
                        </button>
                    </div>
                </div>
                
                <!-- 合约模板 -->
                <div class="row mb-4">
                    <div class="col-12">
                        <div class="blockchain-card">
                            <h5>合约模板</h5>
                            <div class="template-grid" id="templateGrid">
                                <!-- 模板将动态加载 -->
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 筛选和搜索 -->
                <div class="manager-filters">
                    <div class="filter-group">
                        <label>状态筛选</label>
                        <select id="statusFilter" class="form-select">
                            <option value="">所有状态</option>
                            <option value="active">活跃</option>
                            <option value="paused">暂停</option>
                            <option value="deprecated">已弃用</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>类型筛选</label>
                        <select id="typeFilter" class="form-select">
                            <option value="">所有类型</option>
                            <option value="federated_learning">联邦学习</option>
                            <option value="privacy_protection">隐私保护</option>
                            <option value="reputation">信誉管理</option>
                            <option value="token">代币合约</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>搜索</label>
                        <input type="text" id="searchContracts" class="form-control" 
                               placeholder="搜索合约名称或地址...">
                    </div>
                </div>
                
                <!-- 合约列表 -->
                <div class="contracts-grid" id="contractsGrid">
                    <!-- 合约卡片将动态生成 -->
                </div>
            </div>
            
            <!-- 部署合约模态框 -->
            <div class="modal fade" id="deployContractModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">部署智能合约</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <form id="deployForm">
                                        <div class="mb-3">
                                            <label class="form-label">合约名称</label>
                                            <input type="text" class="form-control" id="contractName" required>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">合约类型</label>
                                            <select class="form-select" id="contractType" required>
                                                <option value="">选择合约类型</option>
                                                <option value="federated_learning">联邦学习合约</option>
                                                <option value="privacy_protection">隐私保护合约</option>
                                                <option value="reputation">信誉管理合约</option>
                                                <option value="token">代币合约</option>
                                            </select>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">构造函数参数</label>
                                            <div id="constructorParams">
                                                <!-- 动态生成参数输入框 -->
                                            </div>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Gas限制</label>
                                            <input type="number" class="form-control" id="deployGasLimit" 
                                                   value="3000000" min="21000">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Gas价格 (Gwei)</label>
                                            <input type="number" class="form-control" id="deployGasPrice" 
                                                   value="20" min="1">
                                        </div>
                                    </form>
                                </div>
                                <div class="col-md-6">
                                    <div class="contract-preview">
                                        <h6>合约预览</h6>
                                        <div class="code-preview" id="contractPreview">
                                            <pre><code class="language-solidity">// 选择合约类型查看代码预览</code></pre>
                                        </div>
                                    </div>
                                    <div class="deployment-estimate">
                                        <div class="alert alert-info">
                                            <strong>部署预估:</strong><br>
                                            Gas费用: <span id="deploymentCost">0.06 ETH</span><br>
                                            预计时间: <span id="deploymentTime">~3分钟</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="submit" form="deployForm" class="blockchain-btn">部署合约</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 合约详情模态框 -->
            <div class="modal fade" id="contractDetailModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="contractDetailTitle">合约详情</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <!-- 合约基本信息 -->
                                    <div class="detail-section">
                                        <h6>基本信息</h6>
                                        <div class="detail-grid" id="contractBasicInfo">
                                            <!-- 动态生成 -->
                                        </div>
                                    </div>
                                    
                                    <!-- 合约函数 -->
                                    <div class="detail-section">
                                        <h6>合约函数</h6>
                                        <div class="function-list" id="contractFunctions">
                                            <!-- 动态生成 -->
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <!-- 合约事件 -->
                                    <div class="detail-section">
                                        <h6>最近事件</h6>
                                        <div class="event-list" id="contractEvents">
                                            <!-- 动态生成 -->
                                        </div>
                                    </div>
                                    
                                    <!-- 合约状态 -->
                                    <div class="detail-section">
                                        <h6>合约状态</h6>
                                        <div class="state-variables" id="contractState">
                                            <!-- 动态生成 -->
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                            <button type="button" class="blockchain-btn" onclick="this.openContractInteraction()">
                                与合约交互
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 函数调用模态框 -->
            <div class="modal fade" id="functionCallModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="functionCallTitle">调用合约函数</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="functionCallForm">
                                <div class="mb-3">
                                    <label class="form-label">函数</label>
                                    <select class="form-select" id="functionSelect" required>
                                        <option value="">选择要调用的函数</option>
                                    </select>
                                </div>
                                <div id="functionParameters">
                                    <!-- 动态生成函数参数 -->
                                </div>
                                <div class="mb-3" id="transactionValue" style="display: none;">
                                    <label class="form-label">发送金额 (ETH)</label>
                                    <input type="number" class="form-control" id="ethValue" 
                                           value="0" min="0" step="0.001">
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">Gas限制</label>
                                            <input type="number" class="form-control" id="callGasLimit" 
                                                   value="200000" min="21000">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">Gas价格 (Gwei)</label>
                                            <input type="number" class="form-control" id="callGasPrice" 
                                                   value="20" min="1">
                                        </div>
                                    </div>
                                </div>
                            </form>
                            <div class="function-result" id="functionResult" style="display: none;">
                                <h6>调用结果</h6>
                                <div class="result-content"></div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="submit" form="functionCallForm" class="blockchain-btn">
                                调用函数
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    bindEvents() {
        document.getElementById('deployContract').addEventListener('click', () => this.showDeployModal());
        document.getElementById('importContract').addEventListener('click', () => this.showImportModal());
        document.getElementById('refreshContracts').addEventListener('click', () => this.refreshContracts());
        
        document.getElementById('statusFilter').addEventListener('change', () => this.filterContracts());
        document.getElementById('typeFilter').addEventListener('change', () => this.filterContracts());
        document.getElementById('searchContracts').addEventListener('input', () => this.searchContracts());
        
        const deployForm = document.getElementById('deployForm');
        if (deployForm) {
            deployForm.addEventListener('submit', (e) => this.deployContract(e));
        }
        
        const contractTypeSelect = document.getElementById('contractType');
        if (contractTypeSelect) {
            contractTypeSelect.addEventListener('change', (e) => this.updateContractPreview(e.target.value));
        }
        
        const functionCallForm = document.getElementById('functionCallForm');
        if (functionCallForm) {
            functionCallForm.addEventListener('submit', (e) => this.callContractFunction(e));
        }
        
        const functionSelect = document.getElementById('functionSelect');
        if (functionSelect) {
            functionSelect.addEventListener('change', (e) => this.updateFunctionParameters(e.target.value));
        }
    }
    
    async loadInitialData() {
        try {
            // 加载合约模板
            await this.loadContractTemplates();
            
            // 加载已部署的合约
            await this.loadContracts();
        } catch (error) {
            console.error('加载初始数据失败:', error);
        }
    }
    
    async loadContractTemplates() {
        try {
            const response = await fetch('/api/blockchain/contracts/templates', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const result = await response.json();
            if (result.success) {
                this.templates = result.data;
                this.renderTemplates();
            }
        } catch (error) {
            console.error('加载合约模板失败:', error);
        }
    }
    
    renderTemplates() {
        const container = document.getElementById('templateGrid');
        if (!container) return;
        
        container.innerHTML = this.templates.map(template => `
            <div class="template-card" onclick="this.selectTemplate('${template.type}')">
                <div class="template-icon">
                    ${this.getTemplateIcon(template.type)}
                </div>
                <h6>${template.name}</h6>
                <p>${template.description}</p>
                <div class="template-stats">
                    <span class="badge bg-secondary">${template.complexity}</span>
                    <span class="badge bg-info">${template.gas_estimate} Gas</span>
                </div>
            </div>
        `).join('');
    }
    
    async loadContracts() {
        try {
            const response = await fetch('/api/blockchain/contracts', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const result = await response.json();
            if (result.success) {
                this.contracts = result.data;
                this.renderContracts();
            }
        } catch (error) {
            console.error('加载合约失败:', error);
        }
    }
    
    renderContracts() {
        const container = document.getElementById('contractsGrid');
        if (!container) return;
        
        if (this.contracts.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📄</div>
                    <h4>暂无智能合约</h4>
                    <p>部署您的第一个智能合约</p>
                    <button class="blockchain-btn" onclick="this.showDeployModal()">部署合约</button>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.contracts.map(contract => `
            <div class="contract-card">
                <div class="contract-header">
                    <div class="contract-info">
                        <h5 class="contract-name">${contract.name}</h5>
                        <div class="contract-type">
                            <span class="badge bg-primary">${this.getContractTypeText(contract.type)}</span>
                        </div>
                    </div>
                    <div class="contract-status">
                        <span class="status-indicator status-${contract.status}"></span>
                        <span class="status-text">${this.getStatusText(contract.status)}</span>
                    </div>
                </div>
                
                <div class="contract-info">
                    <div class="info-item">
                        <span class="info-label">合约地址:</span>
                        <span class="hash-address" title="${contract.address}">
                            ${this.truncateAddress(contract.address)}
                        </span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">部署时间:</span>
                        <span class="info-value">${new Date(contract.created_at).toLocaleDateString()}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">交易次数:</span>
                        <span class="info-value">${contract.transaction_count}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">最后活动:</span>
                        <span class="info-value">${contract.last_activity ? new Date(contract.last_activity).toLocaleString() : '无'}</span>
                    </div>
                </div>
                
                <div class="contract-actions">
                    <button class="btn btn-sm btn-outline-primary" 
                            onclick="this.viewContractDetails('${contract.id}')">
                        查看详情
                    </button>
                    <button class="btn btn-sm btn-outline-success" 
                            onclick="this.interactWithContract('${contract.id}')">
                        交互
                    </button>
                    ${contract.status === 'active' ? `
                        <div class="dropdown">
                            <button class="btn btn-sm btn-outline-secondary dropdown-toggle" 
                                    data-bs-toggle="dropdown">
                                更多
                            </button>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" onclick="this.pauseContract('${contract.id}')">暂停合约</a></li>
                                <li><a class="dropdown-item" onclick="this.upgradeContract('${contract.id}')">升级合约</a></li>
                                <li><a class="dropdown-item" onclick="this.exportContract('${contract.id}')">导出ABI</a></li>
                            </ul>
                        </div>
                    ` : ''}
                </div>
                
                <div class="contract-footer">
                    <div class="gas-info">
                        <small>平均Gas: ${contract.avg_gas_used || 0}</small>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    showDeployModal() {
        const modal = new bootstrap.Modal(document.getElementById('deployContractModal'));
        modal.show();
    }
    
    updateContractPreview(contractType) {
        const template = this.templates.find(t => t.type === contractType);
        if (!template) return;
        
        const preview = document.getElementById('contractPreview');
        const constructorParams = document.getElementById('constructorParams');
        
        // 更新代码预览
        preview.innerHTML = `<pre><code class="language-solidity">${template.code}</code></pre>`;
        
        // 更新构造函数参数
        if (template.constructor_params) {
            constructorParams.innerHTML = template.constructor_params.map((param, index) => `
                <div class="mb-2">
                    <label class="form-label">${param.name} (${param.type})</label>
                    <input type="text" class="form-control" 
                           name="param_${index}" 
                           placeholder="${param.description}" 
                           required>
                </div>
            `).join('');
        } else {
            constructorParams.innerHTML = '<p class="text-muted">此合约无构造函数参数</p>';
        }
        
        // 更新部署预估
        this.updateDeploymentEstimate(template);
    }
    
    updateDeploymentEstimate(template) {
        const gasLimit = parseInt(document.getElementById('deployGasLimit').value) || 3000000;
        const gasPrice = parseInt(document.getElementById('deployGasPrice').value) || 20;
        
        const estimatedCost = (gasLimit * gasPrice) / 1e9; // 转换为ETH
        const estimatedTime = gasPrice >= 30 ? '~2分钟' : gasPrice >= 20 ? '~3分钟' : '~5分钟';
        
        document.getElementById('deploymentCost').textContent = `${estimatedCost.toFixed(4)} ETH`;
        document.getElementById('deploymentTime').textContent = estimatedTime;
    }
    
    async deployContract(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const contractData = {
            name: formData.get('contractName'),
            type: formData.get('contractType'),
            gas_limit: parseInt(formData.get('deployGasLimit')),
            gas_price: parseInt(formData.get('deployGasPrice')),
            constructor_params: this.getConstructorParams(formData)
        };
        
        try {
            const response = await fetch('/api/blockchain/contracts/deploy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(contractData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('deployContractModal'));
                modal.hide();
                
                // 重置表单
                event.target.reset();
                
                // 刷新合约列表
                await this.refreshContracts();
                
                this.showNotification('合约部署成功', 'success');
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('部署合约失败:', error);
            this.showNotification(`部署合约失败: ${error.message}`, 'error');
        }
    }
    
    async viewContractDetails(contractId) {
        try {
            const response = await fetch(`/api/blockchain/contracts/${contractId}/details`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const result = await response.json();
            if (result.success) {
                this.showContractDetails(result.data);
            }
        } catch (error) {
            console.error('获取合约详情失败:', error);
        }
    }
    
    showContractDetails(contractData) {
        const modal = new bootstrap.Modal(document.getElementById('contractDetailModal'));
        
        // 更新标题
        document.getElementById('contractDetailTitle').textContent = `${contractData.name} - 详情`;
        
        // 更新基本信息
        const basicInfo = document.getElementById('contractBasicInfo');
        basicInfo.innerHTML = `
            <div class="detail-item">
                <label>合约地址</label>
                <span class="hash-address">${contractData.address}</span>
            </div>
            <div class="detail-item">
                <label>合约类型</label>
                <span>${this.getContractTypeText(contractData.type)}</span>
            </div>
            <div class="detail-item">
                <label>状态</label>
                <span class="status-${contractData.status}">${this.getStatusText(contractData.status)}</span>
            </div>
            <div class="detail-item">
                <label>部署时间</label>
                <span>${new Date(contractData.created_at).toLocaleString()}</span>
            </div>
            <div class="detail-item">
                <label>创建者</label>
                <span class="hash-address">${contractData.creator}</span>
            </div>
        `;
        
        // 更新函数列表
        this.updateContractFunctions(contractData);
        
        // 更新事件列表
        this.updateContractEvents(contractData);
        
        // 更新合约状态
        this.updateContractState(contractData);
        
        this.selectedContract = contractData;
        modal.show();
    }
    
    updateContractFunctions(contractData) {
        const container = document.getElementById('contractFunctions');
        if (!contractData.functions || contractData.functions.length === 0) {
            container.innerHTML = '<p class="text-muted">暂无可调用函数</p>';
            return;
        }
        
        container.innerHTML = contractData.functions.map(func => `
            <div class="function-item">
                <div class="function-header">
                    <span class="function-name">${func.name}</span>
                    <span class="badge bg-${func.type === 'view' ? 'info' : func.type === 'payable' ? 'warning' : 'secondary'}">
                        ${func.type}
                    </span>
                </div>
                <div class="function-params">
                    ${func.inputs ? func.inputs.map(input => `
                        <span class="param-badge">${input.name}: ${input.type}</span>
                    `).join('') : ''}
                </div>
            </div>
        `).join('');
    }
    
    updateContractEvents(contractData) {
        const container = document.getElementById('contractEvents');
        if (!contractData.recent_events || contractData.recent_events.length === 0) {
            container.innerHTML = '<p class="text-muted">暂无事件记录</p>';
            return;
        }
        
        container.innerHTML = contractData.recent_events.map(event => `
            <div class="event-item">
                <div class="event-header">
                    <span class="event-name">${event.name}</span>
                    <span class="event-time">${new Date(event.timestamp).toLocaleString()}</span>
                </div>
                <div class="event-data">
                    ${Object.entries(event.data).map(([key, value]) => `
                        <div class="event-param">
                            <strong>${key}:</strong> ${value}
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('');
    }
    
    updateContractState(contractData) {
        const container = document.getElementById('contractState');
        if (!contractData.state_variables || contractData.state_variables.length === 0) {
            container.innerHTML = '<p class="text-muted">暂无状态变量</p>';
            return;
        }
        
        container.innerHTML = contractData.state_variables.map(variable => `
            <div class="state-item">
                <div class="state-name">${variable.name}</div>
                <div class="state-value">${variable.value}</div>
                <div class="state-type">${variable.type}</div>
            </div>
        `).join('');
    }
    
    interactWithContract(contractId) {
        const contract = this.contracts.find(c => c.id === contractId);
        if (!contract) return;
        
        this.selectedContract = contract;
        this.showFunctionCallModal();
    }
    
    async showFunctionCallModal() {
        if (!this.selectedContract) return;
        
        // 获取合约ABI
        try {
            const response = await fetch(`/api/blockchain/contracts/${this.selectedContract.id}/abi`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const result = await response.json();
            if (result.success) {
                this.populateFunctionSelect(result.data.functions);
                
                const modal = new bootstrap.Modal(document.getElementById('functionCallModal'));
                modal.show();
            }
        } catch (error) {
            console.error('获取合约ABI失败:', error);
        }
    }
    
    populateFunctionSelect(functions) {
        const select = document.getElementById('functionSelect');
        select.innerHTML = '<option value="">选择要调用的函数</option>' +
            functions.map(func => `
                <option value="${func.name}" data-type="${func.type}">${func.name} (${func.type})</option>
            `).join('');
    }
    
    updateFunctionParameters(functionName) {
        // 这里应该根据选择的函数更新参数输入框
        const container = document.getElementById('functionParameters');
        const valueField = document.getElementById('transactionValue');
        
        // 模拟函数参数（实际应该从ABI获取）
        if (functionName) {
            container.innerHTML = `
                <div class="mb-3">
                    <label class="form-label">参数示例</label>
                    <input type="text" class="form-control" placeholder="根据函数定义输入参数">
                </div>
            `;
            
            // 如果是payable函数，显示金额输入框
            const option = document.querySelector(`#functionSelect option[value="${functionName}"]`);
            if (option && option.dataset.type === 'payable') {
                valueField.style.display = 'block';
            } else {
                valueField.style.display = 'none';
            }
        } else {
            container.innerHTML = '';
            valueField.style.display = 'none';
        }
    }
    
    async callContractFunction(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const callData = {
            contract_id: this.selectedContract.id,
            function_name: formData.get('functionSelect'),
            parameters: this.getFunctionParameters(formData),
            value: parseFloat(formData.get('ethValue')) || 0,
            gas_limit: parseInt(formData.get('callGasLimit')),
            gas_price: parseInt(formData.get('callGasPrice'))
        };
        
        try {
            const response = await fetch('/api/blockchain/contracts/call', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(callData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showFunctionResult(result.data);
                this.showNotification('函数调用成功', 'success');
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('调用函数失败:', error);
            this.showNotification(`调用函数失败: ${error.message}`, 'error');
        }
    }
    
    showFunctionResult(resultData) {
        const container = document.getElementById('functionResult');
        const content = container.querySelector('.result-content');
        
        content.innerHTML = `
            <div class="alert alert-success">
                <strong>调用成功!</strong><br>
                交易哈希: <span class="hash-address">${resultData.transaction_hash}</span><br>
                ${resultData.return_value ? `返回值: ${JSON.stringify(resultData.return_value)}` : ''}
            </div>
        `;
        
        container.style.display = 'block';
    }
    
    // 筛选和搜索方法
    filterContracts() {
        const status = document.getElementById('statusFilter').value;
        const type = document.getElementById('typeFilter').value;
        
        let filtered = this.contracts;
        
        if (status) {
            filtered = filtered.filter(contract => contract.status === status);
        }
        
        if (type) {
            filtered = filtered.filter(contract => contract.type === type);
        }
        
        this.renderFilteredContracts(filtered);
    }
    
    searchContracts() {
        const query = document.getElementById('searchContracts').value.toLowerCase();
        
        const filtered = query 
            ? this.contracts.filter(contract => 
                contract.name.toLowerCase().includes(query) ||
                contract.address.toLowerCase().includes(query)
              )
            : this.contracts;
        
        this.renderFilteredContracts(filtered);
    }
    
    renderFilteredContracts(contracts) {
        const originalContracts = this.contracts;
        this.contracts = contracts;
        this.renderContracts();
        this.contracts = originalContracts;
    }
    
    async refreshContracts() {
        await this.loadContracts();
        this.showNotification('合约列表已刷新', 'info');
    }
    
    // 工具方法
    getTemplateIcon(type) {
        const icons = {
            federated_learning: '🤖',
            privacy_protection: '🔒',
            reputation: '⭐',
            token: '🪙'
        };
        return icons[type] || '📄';
    }
    
    getContractTypeText(type) {
        const types = {
            federated_learning: '联邦学习',
            privacy_protection: '隐私保护',
            reputation: '信誉管理',
            token: '代币合约'
        };
        return types[type] || type;
    }
    
    getStatusText(status) {
        const statuses = {
            active: '活跃',
            paused: '暂停',
            deprecated: '已弃用'
        };
        return statuses[status] || status;
    }
    
    truncateAddress(address) {
        return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
    }
    
    getConstructorParams(formData) {
        const params = [];
        let index = 0;
        
        while (formData.get(`param_${index}`) !== null) {
            params.push(formData.get(`param_${index}`));
            index++;
        }
        
        return params;
    }
    
    getFunctionParameters(formData) {
        // 简化处理，实际应该根据ABI解析参数
        return [];
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
    
    selectTemplate(templateType) {
        document.getElementById('contractType').value = templateType;
        this.updateContractPreview(templateType);
        this.showDeployModal();
    }
    
    destroy() {
        // 清理资源
    }
}

// 导出组件
window.ContractManager = ContractManager;