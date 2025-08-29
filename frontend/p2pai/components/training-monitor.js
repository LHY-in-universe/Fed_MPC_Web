/**
 * AI训练监控组件
 * 实时显示训练进度、损失值、准确率等指标
 */

class TrainingMonitor {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.sessionId = null;
        this.chart = null;
        this.updateInterval = null;
        
        this.init();
    }
    
    init() {
        this.createLayout();
        this.initChart();
    }
    
    createLayout() {
        this.container.innerHTML = `
            <div class="training-monitor">
                <div class="monitor-header">
                    <h3>训练监控</h3>
                    <div class="monitor-controls">
                        <button id="startTraining" class="btn btn-primary">开始训练</button>
                        <button id="stopTraining" class="btn btn-danger" disabled>停止训练</button>
                        <button id="pauseTraining" class="btn btn-warning" disabled>暂停训练</button>
                    </div>
                </div>
                
                <div class="monitor-stats">
                    <div class="stat-card">
                        <div class="stat-label">当前轮次</div>
                        <div class="stat-value" id="currentEpoch">0</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">准确率</div>
                        <div class="stat-value" id="accuracy">0.00%</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">损失值</div>
                        <div class="stat-value" id="loss">0.000</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">训练时长</div>
                        <div class="stat-value" id="duration">00:00:00</div>
                    </div>
                </div>
                
                <div class="monitor-chart">
                    <canvas id="trainingChart" width="800" height="400"></canvas>
                </div>
                
                <div class="monitor-logs">
                    <h4>训练日志</h4>
                    <div class="log-container" id="trainingLogs"></div>
                </div>
            </div>
        `;
        
        this.bindEvents();
    }
    
    initChart() {
        const ctx = document.getElementById('trainingChart').getContext('2d');
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '准确率',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.1,
                    yAxisID: 'y'
                }, {
                    label: '损失值',
                    data: [],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    tension: 0.1,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: '训练轮次'
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: '准确率'
                        },
                        min: 0,
                        max: 1
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: '损失值'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                }
            }
        });
    }
    
    bindEvents() {
        document.getElementById('startTraining').addEventListener('click', () => this.startTraining());
        document.getElementById('stopTraining').addEventListener('click', () => this.stopTraining());
        document.getElementById('pauseTraining').addEventListener('click', () => this.pauseTraining());
    }
    
    async startTraining() {
        try {
            // 获取训练配置
            const config = this.getTrainingConfig();
            
            // 调用后端API开始训练
            const response = await fetch('/api/ai/training/local/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(config)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.sessionId = result.data.session_id;
                this.updateControls(true);
                this.startMonitoring();
                this.addLog('训练已开始', 'success');
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('开始训练失败:', error);
            this.addLog(`训练启动失败: ${error.message}`, 'error');
        }
    }
    
    async stopTraining() {
        if (!this.sessionId) return;
        
        try {
            const response = await fetch(`/api/ai/training/local/stop/${this.sessionId}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.stopMonitoring();
                this.updateControls(false);
                this.addLog('训练已停止', 'warning');
            }
        } catch (error) {
            console.error('停止训练失败:', error);
            this.addLog(`停止训练失败: ${error.message}`, 'error');
        }
    }
    
    async pauseTraining() {
        if (!this.sessionId) return;
        
        try {
            const response = await fetch(`/api/ai/training/local/pause/${this.sessionId}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.addLog('训练已暂停', 'info');
            }
        } catch (error) {
            console.error('暂停训练失败:', error);
            this.addLog(`暂停训练失败: ${error.message}`, 'error');
        }
    }
    
    startMonitoring() {
        this.updateInterval = setInterval(() => {
            this.updateTrainingStatus();
        }, 2000); // 每2秒更新一次
    }
    
    stopMonitoring() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
    
    async updateTrainingStatus() {
        if (!this.sessionId) return;
        
        try {
            const response = await fetch(`/api/ai/training/local/status/${this.sessionId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.updateUI(result.data);
            }
        } catch (error) {
            console.error('更新训练状态失败:', error);
        }
    }
    
    updateUI(data) {
        // 更新统计信息
        document.getElementById('currentEpoch').textContent = `${data.current_round}/${data.total_rounds}`;
        document.getElementById('accuracy').textContent = `${(data.accuracy * 100).toFixed(2)}%`;
        document.getElementById('loss').textContent = data.loss.toFixed(4);
        
        // 更新训练时长
        if (data.started_at) {
            const duration = this.calculateDuration(data.started_at);
            document.getElementById('duration').textContent = duration;
        }
        
        // 更新图表
        this.updateChart(data);
        
        // 检查训练状态
        if (data.status === 'completed') {
            this.stopMonitoring();
            this.updateControls(false);
            this.addLog('训练已完成', 'success');
        } else if (data.status === 'failed') {
            this.stopMonitoring();
            this.updateControls(false);
            this.addLog('训练失败', 'error');
        }
    }
    
    updateChart(data) {
        const labels = this.chart.data.labels;
        const accuracyData = this.chart.data.datasets[0].data;
        const lossData = this.chart.data.datasets[1].data;
        
        // 添加新数据点
        if (data.current_round > 0 && !labels.includes(data.current_round)) {
            labels.push(data.current_round);
            accuracyData.push(data.accuracy);
            lossData.push(data.loss);
            
            // 保持最多显示100个数据点
            if (labels.length > 100) {
                labels.shift();
                accuracyData.shift();
                lossData.shift();
            }
            
            this.chart.update('none');
        }
    }
    
    updateControls(isTraining) {
        document.getElementById('startTraining').disabled = isTraining;
        document.getElementById('stopTraining').disabled = !isTraining;
        document.getElementById('pauseTraining').disabled = !isTraining;
    }
    
    addLog(message, type = 'info') {
        const logsContainer = document.getElementById('trainingLogs');
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry log-${type}`;
        logEntry.innerHTML = `<span class="log-time">${timestamp}</span> <span class="log-message">${message}</span>`;
        
        logsContainer.appendChild(logEntry);
        logsContainer.scrollTop = logsContainer.scrollHeight;
        
        // 保持最多50条日志
        while (logsContainer.children.length > 50) {
            logsContainer.removeChild(logsContainer.firstChild);
        }
    }
    
    getTrainingConfig() {
        // 这里应该从表单或配置界面获取训练参数
        return {
            model_type: 'cnn',
            learning_rate: 0.001,
            epochs: 100,
            batch_size: 32,
            dataset_id: 'default_dataset'
        };
    }
    
    calculateDuration(startTime) {
        const start = new Date(startTime);
        const now = new Date();
        const diff = now - start;
        
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);
        
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    
    destroy() {
        this.stopMonitoring();
        if (this.chart) {
            this.chart.destroy();
        }
    }
}

// 导出组件
window.TrainingMonitor = TrainingMonitor;