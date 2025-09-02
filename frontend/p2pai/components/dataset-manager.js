/**
 * AI数据集管理组件
 * 管理数据集的上传、分析、预览和管理
 */

class DatasetManager {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.datasets = [];
        this.selectedDataset = null;
        
        this.init();
    }
    
    init() {
        this.createLayout();
        this.loadDatasets();
    }
    
    createLayout() {
        this.container.innerHTML = `
            <div class="dataset-manager">
                <div class="manager-header">
                    <h3 data-i18n="ai.dashboard.dataset.management">数据集管理</h3>
                    <div class="manager-controls">
                        <button id="uploadDataset" class="btn btn-primary" data-i18n="ai.dashboard.dataset.upload">上传数据集</button>
                        <button id="createDataset" class="btn btn-secondary" data-i18n="ai.dashboard.dataset.create">创建数据集</button>
                        <button id="refreshDatasets" class="btn btn-outline-primary" data-i18n="common.refresh">刷新</button>
                    </div>
                </div>
                
                <div class="manager-filters">
                    <div class="filter-group">
                        <label for="dataTypeFilter" data-i18n="ai.dashboard.dataset.dataType">数据类型:</label>
                        <select id="dataTypeFilter" class="form-select">
                            <option value="" data-i18n="common.all">全部</option>
                            <option value="image" data-i18n="ai.dashboard.dataset.types.image">图像</option>
                            <option value="text" data-i18n="ai.dashboard.dataset.types.text">文本</option>
                            <option value="tabular" data-i18n="ai.dashboard.dataset.types.tabular">表格</option>
                            <option value="audio" data-i18n="ai.dashboard.dataset.types.audio">音频</option>
                            <option value="time_series" data-i18n="ai.dashboard.dataset.types.timeSeries">时间序列</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label for="statusFilter" data-i18n="ai.dashboard.dataset.status">状态:</label>
                        <select id="statusFilter" class="form-select">
                            <option value="" data-i18n="common.all">全部</option>
                            <option value="created" data-i18n="ai.dashboard.dataset.statuses.created">已创建</option>
                            <option value="processing" data-i18n="ai.dashboard.dataset.statuses.processing">处理中</option>
                            <option value="ready" data-i18n="ai.dashboard.dataset.statuses.ready">就绪</option>
                            <option value="error" data-i18n="ai.dashboard.dataset.statuses.error">错误</option>
                        </select>
                    </div>
                </div>
                
                <div class="datasets-grid" id="datasetsGrid"></div>
                
                <!-- 数据集详情模态框 -->
                <div class="modal fade" id="datasetDetailModal" tabindex="-1">
                    <div class="modal-dialog modal-xl">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" data-i18n="ai.dashboard.dataset.detail">数据集详情</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body" id="datasetDetailContent"></div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" data-i18n="common.close">关闭</button>
                                <button type="button" class="btn btn-info" id="previewDataset" data-i18n="ai.dashboard.dataset.preview">预览数据</button>
                                <button type="button" class="btn btn-primary" id="analyzeDataset" data-i18n="ai.dashboard.dataset.analyze">分析数据集</button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 上传数据集模态框 -->
                <div class="modal fade" id="uploadDatasetModal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" data-i18n="ai.dashboard.dataset.uploadTitle">上传数据集</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <form id="uploadDatasetForm">
                                    <div class="mb-3">
                                        <label for="datasetName" class="form-label" data-i18n="ai.dashboard.dataset.form.name">数据集名称</label>
                                        <input type="text" class="form-control" id="datasetName" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="datasetDescription" class="form-label" data-i18n="ai.dashboard.dataset.form.description">描述</label>
                                        <textarea class="form-control" id="datasetDescription" rows="3"></textarea>
                                    </div>
                                    <div class="mb-3">
                                        <label for="datasetType" class="form-label" data-i18n="ai.dashboard.dataset.form.type">数据类型</label>
                                        <select class="form-select" id="datasetType" required>
                                            <option value="" data-i18n="ai.dashboard.dataset.form.selectType">选择数据类型</option>
                                            <option value="image" data-i18n="ai.dashboard.dataset.form.imageData">图像数据</option>
                                            <option value="text" data-i18n="ai.dashboard.dataset.form.textData">文本数据</option>
                                            <option value="tabular" data-i18n="ai.dashboard.dataset.form.tabularData">表格数据</option>
                                            <option value="audio" data-i18n="ai.dashboard.dataset.form.audioData">音频数据</option>
                                            <option value="time_series" data-i18n="ai.dashboard.dataset.form.timeSeriesData">时间序列</option>
                                        </select>
                                    </div>
                                    <div class="mb-3">
                                        <label for="datasetFile" class="form-label" data-i18n="ai.dashboard.dataset.form.file">数据文件</label>
                                        <input type="file" class="form-control" id="datasetFile" 
                                               accept=".csv,.json,.xlsx,.zip,.tar.gz" required>
                                        <div class="form-text">
                                            <span data-i18n="ai.dashboard.dataset.form.supportedFormats">支持格式: CSV, JSON, Excel, ZIP, TAR.GZ (最大100MB)</span>
                                        </div>
                                    </div>
                                    <div class="mb-3">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" id="autoAnalyze" checked>
                                            <label class="form-check-label" for="autoAnalyze">
                                                <span data-i18n="ai.dashboard.dataset.form.autoAnalyze">上传后自动分析</span>
                                            </label>
                                        </div>
                                    </div>
                                </form>
                                
                                <!-- 上传进度 -->
                                <div id="uploadProgress" class="mt-3" style="display: none;">
                                    <div class="progress">
                                        <div class="progress-bar" role="progressbar" style="width: 0%"></div>
                                    </div>
                                    <small class="text-muted mt-1" data-i18n="ai.dashboard.dataset.form.uploading">正在上传...</small>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" data-i18n="common.cancel">取消</button>
                                <button type="button" class="btn btn-primary" id="submitUploadDataset" data-i18n="ai.dashboard.dataset.upload">上传数据集</button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 数据预览模态框 -->
                <div class="modal fade" id="dataPreviewModal" tabindex="-1">
                    <div class="modal-dialog modal-xl">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" data-i18n="ai.dashboard.dataset.dataPreview">数据预览</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body" id="dataPreviewContent"></div>
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
        document.getElementById('uploadDataset').addEventListener('click', () => {
            new bootstrap.Modal(document.getElementById('uploadDatasetModal')).show();
        });
        
        document.getElementById('createDataset').addEventListener('click', () => this.createDataset());
        document.getElementById('refreshDatasets').addEventListener('click', () => this.loadDatasets());
        
        document.getElementById('dataTypeFilter').addEventListener('change', () => this.filterDatasets());
        document.getElementById('statusFilter').addEventListener('change', () => this.filterDatasets());
        
        document.getElementById('submitUploadDataset').addEventListener('click', () => this.uploadDataset());
        document.getElementById('previewDataset').addEventListener('click', () => this.previewDataset());
        document.getElementById('analyzeDataset').addEventListener('click', () => this.analyzeDataset());
    }
    
    async loadDatasets() {
        try {
            const response = await fetch('/api/ai/datasets/list', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.datasets = result.data.datasets;
                this.renderDatasets();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('加载数据集列表失败:', error);
            this.showAlert('加载数据集列表失败', 'error');
        }
    }
    
    renderDatasets() {
        const grid = document.getElementById('datasetsGrid');
        
        if (this.datasets.length === 0) {
            grid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📊</div>
                    <h4 data-i18n="ai.dashboard.dataset.noDatasets">暂无数据集</h4>
                    <p data-i18n="ai.dashboard.dataset.noDatasetsTip">点击"上传数据集"开始添加您的训练数据</p>
                </div>
            `;
            return;
        }
        
        grid.innerHTML = this.datasets.map(dataset => `
            <div class="dataset-card" data-dataset-id="${dataset.id}">
                <div class="dataset-header">
                    <h5 class="dataset-name">${dataset.name}</h5>
                    <span class="dataset-status status-${dataset.status}">${this.getStatusText(dataset.status)}</span>
                </div>
                <div class="dataset-info">
                    <div class="info-item">
                        <span class="info-label" data-i18n="ai.dashboard.dataset.labels.type">类型:</span>
                        <span class="info-value">${this.getDataTypeText(dataset.data_type)}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label" data-i18n="ai.dashboard.dataset.labels.samples">样本数:</span>
                        <span class="info-value">${dataset.total_samples.toLocaleString()}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label" data-i18n="ai.dashboard.dataset.labels.features">特征数:</span>
                        <span class="info-value">${dataset.feature_count}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label" data-i18n="ai.dashboard.dataset.labels.size">大小:</span>
                        <span class="info-value">${this.formatFileSize(dataset.file_size)}</span>
                    </div>
                </div>
                ${dataset.status === 'processing' ? `
                <div class="dataset-progress">
                    <div class="progress">
                        <div class="progress-bar" style="width: ${dataset.processing_progress || 0}%"></div>
                    </div>
                    <small><span data-i18n="ai.dashboard.dataset.processing">处理中</span> ${dataset.processing_progress || 0}%</small>
                </div>
                ` : ''}
                <div class="dataset-actions">
                    <button class="btn btn-sm btn-outline-primary view-dataset" data-dataset-id="${dataset.id}">
                        <span data-i18n="ai.dashboard.dataset.viewDetails">查看详情</span>
                    </button>
                    <button class="btn btn-sm btn-info preview-dataset" data-dataset-id="${dataset.id}"
                            ${dataset.status !== 'ready' ? 'disabled' : ''}>
                        <span data-i18n="ai.dashboard.dataset.previewData">预览数据</span>
                    </button>
                </div>
                <div class="dataset-footer">
                    <small class="text-muted"><span data-i18n="ai.dashboard.dataset.createdOn">创建于</span> ${new Date(dataset.created_at).toLocaleString()}</small>
                </div>
            </div>
        `).join('');
        
        // 绑定数据集卡片事件
        grid.querySelectorAll('.view-dataset').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const datasetId = e.target.dataset.datasetId;
                this.showDatasetDetail(datasetId);
            });
        });
        
        grid.querySelectorAll('.preview-dataset').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const datasetId = e.target.dataset.datasetId;
                this.quickPreviewDataset(datasetId);
            });
        });
    }
    
    async uploadDataset() {
        try {
            const form = document.getElementById('uploadDatasetForm');
            const fileInput = document.getElementById('datasetFile');
            const file = fileInput.files[0];
            
            if (!file) {
                throw new Error('请选择要上传的文件');
            }
            
            // 显示上传进度
            const progressContainer = document.getElementById('uploadProgress');
            const progressBar = progressContainer.querySelector('.progress-bar');
            const submitBtn = document.getElementById('submitUploadDataset');
            
            progressContainer.style.display = 'block';
            submitBtn.disabled = true;
            
            const formData = new FormData();
            formData.append('file', file);
            formData.append('name', document.getElementById('datasetName').value);
            formData.append('description', document.getElementById('datasetDescription').value);
            formData.append('data_type', document.getElementById('datasetType').value);
            
            const xhr = new XMLHttpRequest();
            
            xhr.upload.onprogress = (e) => {
                if (e.lengthComputable) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    progressBar.style.width = percentComplete + '%';
                }
            };
            
            xhr.onload = () => {
                if (xhr.status === 200 || xhr.status === 201) {
                    const result = JSON.parse(xhr.responseText);
                    if (result.success) {
                        bootstrap.Modal.getInstance(document.getElementById('uploadDatasetModal')).hide();
                        this.showAlert('数据集上传成功', 'success');
                        this.loadDatasets();
                        form.reset();
                    } else {
                        throw new Error(result.message);
                    }
                } else {
                    throw new Error('上传失败');
                }
                
                progressContainer.style.display = 'none';
                submitBtn.disabled = false;
            };
            
            xhr.onerror = () => {
                this.showAlert('上传失败', 'error');
                progressContainer.style.display = 'none';
                submitBtn.disabled = false;
            };
            
            xhr.open('POST', '/api/ai/datasets/upload');
            xhr.setRequestHeader('Authorization', `Bearer ${localStorage.getItem('token')}`);
            xhr.send(formData);
            
        } catch (error) {
            console.error('上传数据集失败:', error);
            this.showAlert(`上传数据集失败: ${error.message}`, 'error');
            
            document.getElementById('uploadProgress').style.display = 'none';
            document.getElementById('submitUploadDataset').disabled = false;
        }
    }
    
    async showDatasetDetail(datasetId) {
        try {
            const response = await fetch(`/api/ai/datasets/${datasetId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                const dataset = result.data;
                this.selectedDataset = dataset;
                this.renderDatasetDetail(dataset);
                new bootstrap.Modal(document.getElementById('datasetDetailModal')).show();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('获取数据集详情失败:', error);
            this.showAlert(`获取数据集详情失败: ${error.message}`, 'error');
        }
    }
    
    renderDatasetDetail(dataset) {
        const content = document.getElementById('datasetDetailContent');
        
        content.innerHTML = `
            <div class="dataset-detail">
                <div class="row">
                    <div class="col-md-6">
                        <div class="detail-section">
                            <h6 data-i18n="ai.dashboard.dataset.detail.basicInfo">基本信息</h6>
                            <div class="detail-grid">
                                <div class="detail-item">
                                    <label data-i18n="ai.dashboard.dataset.detail.name">名称:</label>
                                    <span>${dataset.name}</span>
                                </div>
                                <div class="detail-item">
                                    <label data-i18n="ai.dashboard.dataset.detail.dataType">数据类型:</label>
                                    <span>${this.getDataTypeText(dataset.data_type)}</span>
                                </div>
                                <div class="detail-item">
                                    <label data-i18n="ai.dashboard.dataset.detail.status">状态:</label>
                                    <span class="status-${dataset.status}">${this.getStatusText(dataset.status)}</span>
                                </div>
                                <div class="detail-item">
                                    <label data-i18n="ai.dashboard.dataset.detail.fileSize">文件大小:</label>
                                    <span>${this.formatFileSize(dataset.file_size)}</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="detail-section">
                            <h6 data-i18n="ai.dashboard.dataset.detail.dataStats">数据统计</h6>
                            <div class="stats-grid">
                                <div class="stat-card">
                                    <div class="stat-value">${dataset.total_samples.toLocaleString()}</div>
                                    <div class="stat-label" data-i18n="ai.dashboard.dataset.detail.totalSamples">总样本数</div>
                                </div>
                                <div class="stat-card">
                                    <div class="stat-value">${dataset.feature_count}</div>
                                    <div class="stat-label" data-i18n="ai.dashboard.dataset.detail.featureCount">特征数量</div>
                                </div>
                                <div class="stat-card">
                                    <div class="stat-value">${dataset.class_count}</div>
                                    <div class="stat-label" data-i18n="ai.dashboard.dataset.detail.classCount">类别数量</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-6">
                        ${dataset.data_summary ? `
                        <div class="detail-section">
                            <h6>数据划分</h6>
                            <div class="split-info">
                                <div class="split-item">
                                    <label>训练集:</label>
                                    <span>${dataset.split_info ? (dataset.split_info.train_samples.toLocaleString() + ' (' + (dataset.split_info.train_split * 100).toFixed(0) + '%)') : 'N/A'}</span>
                                </div>
                                <div class="split-item">
                                    <label>验证集:</label>
                                    <span>${dataset.split_info ? (dataset.split_info.val_samples.toLocaleString() + ' (' + (dataset.split_info.val_split * 100).toFixed(0) + '%)') : 'N/A'}</span>
                                </div>
                                <div class="split-item">
                                    <label>测试集:</label>
                                    <span>${dataset.split_info ? (dataset.split_info.test_samples.toLocaleString() + ' (' + (dataset.split_info.test_split * 100).toFixed(0) + '%)') : 'N/A'}</span>
                                </div>
                            </div>
                        </div>
                        ` : ''}
                        
                        ${dataset.quality_summary ? `
                        <div class="detail-section">
                            <h6>数据质量</h6>
                            <div class="quality-metrics">
                                ${dataset.quality_summary.individual_scores.completeness !== null ? `
                                <div class="quality-item">
                                    <label>完整性:</label>
                                    <div class="quality-bar">
                                        <div class="quality-fill" style="width: ${dataset.quality_summary.individual_scores.completeness}%"></div>
                                        <span>${dataset.quality_summary.individual_scores.completeness.toFixed(1)}%</span>
                                    </div>
                                </div>
                                ` : ''}
                                ${dataset.quality_summary.individual_scores.consistency !== null ? `
                                <div class="quality-item">
                                    <label>一致性:</label>
                                    <div class="quality-bar">
                                        <div class="quality-fill" style="width: ${dataset.quality_summary.individual_scores.consistency}%"></div>
                                        <span>${dataset.quality_summary.individual_scores.consistency.toFixed(1)}%</span>
                                    </div>
                                </div>
                                ` : ''}
                            </div>
                        </div>
                        ` : ''}
                    </div>
                </div>
                
                ${dataset.description ? `
                <div class="detail-section">
                    <h6>描述</h6>
                    <p>${dataset.description}</p>
                </div>
                ` : ''}
                
                ${dataset.metadata && dataset.metadata.analysis_result ? `
                <div class="detail-section">
                    <h6>分析结果</h6>
                    <div class="analysis-results">
                        <!-- 这里可以显示更详细的分析结果 -->
                        <small class="text-muted">分析完成于 ${dataset.metadata.analysis_result.analyzed_at}</small>
                    </div>
                </div>
                ` : ''}
            </div>
        `;
    }
    
    async quickPreviewDataset(datasetId) {
        try {
            const response = await fetch(`/api/ai/datasets/${datasetId}/preview`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showDataPreview(result.data);
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('预览数据失败:', error);
            this.showAlert(`预览数据失败: ${error.message}`, 'error');
        }
    }
    
    showDataPreview(previewData) {
        const content = document.getElementById('dataPreviewContent');
        
        if (previewData.columns && previewData.data) {
            // 表格数据预览
            content.innerHTML = `
                <div class="data-preview">
                    <div class="preview-info">
                        <p>显示前 ${previewData.showing_rows} 行，总共 ${previewData.total_rows.toLocaleString()} 行</p>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-striped table-hover">
                            <thead class="table-dark">
                                <tr>
                                    ${previewData.columns.map(col => `<th>${col}</th>`).join('')}
                                </tr>
                            </thead>
                            <tbody>
                                ${previewData.data.map(row => `
                                    <tr>
                                        ${row.map(cell => `<td>${cell}</td>`).join('')}
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        } else if (previewData.sample_images) {
            // 图像数据预览
            content.innerHTML = `
                <div class="data-preview">
                    <div class="preview-info">
                        <p>显示 ${previewData.showing_samples} 个样本，总共 ${previewData.total_images.toLocaleString()} 张图片</p>
                    </div>
                    <div class="image-samples">
                        ${previewData.sample_images.map(img => `
                            <div class="image-sample">
                                <div class="image-placeholder">
                                    <span>📷</span>
                                    <small>${img.filename}</small>
                                </div>
                                <div class="image-info">
                                    <span>类别: ${img.class}</span>
                                    <span>尺寸: ${img.size.join('x')}</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        } else {
            content.innerHTML = `
                <div class="data-preview">
                    <div class="alert alert-info">
                        ${previewData.message || '暂无预览数据'}
                    </div>
                </div>
            `;
        }
        
        new bootstrap.Modal(document.getElementById('dataPreviewModal')).show();
    }
    
    filterDatasets() {
        const typeFilter = document.getElementById('dataTypeFilter').value;
        const statusFilter = document.getElementById('statusFilter').value;
        
        let filteredDatasets = this.datasets;
        
        if (typeFilter) {
            filteredDatasets = filteredDatasets.filter(dataset => dataset.data_type === typeFilter);
        }
        
        if (statusFilter) {
            filteredDatasets = filteredDatasets.filter(dataset => dataset.status === statusFilter);
        }
        
        // 临时保存原始数据并渲染过滤后的数据
        const originalDatasets = this.datasets;
        this.datasets = filteredDatasets;
        this.renderDatasets();
        this.datasets = originalDatasets;
    }
    
    getStatusText(status) {
        const statusMap = {
            'created': '已创建',
            'processing': '处理中',
            'ready': '就绪',
            'error': '错误'
        };
        return statusMap[status] || status;
    }
    
    getDataTypeText(dataType) {
        const typeMap = {
            'image': '图像',
            'text': '文本',
            'tabular': '表格',
            'audio': '音频',
            'video': '视频',
            'time_series': '时间序列'
        };
        return typeMap[dataType] || dataType;
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    showAlert(message, type = 'info') {
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
window.DatasetManager = DatasetManager;