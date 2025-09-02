/**
 * AI模型管理组件
 * 管理模型的创建、训练、评估和部署
 */

class ModelManager {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.models = [];
        this.selectedModel = null;
        
        this.init();
    }
    
    init() {
        this.createLayout();
        this.loadModels();
    }
    
    createLayout() {
        this.container.innerHTML = `
            <div class="model-manager">
                <div class="manager-header">
                    <h3 data-i18n="ai.dashboard.model.management">模型管理</h3>
                    <div class="manager-controls">
                        <button id="createModel" class="btn btn-primary" data-i18n="ai.dashboard.model.create">创建模型</button>
                        <button id="importModel" class="btn btn-secondary" data-i18n="ai.dashboard.model.import">导入模型</button>
                        <button id="refreshModels" class="btn btn-outline-primary" data-i18n="common.refresh">刷新</button>
                    </div>
                </div>
                
                <div class="manager-filters">
                    <div class="filter-group">
                        <label for="modelTypeFilter" data-i18n="ai.dashboard.model.modelType">模型类型:</label>
                        <select id="modelTypeFilter" class="form-select">
                            <option value="" data-i18n="common.all">全部</option>
                            <option value="cnn">CNN</option>
                            <option value="rnn">RNN</option>
                            <option value="lstm">LSTM</option>
                            <option value="transformer">Transformer</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label for="statusFilter" data-i18n="ai.dashboard.model.status">状态:</label>
                        <select id="statusFilter" class="form-select">
                            <option value="" data-i18n="common.all">全部</option>
                            <option value="created" data-i18n="ai.dashboard.model.statuses.created">已创建</option>
                            <option value="training" data-i18n="ai.dashboard.model.statuses.training">训练中</option>
                            <option value="trained" data-i18n="ai.dashboard.model.statuses.trained">已训练</option>
                            <option value="deployed" data-i18n="ai.dashboard.model.statuses.deployed">已部署</option>
                        </select>
                    </div>
                </div>
                
                <div class="models-grid" id="modelsGrid"></div>
                
                <!-- 模型详情模态框 -->
                <div class="modal fade" id="modelDetailModal" tabindex="-1">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" data-i18n="ai.dashboard.model.detail">模型详情</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body" id="modelDetailContent"></div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" data-i18n="common.close">关闭</button>
                                <button type="button" class="btn btn-primary" id="trainModel" data-i18n="ai.dashboard.model.train">训练模型</button>
                                <button type="button" class="btn btn-success" id="deployModel" data-i18n="ai.dashboard.model.deploy">部署模型</button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 创建模型模态框 -->
                <div class="modal fade" id="createModelModal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" data-i18n="ai.dashboard.model.createNew">创建新模型</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <form id="createModelForm">
                                    <div class="mb-3">
                                        <label for="modelName" class="form-label" data-i18n="ai.dashboard.model.form.name">模型名称</label>
                                        <input type="text" class="form-control" id="modelName" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="modelDescription" class="form-label" data-i18n="ai.dashboard.model.form.description">描述</label>
                                        <textarea class="form-control" id="modelDescription" rows="3"></textarea>
                                    </div>
                                    <div class="mb-3">
                                        <label for="modelType" class="form-label" data-i18n="ai.dashboard.model.form.type">模型类型</label>
                                        <select class="form-select" id="modelType" required>
                                            <option value="" data-i18n="ai.dashboard.model.form.selectType">选择模型类型</option>
                                            <option value="cnn" data-i18n="ai.dashboard.model.form.cnn">CNN - 卷积神经网络</option>
                                            <option value="rnn" data-i18n="ai.dashboard.model.form.rnn">RNN - 循环神经网络</option>
                                            <option value="lstm" data-i18n="ai.dashboard.model.form.lstm">LSTM - 长短期记忆网络</option>
                                            <option value="transformer">Transformer</option>
                                            <option value="mlp" data-i18n="ai.dashboard.model.form.mlp">MLP - 多层感知器</option>
                                        </select>
                                    </div>
                                    <div class="mb-3">
                                        <label for="architecture" class="form-label" data-i18n="ai.dashboard.model.form.architecture">架构</label>
                                        <input type="text" class="form-control" id="architecture" required>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label" data-i18n="ai.dashboard.model.form.hyperparams">超参数配置</label>
                                        <div class="row">
                                            <div class="col-md-6">
                                                <label for="learningRate" class="form-label" data-i18n="ai.dashboard.model.form.learningRate">学习率</label>
                                                <input type="number" class="form-control" id="learningRate" 
                                                       value="0.001" step="0.0001" min="0.0001" max="1">
                                            </div>
                                            <div class="col-md-6">
                                                <label for="batchSize" class="form-label" data-i18n="ai.dashboard.model.form.batchSize">批次大小</label>
                                                <input type="number" class="form-control" id="batchSize" 
                                                       value="32" min="1" max="1024">
                                            </div>
                                        </div>
                                    </div>
                                </form>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" data-i18n="common.cancel">取消</button>
                                <button type="button" class="btn btn-primary" id="submitCreateModel" data-i18n="ai.dashboard.model.create">创建模型</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.bindEvents();
        
        // Apply i18n translations if available
        if (window.i18nManager) {
            window.i18nManager.applyTranslations();
        }
    }
    
    bindEvents() {
        document.getElementById('createModel').addEventListener('click', () => {
            new bootstrap.Modal(document.getElementById('createModelModal')).show();
        });
        
        document.getElementById('importModel').addEventListener('click', () => this.importModel());
        document.getElementById('refreshModels').addEventListener('click', () => this.loadModels());
        
        document.getElementById('modelTypeFilter').addEventListener('change', () => this.filterModels());
        document.getElementById('statusFilter').addEventListener('change', () => this.filterModels());
        
        document.getElementById('submitCreateModel').addEventListener('click', () => this.createModel());
        document.getElementById('trainModel').addEventListener('click', () => this.trainModel());
        document.getElementById('deployModel').addEventListener('click', () => this.deployModel());
    }
    
    async loadModels() {
        try {
            const response = await fetch('/api/ai/models/list', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.models = result.data.models;
                this.renderModels();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('加载模型列表失败:', error);
            this.showAlert('加载模型列表失败', 'error');
        }
    }
    
    renderModels() {
        const grid = document.getElementById('modelsGrid');
        
        if (this.models.length === 0) {
            grid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🤖</div>
                    <h4>暂无模型</h4>
                    <p>点击"创建模型"开始构建您的第一个模型</p>
                </div>
            `;
            return;
        }
        
        grid.innerHTML = this.models.map(model => `
            <div class="model-card" data-model-id="${model.id}">
                <div class="model-header">
                    <h5 class="model-name">${model.name}</h5>
                    <span class="model-status status-${model.status}">${this.getStatusText(model.status)}</span>
                </div>
                <div class="model-info">
                    <div class="info-item">
                        <span class="info-label">类型:</span>
                        <span class="info-value">${model.model_type}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">架构:</span>
                        <span class="info-value">${model.architecture}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">准确率:</span>
                        <span class="info-value">${(model.accuracy * 100).toFixed(2)}%</span>
                    </div>
                </div>
                <div class="model-actions">
                    <button class="btn btn-sm btn-outline-primary view-model" data-model-id="${model.id}">
                        查看详情
                    </button>
                    <button class="btn btn-sm btn-primary train-model" data-model-id="${model.id}"
                            ${model.status === 'training' ? 'disabled' : ''}>
                        ${model.status === 'training' ? '训练中' : '开始训练'}
                    </button>
                </div>
                <div class="model-footer">
                    <small class="text-muted">创建于 ${new Date(model.created_at).toLocaleString()}</small>
                </div>
            </div>
        `).join('');
        
        // 绑定模型卡片事件
        grid.querySelectorAll('.view-model').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modelId = e.target.dataset.modelId;
                this.showModelDetail(modelId);
            });
        });
        
        grid.querySelectorAll('.train-model').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modelId = e.target.dataset.modelId;
                this.quickTrainModel(modelId);
            });
        });
    }
    
    async createModel() {
        try {
            const form = document.getElementById('createModelForm');
            const formData = new FormData(form);
            
            const modelData = {
                name: formData.get('modelName') || document.getElementById('modelName').value,
                description: formData.get('modelDescription') || document.getElementById('modelDescription').value,
                model_type: formData.get('modelType') || document.getElementById('modelType').value,
                architecture: formData.get('architecture') || document.getElementById('architecture').value,
                hyperparameters: {
                    learning_rate: parseFloat(document.getElementById('learningRate').value),
                    batch_size: parseInt(document.getElementById('batchSize').value)
                }
            };
            
            const response = await fetch('/api/ai/models/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(modelData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                bootstrap.Modal.getInstance(document.getElementById('createModelModal')).hide();
                this.showAlert('模型创建成功', 'success');
                this.loadModels();
                document.getElementById('createModelForm').reset();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('创建模型失败:', error);
            this.showAlert(`创建模型失败: ${error.message}`, 'error');
        }
    }
    
    async showModelDetail(modelId) {
        try {
            const response = await fetch(`/api/ai/models/${modelId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                const model = result.data;
                this.selectedModel = model;
                this.renderModelDetail(model);
                new bootstrap.Modal(document.getElementById('modelDetailModal')).show();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('获取模型详情失败:', error);
            this.showAlert(`获取模型详情失败: ${error.message}`, 'error');
        }
    }
    
    renderModelDetail(model) {
        const content = document.getElementById('modelDetailContent');
        
        content.innerHTML = `
            <div class="model-detail">
                <div class="detail-section">
                    <h6>基本信息</h6>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <label>名称:</label>
                            <span>${model.name}</span>
                        </div>
                        <div class="detail-item">
                            <label>类型:</label>
                            <span>${model.model_type}</span>
                        </div>
                        <div class="detail-item">
                            <label>架构:</label>
                            <span>${model.architecture}</span>
                        </div>
                        <div class="detail-item">
                            <label>状态:</label>
                            <span class="status-${model.status}">${this.getStatusText(model.status)}</span>
                        </div>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h6>性能指标</h6>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">${(model.accuracy * 100).toFixed(2)}%</div>
                            <div class="metric-label">准确率</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${model.loss ? model.loss.toFixed(4) : 'N/A'}</div>
                            <div class="metric-label">损失值</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${model.precision ? (model.precision * 100).toFixed(2) + '%' : 'N/A'}</div>
                            <div class="metric-label">精确率</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${model.recall ? (model.recall * 100).toFixed(2) + '%' : 'N/A'}</div>
                            <div class="metric-label">召回率</div>
                        </div>
                    </div>
                </div>
                
                ${model.hyperparameters ? `
                <div class="detail-section">
                    <h6>超参数</h6>
                    <div class="hyperparams">
                        ${Object.entries(model.hyperparameters).map(([key, value]) => `
                            <div class="param-item">
                                <label>${key}:</label>
                                <span>${value}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}
                
                ${model.recent_sessions && model.recent_sessions.length > 0 ? `
                <div class="detail-section">
                    <h6>最近训练会话</h6>
                    <div class="sessions-list">
                        ${model.recent_sessions.map(session => `
                            <div class="session-item">
                                <div class="session-info">
                                    <span class="session-id">${session.session_id}</span>
                                    <span class="session-status status-${session.status}">${session.status}</span>
                                </div>
                                <div class="session-metrics">
                                    <span>准确率: ${(session.accuracy * 100).toFixed(2)}%</span>
                                    <span>轮次: ${session.current_round}/${session.total_rounds}</span>
                                </div>
                                <div class="session-time">
                                    ${new Date(session.created_at).toLocaleString()}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}
            </div>
        `;
    }
    
    async quickTrainModel(modelId) {
        try {
            const model = this.models.find(m => m.id == modelId);
            if (!model) return;
            
            const trainingConfig = {
                model_id: modelId,
                dataset_id: 'default_dataset',
                training_config: {
                    epochs: 10,
                    learning_rate: 0.001,
                    batch_size: 32
                }
            };
            
            const response = await fetch(`/api/ai/models/${modelId}/train`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(trainingConfig)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showAlert('模型训练已开始', 'success');
                this.loadModels();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('启动模型训练失败:', error);
            this.showAlert(`启动模型训练失败: ${error.message}`, 'error');
        }
    }
    
    filterModels() {
        const typeFilter = document.getElementById('modelTypeFilter').value;
        const statusFilter = document.getElementById('statusFilter').value;
        
        let filteredModels = this.models;
        
        if (typeFilter) {
            filteredModels = filteredModels.filter(model => model.model_type === typeFilter);
        }
        
        if (statusFilter) {
            filteredModels = filteredModels.filter(model => model.status === statusFilter);
        }
        
        // 临时保存原始数据并渲染过滤后的数据
        const originalModels = this.models;
        this.models = filteredModels;
        this.renderModels();
        this.models = originalModels;
    }
    
    getStatusText(status) {
        const statusMap = {
            'created': '已创建',
            'training': '训练中',
            'trained': '已训练',
            'deployed': '已部署',
            'error': '错误'
        };
        return statusMap[status] || status;
    }
    
    showAlert(message, type = 'info') {
        // 创建并显示警告消息
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alert.style.top = '20px';
        alert.style.right = '20px';
        alert.style.zIndex = '9999';
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
}

// 导出组件
window.ModelManager = ModelManager;