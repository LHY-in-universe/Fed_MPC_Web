/**
 * 联邦学习平台 - Chart.js 配置
 * 提供统一的图表配置和主题
 */

const ChartConfig = {
    
    /**
     * 默认配置
     */
    defaults: {
        responsive: true,
        maintainAspectRatio: false,
        font: {
            family: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
        },
        plugins: {
            legend: {
                display: true,
                position: 'top',
                labels: {
                    padding: 20,
                    usePointStyle: true,
                    pointStyle: 'circle'
                }
            },
            tooltip: {
                enabled: true,
                mode: 'index',
                intersect: false,
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                titleColor: 'white',
                bodyColor: 'white',
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 1,
                cornerRadius: 8,
                padding: 12
            }
        },
        scales: {
            x: {
                grid: {
                    display: false,
                    color: 'rgba(0, 0, 0, 0.05)'
                },
                ticks: {
                    color: '#64748b',
                    font: {
                        size: 12
                    }
                }
            },
            y: {
                grid: {
                    color: 'rgba(0, 0, 0, 0.05)',
                    drawBorder: false
                },
                ticks: {
                    color: '#64748b',
                    font: {
                        size: 12
                    },
                    padding: 8
                }
            }
        },
        elements: {
            point: {
                radius: 4,
                hoverRadius: 6,
                borderWidth: 2,
                hoverBorderWidth: 3
            },
            line: {
                tension: 0.4,
                borderWidth: 3,
                fill: false
            }
        },
        animation: {
            duration: 1000,
            easing: 'easeInOutQuart'
        }
    },

    /**
     * 业务主题配色 - 科创企业灰色调
     */
    themes: {
        ai: {
            primary: '#6b7280',
            secondary: '#9ca3af',
            gradient: ['#6b7280', '#9ca3af', '#d1d5db', '#4b5563'],
            success: '#059669',
            warning: '#d97706',
            error: '#dc2626',
            info: '#2563eb'
        },
        blockchain: {
            primary: '#374151',
            secondary: '#4b5563',
            gradient: ['#374151', '#4b5563', '#6b7280', '#1f2937'],
            success: '#059669',
            warning: '#d97706',
            error: '#dc2626',
            info: '#2563eb'
        }
    },

    /**
     * 获取当前主题配色
     * @returns {Object} 主题配色对象
     */
    getCurrentTheme() {
        const businessType = localStorage.getItem('businessType') || 'ai';
        return this.themes[businessType];
    },

    /**
     * 训练准确率图表配置
     * @param {Array} labels - 标签数据
     * @param {Array} data - 数据点
     * @param {string} businessType - 业务类型
     * @returns {Object} Chart.js配置对象
     */
    createAccuracyChart(labels, data, businessType = 'ai') {
        const theme = this.themes[businessType];
        
        return {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: window.i18nManager?.getCurrentLanguage() === 'en' ? 'Model Accuracy' : '模型准确率',
                    data: data,
                    borderColor: theme.primary,
                    backgroundColor: this.createGradient(theme.primary, 0.1),
                    pointBackgroundColor: theme.primary,
                    pointBorderColor: '#ffffff',
                    pointHoverBackgroundColor: theme.secondary,
                    pointHoverBorderColor: '#ffffff',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                ...this.defaults,
                scales: {
                    ...this.defaults.scales,
                    y: {
                        ...this.defaults.scales.y,
                        beginAtZero: false,
                        min: 0.5,
                        max: 1.0,
                        ticks: {
                            ...this.defaults.scales.y.ticks,
                            callback: function(value) {
                                return (value * 100).toFixed(0) + '%';
                            }
                        }
                    },
                    x: {
                        ...this.defaults.scales.x,
                        title: {
                            display: true,
                            text: window.i18nManager?.getCurrentLanguage() === 'en' ? 'Training Rounds' : '训练轮次 (Rounds)',
                            color: '#475569',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        }
                    }
                },
                plugins: {
                    ...this.defaults.plugins,
                    legend: {
                        display: false
                    },
                    tooltip: {
                        ...this.defaults.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                const isEn = window.i18nManager?.getCurrentLanguage() === 'en';
                                return isEn ? `Accuracy: ${(context.parsed.y * 100).toFixed(2)}%` : `准确率: ${(context.parsed.y * 100).toFixed(2)}%`;
                            }
                        }
                    }
                }
            }
        };
    },

    /**
     * 损失函数图表配置
     * @param {Array} labels - 标签数据
     * @param {Array} data - 数据点
     * @param {string} businessType - 业务类型
     * @returns {Object} Chart.js配置对象
     */
    createLossChart(labels, data, businessType = 'ai') {
        const theme = this.themes[businessType];
        
        return {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '模型损失',
                    data: data,
                    borderColor: theme.error,
                    backgroundColor: this.createGradient(theme.error, 0.1),
                    pointBackgroundColor: theme.error,
                    pointBorderColor: '#ffffff',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                ...this.defaults,
                scales: {
                    ...this.defaults.scales,
                    y: {
                        ...this.defaults.scales.y,
                        beginAtZero: true,
                        ticks: {
                            ...this.defaults.scales.y.ticks,
                            callback: function(value) {
                                return value.toFixed(3);
                            }
                        }
                    }
                },
                plugins: {
                    ...this.defaults.plugins,
                    tooltip: {
                        ...this.defaults.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                return `损失: ${context.parsed.y.toFixed(4)}`;
                            }
                        }
                    }
                }
            }
        };
    },

    /**
     * 节点状态分布饼图配置
     * @param {Array} data - 数据
     * @param {string} businessType - 业务类型
     * @returns {Object} Chart.js配置对象
     */
    createNodeStatusChart(data, businessType = 'ai') {
        const theme = this.themes[businessType];
        
        return {
            type: 'doughnut',
            data: {
                labels: window.i18nManager?.getCurrentLanguage() === 'en' ? ['Online', 'Offline', 'Training'] : ['在线', '离线', '训练中'],
                datasets: [{
                    data: data,
                    backgroundColor: [
                        theme.success,
                        '#6b7280',
                        theme.primary
                    ],
                    borderColor: '#ffffff',
                    borderWidth: 2,
                    hoverBorderWidth: 3
                }]
            },
            options: {
                ...this.defaults,
                cutout: '60%',
                plugins: {
                    ...this.defaults.plugins,
                    legend: {
                        ...this.defaults.plugins.legend,
                        position: 'bottom',
                        labels: {
                            ...this.defaults.plugins.legend.labels,
                            padding: 15
                        }
                    },
                    tooltip: {
                        ...this.defaults.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.raw / total) * 100).toFixed(1);
                                return `${context.label}: ${context.raw} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        };
    },

    /**
     * 多指标对比图表配置
     * @param {Array} labels - 标签数据
     * @param {Array} datasets - 数据集
     * @param {string} businessType - 业务类型
     * @returns {Object} Chart.js配置对象
     */
    createMultiMetricChart(labels, datasets, businessType = 'ai') {
        const theme = this.themes[businessType];
        const colors = theme.gradient;
        
        const processedDatasets = datasets.map((dataset, index) => ({
            ...dataset,
            borderColor: colors[index % colors.length],
            backgroundColor: this.createGradient(colors[index % colors.length], 0.1),
            pointBackgroundColor: colors[index % colors.length],
            pointBorderColor: '#ffffff',
            fill: false,
            tension: 0.4
        }));

        return {
            type: 'line',
            data: {
                labels: labels,
                datasets: processedDatasets
            },
            options: {
                ...this.defaults,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    ...this.defaults.plugins,
                    legend: {
                        ...this.defaults.plugins.legend,
                        display: true
                    }
                }
            }
        };
    },

    /**
     * 创建渐变色
     * @param {string} color - 基础颜色
     * @param {number} opacity - 透明度
     * @returns {string} 渐变色字符串
     */
    createGradient(color, opacity = 0.2) {
        // 这里返回颜色字符串，在实际使用时需要在canvas context中创建gradient
        return color + Math.floor(opacity * 255).toString(16).padStart(2, '0');
    },

    /**
     * 创建Canvas渐变
     * @param {CanvasRenderingContext2D} ctx - Canvas上下文
     * @param {string} color1 - 起始颜色
     * @param {string} color2 - 结束颜色
     * @param {number} height - 高度
     * @returns {CanvasGradient} Canvas渐变对象
     */
    createCanvasGradient(ctx, color1, color2, height = 400) {
        const gradient = ctx.createLinearGradient(0, 0, 0, height);
        gradient.addColorStop(0, color1);
        gradient.addColorStop(1, color2);
        return gradient;
    },

    /**
     * 更新图表主题
     * @param {Chart} chart - Chart.js实例
     * @param {string} businessType - 业务类型
     */
    updateChartTheme(chart, businessType) {
        const theme = this.themes[businessType];
        
        // 更新数据集颜色
        chart.data.datasets.forEach((dataset, index) => {
            const colors = theme.gradient;
            dataset.borderColor = colors[index % colors.length];
            dataset.backgroundColor = this.createGradient(colors[index % colors.length], 0.1);
            dataset.pointBackgroundColor = colors[index % colors.length];
        });
        
        chart.update('none');
    },

    /**
     * 动画配置预设
     */
    animations: {
        smooth: {
            duration: 1500,
            easing: 'easeInOutCubic'
        },
        fast: {
            duration: 500,
            easing: 'easeOutQuart'
        },
        bounce: {
            duration: 1000,
            easing: 'easeOutBounce'
        }
    }
};

// 设置Chart.js全局默认配置
if (typeof Chart !== 'undefined') {
    Chart.defaults.font.family = ChartConfig.defaults.font.family;
    Chart.defaults.animation.duration = ChartConfig.defaults.animation.duration;
    Chart.defaults.animation.easing = ChartConfig.defaults.animation.easing;
}

// 导出到全局
if (typeof window !== 'undefined') {
    window.ChartConfig = ChartConfig;
}

// 模块化导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChartConfig;
}