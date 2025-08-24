/**
 * 密钥管理组件
 * 生成、管理和操作各种类型的密钥
 */

class KeyManager {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.keys = [];
        this.selectedKey = null;
        
        this.init();
    }
    
    init() {
        this.createLayout();
        this.bindEvents();
        this.loadKeys();
    }
    
    createLayout() {
        this.container.innerHTML = `
            <div class="key-manager">
                <div class="manager-header">
                    <h3>密钥管理</h3>
                    <div class="manager-controls">
                        <button id="generateKey" class="crypto-btn">生成密钥</button>
                        <button id="importKey" class="crypto-btn crypto-btn-secondary">导入密钥</button>
                        <button id="refreshKeys" class="btn btn-outline-secondary">
                            <i class="bi bi-arrow-clockwise"></i> 刷新
                        </button>
                    </div>
                </div>
                
                <!-- 筛选和搜索 -->
                <div class="manager-filters">
                    <div class="filter-group">
                        <label>密钥类型</label>
                        <select id="keyTypeFilter" class="form-select">
                            <option value="">所有类型</option>
                            <option value="rsa">RSA</option>
                            <option value="aes">AES</option>
                            <option value="ecc">ECC</option>
                            <option value="dsa">DSA</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>状态筛选</label>
                        <select id="statusFilter" class="form-select">
                            <option value="">所有状态</option>
                            <option value="active">活跃</option>
                            <option value="expired">已过期</option>
                            <option value="revoked">已撤销</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>搜索</label>
                        <input type="text" id="searchKeys" class="form-control" 
                               placeholder="搜索密钥名称...">
                    </div>
                </div>
                
                <!-- 密钥列表 -->
                <div class="key-grid" id="keyGrid">
                    <!-- 密钥卡片将动态生成 -->
                </div>
            </div>
            
            <!-- 生成密钥模态框 -->
            <div class="modal fade" id="generateKeyModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">生成新密钥</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="key-generation-form">
                                <form id="keyGenerationForm">
                                    <div class="form-section">
                                        <h6>基本信息</h6>
                                        <div class="mb-3">
                                            <label class="form-label">密钥名称</label>
                                            <input type="text" class="form-control" id="keyName" required>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">密钥类型</label>
                                            <select class="form-select" id="keyType" required>
                                                <option value="">选择密钥类型</option>
                                                <option value="rsa">RSA (非对称加密)</option>
                                                <option value="aes">AES (对称加密)</option>
                                                <option value="ecc">ECC (椭圆曲线)</option>
                                                <option value="dsa">DSA (数字签名)</option>
                                            </select>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">用途</label>
                                            <select class="form-select" id="keyPurpose">
                                                <option value="encryption">加密</option>
                                                <option value="signing">数字签名</option>
                                                <option value="both">加密和签名</option>
                                            </select>
                                        </div>
                                    </div>
                                    
                                    <div class="form-section">
                                        <h6>密钥参数</h6>
                                        <div class="mb-3" id="keySizeSection">
                                            <label class="form-label">密钥长度</label>
                                            <div class="key-size-selector" id="keySizeSelector">
                                                <!-- 动态生成密钥长度选项 -->
                                            </div>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">有效期 (天)</label>
                                            <input type="number" class="form-control" id="keyValidity" 
                                                   value="365" min="1" max="3650">
                                        </div>
                                    </div>
                                    
                                    <div class="form-section">
                                        <h6>安全选项</h6>
                                        <div class="mb-3">
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="keyPassword">
                                                <label class="form-check-label" for="keyPassword">
                                                    使用密码保护
                                                </label>
                                            </div>
                                        </div>
                                        <div class="mb-3" id="passwordSection" style="display: none;">
                                            <label class="form-label">密钥密码</label>
                                            <input type="password" class="form-control" id="keyPasswordInput">
                                        </div>
                                        <div class="mb-3">
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="keyBackup" checked>
                                                <label class="form-check-label" for="keyBackup">
                                                    自动备份密钥
                                                </label>
                                            </div>
                                        </div>
                                    </div>
                                </form>
                                
                                <div class="generation-progress" id="generationProgress" style="display: none;">
                                    <h6>正在生成密钥...</h6>
                                    <div class="crypto-progress">
                                        <div class="crypto-progress-bar" id="progressBar" style="width: 0%"></div>
                                    </div>
                                    <p class="text-muted" id="progressText">初始化随机数生成器...</p>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="submit" form="keyGenerationForm" class="crypto-btn" id="generateBtn">
                                生成密钥
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 密钥详情模态框 -->
            <div class="modal fade" id="keyDetailModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="keyDetailTitle">密钥详情</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <!-- 密钥基本信息 -->
                                    <div class="detail-section">
                                        <h6>基本信息</h6>
                                        <div class="detail-grid" id="keyBasicInfo">
                                            <!-- 动态生成 -->
                                        </div>
                                    </div>
                                    
                                    <!-- 密钥内容 -->
                                    <div class="detail-section">
                                        <h6>密钥内容</h6>
                                        <div class="key-content">
                                            <div class="mb-3">
                                                <label class="form-label">公钥</label>
                                                <div class="key-display" id="publicKeyDisplay">
                                                    <!-- 公钥内容 -->
                                                </div>
                                                <button class="btn btn-sm btn-outline-secondary mt-2" 
                                                        onclick="this.copyToClipboard('public')">
                                                    <i class="bi bi-copy"></i> 复制公钥
                                                </button>
                                            </div>
                                            <div class="mb-3" id="privateKeySection">
                                                <label class="form-label">私钥</label>
                                                <div class="key-display" id="privateKeyDisplay">
                                                    <!-- 私钥内容 -->
                                                </div>
                                                <button class="btn btn-sm btn-outline-warning mt-2" 
                                                        onclick="this.copyToClipboard('private')">
                                                    <i class="bi bi-copy"></i> 复制私钥
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <!-- 密钥统计 -->
                                    <div class="detail-section">
                                        <h6>使用统计</h6>
                                        <div class="key-stats" id="keyStats">
                                            <!-- 动态生成 -->
                                        </div>
                                    </div>
                                    
                                    <!-- 操作历史 -->
                                    <div class="detail-section">
                                        <h6>最近操作</h6>
                                        <div class="operation-history" id="keyOperationHistory">
                                            <!-- 动态生成 -->
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                            <button type="button" class="crypto-btn" onclick="this.exportKey()">
                                <i class="bi bi-download"></i> 导出密钥
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 导入密钥模态框 -->
            <div class="modal fade" id="importKeyModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">导入密钥</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="import-methods">
                                <div class="nav nav-tabs" role="tablist">
                                    <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#fileImport">
                                        文件导入
                                    </button>
                                    <button class="nav-link" data-bs-toggle="tab" data-bs-target="#textImport">
                                        文本导入
                                    </button>
                                </div>
                                
                                <div class="tab-content mt-3">
                                    <div class="tab-pane fade show active" id="fileImport">
                                        <div class="file-drop-zone" id="keyFileDropzone">
                                            <div class="drop-icon">📁</div>
                                            <h6>拖拽文件到此处或点击选择</h6>
                                            <p class="text-muted">支持 PEM, DER, P12, JKS 格式</p>
                                            <input type="file" id="keyFileInput" class="d-none" 
                                                   accept=".pem,.der,.p12,.jks,.key,.crt,.cer">
                                        </div>
                                    </div>
                                    
                                    <div class="tab-pane fade" id="textImport">
                                        <form id="textImportForm">
                                            <div class="mb-3">
                                                <label class="form-label">密钥名称</label>
                                                <input type="text" class="form-control" id="importKeyName" required>
                                            </div>
                                            <div class="mb-3">
                                                <label class="form-label">密钥内容</label>
                                                <textarea class="form-control text-area-large" 
                                                          id="keyTextContent" 
                                                          placeholder="粘贴密钥内容..." required></textarea>
                                            </div>
                                            <div class="mb-3">
                                                <label class="form-label">密钥类型</label>
                                                <select class="form-select" id="importKeyType">
                                                    <option value="auto">自动检测</option>
                                                    <option value="rsa">RSA</option>
                                                    <option value="aes">AES</option>
                                                    <option value="ecc">ECC</option>
                                                    <option value="dsa">DSA</option>
                                                </select>
                                            </div>
                                        </form>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="button" class="crypto-btn" onclick="this.importKey()">
                                导入密钥
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    bindEvents() {
        document.getElementById('generateKey').addEventListener('click', () => this.showGenerateKeyModal());
        document.getElementById('importKey').addEventListener('click', () => this.showImportKeyModal());
        document.getElementById('refreshKeys').addEventListener('click', () => this.refreshKeys());
        
        document.getElementById('keyTypeFilter').addEventListener('change', () => this.filterKeys());
        document.getElementById('statusFilter').addEventListener('change', () => this.filterKeys());
        document.getElementById('searchKeys').addEventListener('input', () => this.searchKeys());
        
        const keyGenerationForm = document.getElementById('keyGenerationForm');
        if (keyGenerationForm) {
            keyGenerationForm.addEventListener('submit', (e) => this.generateKey(e));
        }
        
        const keyTypeSelect = document.getElementById('keyType');
        if (keyTypeSelect) {
            keyTypeSelect.addEventListener('change', (e) => this.updateKeySizeOptions(e.target.value));
        }
        
        const keyPasswordCheck = document.getElementById('keyPassword');
        if (keyPasswordCheck) {
            keyPasswordCheck.addEventListener('change', (e) => {
                const passwordSection = document.getElementById('passwordSection');
                passwordSection.style.display = e.target.checked ? 'block' : 'none';
            });
        }
        
        const keyFileDropzone = document.getElementById('keyFileDropzone');
        const keyFileInput = document.getElementById('keyFileInput');
        
        if (keyFileDropzone && keyFileInput) {
            keyFileDropzone.addEventListener('click', () => keyFileInput.click());
            keyFileDropzone.addEventListener('dragover', (e) => {
                e.preventDefault();
                keyFileDropzone.classList.add('drag-over');
            });
            keyFileDropzone.addEventListener('dragleave', () => {
                keyFileDropzone.classList.remove('drag-over');
            });
            keyFileDropzone.addEventListener('drop', (e) => {
                e.preventDefault();
                keyFileDropzone.classList.remove('drag-over');
                this.handleFileImport(e.dataTransfer.files[0]);
            });
            keyFileInput.addEventListener('change', (e) => {
                this.handleFileImport(e.target.files[0]);
            });
        }
    }
    
    async loadKeys() {
        try {
            const response = await fetch('/api/crypto/keys', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const result = await response.json();
            if (result.success) {
                this.keys = result.data;
                this.renderKeys();
            }
        } catch (error) {
            console.error('加载密钥失败:', error);
            // 加载模拟数据
            this.loadMockData();
        }
    }
    
    loadMockData() {
        this.keys = [
            {
                id: '1',
                name: 'MyRSA2048',
                type: 'rsa',
                key_size: 2048,
                purpose: 'encryption',
                status: 'active',
                created_at: new Date().toISOString(),
                expires_at: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(),
                usage_count: 45,
                last_used: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
            },
            {
                id: '2',
                name: 'AES256-Secret',
                type: 'aes',
                key_size: 256,
                purpose: 'encryption',
                status: 'active',
                created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
                expires_at: new Date(Date.now() + 335 * 24 * 60 * 60 * 1000).toISOString(),
                usage_count: 123,
                last_used: new Date(Date.now() - 5 * 60 * 1000).toISOString()
            }
        ];
        this.renderKeys();
    }
    
    renderKeys() {
        const container = document.getElementById('keyGrid');
        if (!container) return;
        
        if (this.keys.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🔐</div>
                    <h4>暂无密钥</h4>
                    <p>生成您的第一个密钥</p>
                    <button class="crypto-btn" onclick="this.showGenerateKeyModal()">生成密钥</button>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.keys.map(key => `
            <div class="key-card">
                <div class="key-header">
                    <div class="key-info">
                        <h5 class="key-name">${key.name}</h5>
                        <div class="key-type">
                            <span class="key-type-badge ${key.type}">${key.type.toUpperCase()}</span>
                            <span class="badge bg-secondary">${key.key_size} bits</span>
                        </div>
                    </div>
                    <div class="key-status">
                        <span class="status-indicator status-${key.status}"></span>
                        <span class="status-text">${this.getStatusText(key.status)}</span>
                    </div>
                </div>
                
                <div class="key-info">
                    <div class="info-item">
                        <span class="info-label">用途:</span>
                        <span class="info-value">${this.getPurposeText(key.purpose)}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">创建时间:</span>
                        <span class="info-value">${new Date(key.created_at).toLocaleDateString()}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">过期时间:</span>
                        <span class="info-value">${new Date(key.expires_at).toLocaleDateString()}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">使用次数:</span>
                        <span class="info-value">${key.usage_count}</span>
                    </div>
                </div>
                
                <!-- 安全等级指示器 -->
                <div class="security-level ${this.getSecurityLevel(key)}">
                    <i class="bi bi-shield-check"></i>
                    ${this.getSecurityLevelText(key)}
                </div>
                
                <div class="key-actions">
                    <button class="btn btn-sm btn-outline-primary" 
                            onclick="this.viewKeyDetails('${key.id}')">
                        查看详情
                    </button>
                    <button class="btn btn-sm btn-outline-success" 
                            onclick="this.useKey('${key.id}')">
                        使用密钥
                    </button>
                    <div class="dropdown">
                        <button class="btn btn-sm btn-outline-secondary dropdown-toggle" 
                                data-bs-toggle="dropdown">
                            更多
                        </button>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" onclick="this.exportKey('${key.id}')">导出密钥</a></li>
                            <li><a class="dropdown-item" onclick="this.renewKey('${key.id}')">续期密钥</a></li>
                            <li><a class="dropdown-item" onclick="this.revokeKey('${key.id}')">撤销密钥</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-danger" onclick="this.deleteKey('${key.id}')">删除密钥</a></li>
                        </ul>
                    </div>
                </div>
                
                <div class="key-footer">
                    <small class="text-muted">
                        最后使用: ${key.last_used ? new Date(key.last_used).toLocaleString() : '从未使用'}
                    </small>
                </div>
            </div>
        `).join('');
    }
    
    showGenerateKeyModal() {
        const modal = new bootstrap.Modal(document.getElementById('generateKeyModal'));
        modal.show();
    }
    
    showImportKeyModal() {
        const modal = new bootstrap.Modal(document.getElementById('importKeyModal'));
        modal.show();
    }
    
    updateKeySizeOptions(keyType) {
        const selector = document.getElementById('keySizeSelector');
        const keySizes = this.getKeySizesForType(keyType);
        
        selector.innerHTML = keySizes.map(size => `
            <div class="key-size-option" onclick="this.selectKeySize(${size})">
                ${size}
            </div>
        `).join('');
        
        // 默认选择第一个
        if (keySizes.length > 0) {
            this.selectKeySize(keySizes[0]);
        }
    }
    
    selectKeySize(size) {
        const options = document.querySelectorAll('.key-size-option');
        options.forEach(option => option.classList.remove('selected'));
        
        const selectedOption = [...options].find(option => 
            parseInt(option.textContent.trim()) === size
        );
        if (selectedOption) {
            selectedOption.classList.add('selected');
        }
    }
    
    getKeySizesForType(type) {
        const sizes = {
            rsa: [1024, 2048, 3072, 4096],
            aes: [128, 192, 256],
            ecc: [256, 384, 521],
            dsa: [1024, 2048, 3072]
        };
        return sizes[type] || [2048];
    }
    
    async generateKey(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const selectedSizeOption = document.querySelector('.key-size-option.selected');
        const keySize = selectedSizeOption ? parseInt(selectedSizeOption.textContent.trim()) : 2048;
        
        const keyData = {
            name: formData.get('keyName'),
            type: formData.get('keyType'),
            key_size: keySize,
            purpose: formData.get('keyPurpose'),
            validity_days: parseInt(formData.get('keyValidity')),
            password_protected: document.getElementById('keyPassword').checked,
            password: document.getElementById('keyPasswordInput').value,
            auto_backup: document.getElementById('keyBackup').checked
        };
        
        try {
            // 显示进度
            this.showGenerationProgress();
            
            const response = await fetch('/api/crypto/keys/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(keyData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('generateKeyModal'));
                modal.hide();
                
                // 重置表单
                event.target.reset();
                document.getElementById('passwordSection').style.display = 'none';
                
                // 刷新密钥列表
                await this.refreshKeys();
                
                this.showNotification('密钥生成成功', 'success');
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('生成密钥失败:', error);
            this.showNotification(`生成密钥失败: ${error.message}`, 'error');
        } finally {
            this.hideGenerationProgress();
        }
    }
    
    showGenerationProgress() {
        const form = document.querySelector('#generateKeyModal .key-generation-form form');
        const progress = document.getElementById('generationProgress');
        const generateBtn = document.getElementById('generateBtn');
        
        form.style.display = 'none';
        progress.style.display = 'block';
        generateBtn.disabled = true;
        
        // 模拟进度更新
        let progressValue = 0;
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        const messages = [
            '初始化随机数生成器...',
            '生成密钥对...',
            '验证密钥强度...',
            '保存密钥信息...',
            '创建备份...'
        ];
        
        const interval = setInterval(() => {
            progressValue += Math.random() * 20;
            if (progressValue > 100) progressValue = 100;
            
            progressBar.style.width = `${progressValue}%`;
            progressText.textContent = messages[Math.floor((progressValue / 100) * (messages.length - 1))];
            
            if (progressValue >= 100) {
                clearInterval(interval);
            }
        }, 500);
        
        this.progressInterval = interval;
    }
    
    hideGenerationProgress() {
        const form = document.querySelector('#generateKeyModal .key-generation-form form');
        const progress = document.getElementById('generationProgress');
        const generateBtn = document.getElementById('generateBtn');
        
        form.style.display = 'block';
        progress.style.display = 'none';
        generateBtn.disabled = false;
        
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
    }
    
    async viewKeyDetails(keyId) {
        try {
            const response = await fetch(`/api/crypto/keys/${keyId}/details`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const result = await response.json();
            if (result.success) {
                this.showKeyDetails(result.data);
            }
        } catch (error) {
            console.error('获取密钥详情失败:', error);
            // 显示本地密钥详情
            const key = this.keys.find(k => k.id === keyId);
            if (key) {
                this.showKeyDetails(key);
            }
        }
    }
    
    showKeyDetails(keyData) {
        const modal = new bootstrap.Modal(document.getElementById('keyDetailModal'));
        
        // 更新标题
        document.getElementById('keyDetailTitle').textContent = `${keyData.name} - 详情`;
        
        // 更新基本信息
        const basicInfo = document.getElementById('keyBasicInfo');
        basicInfo.innerHTML = `
            <div class="detail-item">
                <label>密钥名称</label>
                <span>${keyData.name}</span>
            </div>
            <div class="detail-item">
                <label>密钥类型</label>
                <span class="key-type-badge ${keyData.type}">${keyData.type.toUpperCase()}</span>
            </div>
            <div class="detail-item">
                <label>密钥长度</label>
                <span>${keyData.key_size} bits</span>
            </div>
            <div class="detail-item">
                <label>用途</label>
                <span>${this.getPurposeText(keyData.purpose)}</span>
            </div>
            <div class="detail-item">
                <label>状态</label>
                <span class="status-${keyData.status}">${this.getStatusText(keyData.status)}</span>
            </div>
            <div class="detail-item">
                <label>创建时间</label>
                <span>${new Date(keyData.created_at).toLocaleString()}</span>
            </div>
            <div class="detail-item">
                <label>过期时间</label>
                <span>${new Date(keyData.expires_at).toLocaleString()}</span>
            </div>
        `;
        
        // 显示密钥内容（模拟）
        document.getElementById('publicKeyDisplay').textContent = '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----';
        document.getElementById('privateKeyDisplay').textContent = '-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----';
        
        this.selectedKey = keyData;
        modal.show();
    }
    
    // 工具方法
    getStatusText(status) {
        const statuses = {
            active: '活跃',
            expired: '已过期',
            revoked: '已撤销',
            pending: '待激活'
        };
        return statuses[status] || status;
    }
    
    getPurposeText(purpose) {
        const purposes = {
            encryption: '加密',
            signing: '数字签名',
            both: '加密和签名'
        };
        return purposes[purpose] || purpose;
    }
    
    getSecurityLevel(key) {
        const { type, key_size } = key;
        
        if (type === 'aes' && key_size >= 256) return 'ultra';
        if (type === 'rsa' && key_size >= 4096) return 'ultra';
        if (type === 'ecc' && key_size >= 384) return 'high';
        if (type === 'rsa' && key_size >= 2048) return 'high';
        if (key_size >= 1024) return 'medium';
        
        return 'low';
    }
    
    getSecurityLevelText(key) {
        const levels = {
            low: '低级',
            medium: '中级',
            high: '高级',
            ultra: '超高级'
        };
        return levels[this.getSecurityLevel(key)];
    }
    
    filterKeys() {
        const typeFilter = document.getElementById('keyTypeFilter').value;
        const statusFilter = document.getElementById('statusFilter').value;
        
        let filtered = this.keys;
        
        if (typeFilter) {
            filtered = filtered.filter(key => key.type === typeFilter);
        }
        
        if (statusFilter) {
            filtered = filtered.filter(key => key.status === statusFilter);
        }
        
        this.renderFilteredKeys(filtered);
    }
    
    searchKeys() {
        const query = document.getElementById('searchKeys').value.toLowerCase();
        
        const filtered = query 
            ? this.keys.filter(key => key.name.toLowerCase().includes(query))
            : this.keys;
        
        this.renderFilteredKeys(filtered);
    }
    
    renderFilteredKeys(keys) {
        const originalKeys = this.keys;
        this.keys = keys;
        this.renderKeys();
        this.keys = originalKeys;
    }
    
    async refreshKeys() {
        await this.loadKeys();
        this.showNotification('密钥列表已刷新', 'info');
    }
    
    copyToClipboard(keyType) {
        const content = keyType === 'public' 
            ? document.getElementById('publicKeyDisplay').textContent
            : document.getElementById('privateKeyDisplay').textContent;
        
        navigator.clipboard.writeText(content).then(() => {
            this.showNotification('密钥已复制到剪贴板', 'success');
        }).catch(err => {
            console.error('复制失败:', err);
        });
    }
    
    exportKey(keyId = null) {
        if (keyId) {
            this.selectedKey = this.keys.find(k => k.id === keyId);
        }
        
        if (!this.selectedKey) return;
        
        const data = {
            name: this.selectedKey.name,
            type: this.selectedKey.type,
            public_key: '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----',
            export_time: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        
        a.href = url;
        a.download = `${this.selectedKey.name}-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('密钥已导出', 'success');
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
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
    }
}

// 导出组件
window.KeyManager = KeyManager;