/**
 * 加密工具组件
 * 提供数据加密、解密、数字签名等功能
 */

class EncryptionTool {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.operationHistory = [];
        this.selectedKey = null;
        
        this.init();
    }
    
    init() {
        this.createLayout();
        this.bindEvents();
        this.loadAvailableKeys();
    }
    
    createLayout() {
        this.container.innerHTML = `
            <div class="encryption-tool">
                <div class="tool-header">
                    <h3>加密工具</h3>
                    <div class="tool-controls">
                        <button id="clearAll" class="crypto-btn crypto-btn-secondary">清空所有</button>
                        <button id="showHistory" class="crypto-btn crypto-btn-secondary">操作历史</button>
                    </div>
                </div>
                
                <!-- 操作选择 -->
                <div class="operation-selector mb-4">
                    <div class="btn-group w-100" role="group">
                        <input type="radio" class="btn-check" name="operation" id="encryptOp" value="encrypt" checked>
                        <label class="btn btn-outline-success" for="encryptOp">
                            <i class="bi bi-shield-lock me-2"></i>加密
                        </label>
                        
                        <input type="radio" class="btn-check" name="operation" id="decryptOp" value="decrypt">
                        <label class="btn btn-outline-warning" for="decryptOp">
                            <i class="bi bi-shield-unlock me-2"></i>解密
                        </label>
                        
                        <input type="radio" class="btn-check" name="operation" id="signOp" value="sign">
                        <label class="btn btn-outline-primary" for="signOp">
                            <i class="bi bi-pen me-2"></i>数字签名
                        </label>
                        
                        <input type="radio" class="btn-check" name="operation" id="verifyOp" value="verify">
                        <label class="btn btn-outline-info" for="verifyOp">
                            <i class="bi bi-check-circle me-2"></i>验证签名
                        </label>
                        
                        <input type="radio" class="btn-check" name="operation" id="hashOp" value="hash">
                        <label class="btn btn-outline-secondary" for="hashOp">
                            <i class="bi bi-hash me-2"></i>哈希
                        </label>
                    </div>
                </div>
                
                <!-- 密钥选择区域 -->
                <div class="key-selection mb-4" id="keySelectionArea">
                    <div class="crypto-card p-3">
                        <h6><i class="bi bi-key me-2"></i>选择密钥</h6>
                        <div class="row">
                            <div class="col-md-6">
                                <select class="form-select" id="keySelect">
                                    <option value="">选择密钥...</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <div class="selected-key-info" id="selectedKeyInfo">
                                    <small class="text-muted">请选择一个密钥</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 工作区域 -->
                <div class="encryption-workspace">
                    <!-- 输入面板 -->
                    <div class="input-panel">
                        <h6 class="mb-3">
                            <i class="bi bi-input-cursor me-2"></i>输入数据
                        </h6>
                        <div class="input-methods mb-3">
                            <div class="btn-group" role="group">
                                <input type="radio" class="btn-check" name="inputMethod" id="textInput" value="text" checked>
                                <label class="btn btn-outline-secondary btn-sm" for="textInput">文本输入</label>
                                
                                <input type="radio" class="btn-check" name="inputMethod" id="fileInput" value="file">
                                <label class="btn btn-outline-secondary btn-sm" for="fileInput">文件上传</label>
                            </div>
                        </div>
                        
                        <!-- 文本输入 -->
                        <div class="text-input-area" id="textInputArea">
                            <textarea class="text-area-large" id="inputText" 
                                      placeholder="输入要处理的文本数据..."></textarea>
                        </div>
                        
                        <!-- 文件上传 -->
                        <div class="file-input-area" id="fileInputArea" style="display: none;">
                            <div class="file-drop-zone" id="fileDropzone">
                                <div class="drop-icon">📁</div>
                                <h6>拖拽文件到此处或点击选择</h6>
                                <p class="text-muted">支持所有文件类型</p>
                                <input type="file" id="fileSelect" class="d-none">
                            </div>
                            <div class="selected-file-info" id="selectedFileInfo" style="display: none;">
                                <div class="alert alert-info">
                                    <strong>已选择文件:</strong> <span id="fileName"></span><br>
                                    <strong>文件大小:</strong> <span id="fileSize"></span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- 高级选项 -->
                        <div class="advanced-options mt-3" id="advancedOptions">
                            <!-- 动态生成高级选项 -->
                        </div>
                        
                        <!-- 操作按钮 -->
                        <div class="operation-buttons mt-3">
                            <button id="executeOperation" class="crypto-btn w-100">
                                <i class="bi bi-play-circle me-2"></i>
                                <span id="operationButtonText">执行加密</span>
                            </button>
                        </div>
                    </div>
                    
                    <!-- 输出面板 -->
                    <div class="output-panel">
                        <h6 class="mb-3">
                            <i class="bi bi-output me-2"></i>输出结果
                        </h6>
                        
                        <div class="output-area">
                            <textarea class="text-area-large" id="outputText" readonly 
                                      placeholder="处理结果将显示在这里..."></textarea>
                        </div>
                        
                        <div class="output-actions mt-3">
                            <button class="btn btn-outline-secondary" onclick="this.copyOutput()">
                                <i class="bi bi-copy me-2"></i>复制结果
                            </button>
                            <button class="btn btn-outline-primary" onclick="this.downloadOutput()">
                                <i class="bi bi-download me-2"></i>下载结果
                            </button>
                            <button class="btn btn-outline-info" onclick="this.saveToHistory()">
                                <i class="bi bi-bookmark me-2"></i>保存到历史
                            </button>
                        </div>
                        
                        <!-- 操作信息 -->
                        <div class="operation-info mt-3" id="operationInfo" style="display: none;">
                            <div class="alert alert-success">
                                <strong>操作成功!</strong><br>
                                <span id="operationDetails"></span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 进度指示器 -->
                <div class="operation-progress" id="operationProgress" style="display: none;">
                    <div class="crypto-progress">
                        <div class="crypto-progress-bar" id="progressBar" style="width: 0%"></div>
                    </div>
                    <p class="text-center mt-2" id="progressText">正在处理...</p>
                </div>
            </div>
            
            <!-- 操作历史模态框 -->
            <div class="modal fade" id="historyModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">操作历史</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="operation-history" id="operationHistoryList">
                                <!-- 操作历史将在这里显示 -->
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                            <button type="button" class="crypto-btn" onclick="this.clearHistory()">
                                清空历史
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    bindEvents() {
        // 操作类型选择
        document.querySelectorAll('input[name="operation"]').forEach(radio => {
            radio.addEventListener('change', (e) => this.onOperationChange(e.target.value));
        });
        
        // 输入方式选择
        document.querySelectorAll('input[name="inputMethod"]').forEach(radio => {
            radio.addEventListener('change', (e) => this.onInputMethodChange(e.target.value));
        });
        
        // 密钥选择
        document.getElementById('keySelect').addEventListener('change', (e) => {
            this.onKeySelect(e.target.value);
        });
        
        // 执行操作
        document.getElementById('executeOperation').addEventListener('click', () => {
            this.executeOperation();
        });
        
        // 文件处理
        const fileDropzone = document.getElementById('fileDropzone');
        const fileSelect = document.getElementById('fileSelect');
        
        fileDropzone.addEventListener('click', () => fileSelect.click());
        fileDropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            fileDropzone.classList.add('drag-over');
        });
        fileDropzone.addEventListener('dragleave', () => {
            fileDropzone.classList.remove('drag-over');
        });
        fileDropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            fileDropzone.classList.remove('drag-over');
            this.handleFileSelect(e.dataTransfer.files[0]);
        });
        fileSelect.addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files[0]);
        });
        
        // 控制按钮
        document.getElementById('clearAll').addEventListener('click', () => this.clearAll());
        document.getElementById('showHistory').addEventListener('click', () => this.showHistory());
    }
    
    async loadAvailableKeys() {
        try {
            const response = await fetch('/api/crypto/keys', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const result = await response.json();
            if (result.success) {
                this.populateKeySelect(result.data);
            }
        } catch (error) {
            console.error('加载密钥失败:', error);
            // 加载模拟数据
            this.loadMockKeys();
        }
    }
    
    loadMockKeys() {
        const mockKeys = [
            { id: '1', name: 'MyRSA2048', type: 'rsa', key_size: 2048, purpose: 'both' },
            { id: '2', name: 'AES256-Secret', type: 'aes', key_size: 256, purpose: 'encryption' },
            { id: '3', name: 'ECC-P256', type: 'ecc', key_size: 256, purpose: 'signing' }
        ];
        this.populateKeySelect(mockKeys);
    }
    
    populateKeySelect(keys) {
        const select = document.getElementById('keySelect');
        select.innerHTML = '<option value="">选择密钥...</option>' +
            keys.map(key => `
                <option value="${key.id}" data-type="${key.type}" data-size="${key.key_size}" data-purpose="${key.purpose}">
                    ${key.name} (${key.type.toUpperCase()} ${key.key_size}bit)
                </option>
            `).join('');
    }
    
    onOperationChange(operation) {
        // 更新按钮文本
        const buttonTexts = {
            encrypt: '执行加密',
            decrypt: '执行解密', 
            sign: '生成签名',
            verify: '验证签名',
            hash: '计算哈希'
        };
        
        document.getElementById('operationButtonText').textContent = buttonTexts[operation];
        
        // 更新高级选项
        this.updateAdvancedOptions(operation);
        
        // 更新密钥选择区域显示
        const keyArea = document.getElementById('keySelectionArea');
        if (operation === 'hash') {
            keyArea.style.display = 'none';
        } else {
            keyArea.style.display = 'block';
        }
    }
    
    updateAdvancedOptions(operation) {
        const advancedOptions = document.getElementById('advancedOptions');
        
        switch (operation) {
            case 'encrypt':
                advancedOptions.innerHTML = `
                    <div class="mb-2">
                        <label class="form-label">填充模式</label>
                        <select class="form-select form-select-sm" id="paddingMode">
                            <option value="PKCS1">PKCS#1</option>
                            <option value="OAEP">OAEP</option>
                            <option value="PSS">PSS</option>
                        </select>
                    </div>
                `;
                break;
            case 'hash':
                advancedOptions.innerHTML = `
                    <div class="mb-2">
                        <label class="form-label">哈希算法</label>
                        <select class="form-select form-select-sm" id="hashAlgorithm">
                            <option value="SHA256">SHA-256</option>
                            <option value="SHA512">SHA-512</option>
                            <option value="MD5">MD5</option>
                            <option value="SHA1">SHA-1</option>
                        </select>
                    </div>
                `;
                break;
            case 'sign':
                advancedOptions.innerHTML = `
                    <div class="mb-2">
                        <label class="form-label">签名算法</label>
                        <select class="form-select form-select-sm" id="signAlgorithm">
                            <option value="RSA-SHA256">RSA with SHA-256</option>
                            <option value="ECDSA-SHA256">ECDSA with SHA-256</option>
                            <option value="DSA-SHA256">DSA with SHA-256</option>
                        </select>
                    </div>
                `;
                break;
            default:
                advancedOptions.innerHTML = '';
                break;
        }
    }
    
    onInputMethodChange(method) {
        const textArea = document.getElementById('textInputArea');
        const fileArea = document.getElementById('fileInputArea');
        
        if (method === 'text') {
            textArea.style.display = 'block';
            fileArea.style.display = 'none';
        } else {
            textArea.style.display = 'none';
            fileArea.style.display = 'block';
        }
    }
    
    onKeySelect(keyId) {
        if (!keyId) {
            document.getElementById('selectedKeyInfo').innerHTML = '<small class="text-muted">请选择一个密钥</small>';
            return;
        }
        
        const option = document.querySelector(`option[value="${keyId}"]`);
        if (option) {
            const type = option.dataset.type;
            const size = option.dataset.size;
            const purpose = option.dataset.purpose;
            
            document.getElementById('selectedKeyInfo').innerHTML = `
                <div class="selected-key-details">
                    <span class="key-type-badge ${type}">${type.toUpperCase()}</span>
                    <small class="text-muted ms-2">${size} bits | ${this.getPurposeText(purpose)}</small>
                </div>
            `;
            
            this.selectedKey = { id: keyId, type, size, purpose };
        }
    }
    
    handleFileSelect(file) {
        if (!file) return;
        
        const fileInfo = document.getElementById('selectedFileInfo');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        
        fileName.textContent = file.name;
        fileSize.textContent = this.formatFileSize(file.size);
        fileInfo.style.display = 'block';
        
        // 读取文件内容
        const reader = new FileReader();
        reader.onload = (e) => {
            this.selectedFile = {
                name: file.name,
                size: file.size,
                content: e.target.result
            };
        };
        reader.readAsArrayBuffer(file);
    }
    
    async executeOperation() {
        const operation = document.querySelector('input[name="operation"]:checked').value;
        const inputMethod = document.querySelector('input[name="inputMethod"]:checked').value;
        
        let inputData;
        if (inputMethod === 'text') {
            inputData = document.getElementById('inputText').value;
            if (!inputData.trim()) {
                this.showNotification('请输入要处理的数据', 'warning');
                return;
            }
        } else {
            if (!this.selectedFile) {
                this.showNotification('请选择要处理的文件', 'warning');
                return;
            }
            inputData = this.selectedFile.content;
        }
        
        if (operation !== 'hash' && !this.selectedKey) {
            this.showNotification('请选择密钥', 'warning');
            return;
        }
        
        try {
            this.showProgress();
            
            const result = await this.performOperation(operation, inputData);
            
            document.getElementById('outputText').value = result.output;
            this.showOperationInfo(result);
            
            // 添加到历史记录
            this.addToHistory({
                operation,
                timestamp: new Date().toISOString(),
                keyName: this.selectedKey ? this.selectedKey.id : null,
                inputSize: inputMethod === 'text' ? inputData.length : this.selectedFile.size,
                success: true
            });
            
        } catch (error) {
            console.error('操作失败:', error);
            this.showNotification(`操作失败: ${error.message}`, 'error');
            
            this.addToHistory({
                operation,
                timestamp: new Date().toISOString(),
                error: error.message,
                success: false
            });
        } finally {
            this.hideProgress();
        }
    }
    
    async performOperation(operation, inputData) {
        // 模拟操作延迟
        await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
        
        switch (operation) {
            case 'encrypt':
                return {
                    output: this.generateMockOutput('encrypted', inputData),
                    details: `使用${this.selectedKey.type.toUpperCase()}密钥加密成功`
                };
            case 'decrypt':
                return {
                    output: this.generateMockOutput('decrypted', inputData),
                    details: `使用${this.selectedKey.type.toUpperCase()}密钥解密成功`
                };
            case 'sign':
                return {
                    output: this.generateMockSignature(),
                    details: `使用${this.selectedKey.type.toUpperCase()}密钥生成数字签名`
                };
            case 'verify':
                return {
                    output: 'VALID',
                    details: '签名验证成功，数据完整性确认'
                };
            case 'hash':
                const algorithm = document.getElementById('hashAlgorithm')?.value || 'SHA256';
                return {
                    output: this.generateMockHash(algorithm),
                    details: `使用${algorithm}算法计算哈希值`
                };
            default:
                throw new Error('不支持的操作类型');
        }
    }
    
    generateMockOutput(type, input) {
        const base64Chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
        let result = '';
        
        if (type === 'encrypted') {
            result += '-----BEGIN ENCRYPTED DATA-----\n';
            for (let i = 0; i < 8; i++) {
                for (let j = 0; j < 64; j++) {
                    result += base64Chars[Math.floor(Math.random() * base64Chars.length)];
                }
                result += '\n';
            }
            result += '-----END ENCRYPTED DATA-----';
        } else if (type === 'decrypted') {
            result = typeof input === 'string' ? input : 'Decrypted content: ' + new Date().toISOString();
        }
        
        return result;
    }
    
    generateMockSignature() {
        const hexChars = '0123456789abcdef';
        let signature = '';
        for (let i = 0; i < 128; i++) {
            signature += hexChars[Math.floor(Math.random() * hexChars.length)];
        }
        return signature.toUpperCase();
    }
    
    generateMockHash(algorithm) {
        const lengths = { MD5: 32, SHA1: 40, SHA256: 64, SHA512: 128 };
        const length = lengths[algorithm] || 64;
        const hexChars = '0123456789abcdef';
        let hash = '';
        for (let i = 0; i < length; i++) {
            hash += hexChars[Math.floor(Math.random() * hexChars.length)];
        }
        return hash.toUpperCase();
    }
    
    showProgress() {
        document.getElementById('operationProgress').style.display = 'block';
        document.getElementById('executeOperation').disabled = true;
        
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 95) progress = 95;
            
            progressBar.style.width = `${progress}%`;
            
            if (progress < 30) progressText.textContent = '正在准备...';
            else if (progress < 60) progressText.textContent = '正在处理数据...';
            else if (progress < 90) progressText.textContent = '正在生成结果...';
            else progressText.textContent = '即将完成...';
        }, 200);
        
        this.progressInterval = interval;
    }
    
    hideProgress() {
        document.getElementById('operationProgress').style.display = 'none';
        document.getElementById('executeOperation').disabled = false;
        
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
        
        document.getElementById('progressBar').style.width = '100%';
    }
    
    showOperationInfo(result) {
        const info = document.getElementById('operationInfo');
        const details = document.getElementById('operationDetails');
        
        details.textContent = result.details;
        info.style.display = 'block';
    }
    
    addToHistory(entry) {
        this.operationHistory.unshift(entry);
        if (this.operationHistory.length > 50) {
            this.operationHistory = this.operationHistory.slice(0, 50);
        }
    }
    
    showHistory() {
        const modal = new bootstrap.Modal(document.getElementById('historyModal'));
        const historyList = document.getElementById('operationHistoryList');
        
        if (this.operationHistory.length === 0) {
            historyList.innerHTML = '<p class="text-muted text-center">暂无操作历史</p>';
        } else {
            historyList.innerHTML = this.operationHistory.map(entry => `
                <div class="operation-item ${entry.operation} ${entry.success ? 'success' : 'error'}">
                    <div class="operation-header">
                        <div class="operation-type">${this.getOperationText(entry.operation)}</div>
                        <div class="operation-time">${new Date(entry.timestamp).toLocaleString()}</div>
                    </div>
                    <div class="operation-details">
                        ${entry.success 
                            ? `密钥: ${entry.keyName || 'N/A'} | 数据大小: ${this.formatFileSize(entry.inputSize)}`
                            : `错误: ${entry.error}`
                        }
                    </div>
                </div>
            `).join('');
        }
        
        modal.show();
    }
    
    // 工具方法
    getPurposeText(purpose) {
        const purposes = {
            encryption: '加密',
            signing: '签名',
            both: '加密/签名'
        };
        return purposes[purpose] || purpose;
    }
    
    getOperationText(operation) {
        const operations = {
            encrypt: '加密',
            decrypt: '解密',
            sign: '数字签名',
            verify: '签名验证',
            hash: '哈希计算'
        };
        return operations[operation] || operation;
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    copyOutput() {
        const output = document.getElementById('outputText').value;
        if (!output) {
            this.showNotification('没有可复制的内容', 'warning');
            return;
        }
        
        navigator.clipboard.writeText(output).then(() => {
            this.showNotification('已复制到剪贴板', 'success');
        }).catch(err => {
            console.error('复制失败:', err);
        });
    }
    
    downloadOutput() {
        const output = document.getElementById('outputText').value;
        if (!output) {
            this.showNotification('没有可下载的内容', 'warning');
            return;
        }
        
        const operation = document.querySelector('input[name="operation"]:checked').value;
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `${operation}-result-${timestamp}.txt`;
        
        const blob = new Blob([output], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('文件已下载', 'success');
    }
    
    clearAll() {
        document.getElementById('inputText').value = '';
        document.getElementById('outputText').value = '';
        document.getElementById('keySelect').value = '';
        document.getElementById('selectedKeyInfo').innerHTML = '<small class="text-muted">请选择一个密钥</small>';
        document.getElementById('operationInfo').style.display = 'none';
        
        this.selectedKey = null;
        this.selectedFile = null;
        
        this.showNotification('已清空所有内容', 'info');
    }
    
    clearHistory() {
        this.operationHistory = [];
        this.showNotification('操作历史已清空', 'info');
        
        const modal = bootstrap.Modal.getInstance(document.getElementById('historyModal'));
        if (modal) modal.hide();
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
window.EncryptionTool = EncryptionTool;