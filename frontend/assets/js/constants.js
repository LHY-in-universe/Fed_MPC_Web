/**
 * 联邦学习平台 - 常量定义
 * 定义全局常量和配置信息
 */

const FedConstants = {
    
    /**
     * 应用基本信息
     */
    APP: {
        NAME: '联邦学习平台',
        VERSION: '1.0.0',
        AUTHOR: 'Fed_MPC_Web Team',
        DESCRIPTION: '基于Web的联邦学习平台，支持AI大模型和金融区块链业务',
        COPYRIGHT: '© 2024 Fed_MPC_Web. All rights reserved.'
    },

    /**
     * API端点配置
     */
    API: {
        BASE_URL: 'http://localhost:5000/api',
        TIMEOUT: 30000,
        RETRY_COUNT: 3,
        ENDPOINTS: {
            // 认证接口
            AUTH: {
                LOGIN: '/auth/login',
                LOGOUT: '/auth/logout',
                VERIFY: '/auth/verify',
                REFRESH: '/auth/refresh',
                REGISTER: '/auth/register',
                CHANGE_PASSWORD: '/auth/change-password'
            },
            
            // 客户端接口
            CLIENT: {
                PROJECTS: '/client/projects',
                PROJECT_DETAIL: '/client/projects/{id}',
                TRAINING_REQUESTS: '/client/training-requests',
                TRAINING_DATA: '/client/training-data/{id}'
            },
            
            // 服务器接口
            SERVER: {
                DASHBOARD: '/server/dashboard',
                CLIENTS: '/server/clients',
                CLIENT_DETAIL: '/server/clients/{id}',
                APPROVE_REQUEST: '/server/training-requests/{id}/approve',
                REJECT_REQUEST: '/server/training-requests/{id}/reject',
                MODELS: '/server/models',
                CONFIG: '/server/system/config'
            },
            
            // 训练接口
            TRAINING: {
                SESSIONS: '/training/sessions',
                SESSION_DETAIL: '/training/sessions/{id}',
                START_SESSION: '/training/sessions/{id}/start',
                STOP_SESSION: '/training/sessions/{id}/stop',
                SUBMIT_ROUND: '/training/sessions/{id}/round',
                SESSION_LOGS: '/training/sessions/{id}/logs',
                HEARTBEAT: '/training/sessions/{id}/heartbeat',
                STATISTICS: '/training/statistics'
            },
            
            // 系统接口
            SYSTEM: {
                HEALTH: '/health',
                STATUS: '/status'
            }
        }
    },

    /**
     * 业务类型配置
     */
    BUSINESS_TYPES: {
        AI: {
            key: 'ai',
            name: 'AI大模型业务',
            description: '深度学习模型训练、自然语言处理、计算机视觉等AI应用的联邦学习',
            icon: 'lightbulb',
            color: {
                primary: '#6b7280',
                secondary: '#9ca3af',
                gradient: 'linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%)'
            },
            models: [
                { name: 'ResNet-50', type: 'CNN' },
                { name: 'BERT-Base', type: 'Transformer' },
                { name: 'YOLOv5', type: 'Detection' }
            ]
        },
        BLOCKCHAIN: {
            key: 'blockchain',
            name: '金融区块链业务',
            description: '基于区块链的金融数据分析、风险评估、智能合约等应用的安全联邦学习',
            icon: 'currency-dollar',
            color: {
                primary: '#374151',
                secondary: '#4b5563',
                gradient: 'linear-gradient(135deg, #e5e7eb 0%, #d1d5db 100%)'
            },
            models: [
                { name: 'FinNet-Risk', type: 'Risk Assessment' },
                { name: 'AML-Detector', type: 'Anti Money Laundering' },
                { name: 'Credit-Score', type: 'Credit Scoring' }
            ]
        }
    },

    /**
     * 用户角色配置
     */
    USER_TYPES: {
        CLIENT: {
            key: 'client',
            name: '客户端',
            description: '参与联邦学习训练的客户端用户',
            permissions: [
                'create_local_project',
                'view_own_projects',
                'submit_training_request',
                'view_training_progress'
            ]
        },
        SERVER: {
            key: 'server',
            name: '总服务器管理员',
            description: '管理整个联邦学习平台的管理员用户',
            permissions: [
                'manage_all_clients',
                'approve_training_requests',
                'view_global_projects',
                'manage_models',
                'system_configuration'
            ]
        }
    },

    /**
     * 训练模式配置
     */
    TRAINING_MODES: {
        NORMAL: {
            key: 'normal',
            name: '普通训练',
            icon: '👁',
            description: '训练过程透明，总服务器可查看详细训练数据',
            features: [
                '训练过程透明',
                '实时监控准确率和损失',
                '完整的训练日志',
                '高效的模型聚合'
            ],
            privacy_level: 'low',
            performance: 'high',
            suitable_for: ['数据隐私要求不高的场景', '需要详细监控的项目', '快速验证模型效果']
        },
        MPC: {
            key: 'mpc',
            name: 'MPC安全多方计算',
            icon: '🔒',
            description: '使用安全多方计算技术，保护参与方数据隐私',
            features: [
                '数据隐私保护',
                '加密计算过程',
                '防止数据泄露',
                '支持多方协作'
            ],
            privacy_level: 'high',
            performance: 'medium',
            suitable_for: ['金融敏感数据', '医疗健康数据', '商业机密信息']
        }
    },

    /**
     * 项目状态配置
     */
    PROJECT_STATUS: {
        CREATED: {
            key: 'created',
            name: '已创建',
            color: '#6b7280',
            description: '项目已创建，尚未开始训练'
        },
        RUNNING: {
            key: 'running',
            name: '运行中',
            color: '#10b981',
            description: '项目正在进行训练'
        },
        PAUSED: {
            key: 'paused',
            name: '已暂停',
            color: '#f59e0b',
            description: '项目训练已暂停'
        },
        COMPLETED: {
            key: 'completed',
            name: '已完成',
            color: '#3b82f6',
            description: '项目训练已完成'
        },
        WAITING_APPROVAL: {
            key: 'waiting_approval',
            name: '等待审批',
            color: '#f59e0b',
            description: '联合训练申请等待总服务器审批'
        },
        APPROVED: {
            key: 'approved',
            name: '已批准',
            color: '#10b981',
            description: '联合训练申请已获批准'
        },
        REJECTED: {
            key: 'rejected',
            name: '已拒绝',
            color: '#ef4444',
            description: '联合训练申请已被拒绝'
        },
        STOPPED: {
            key: 'stopped',
            name: '已停止',
            color: '#6b7280',
            description: '项目训练已停止'
        }
    },

    /**
     * 节点状态配置
     */
    NODE_STATUS: {
        ONLINE: {
            key: 'online',
            name: '在线',
            color: '#10b981',
            icon: '●'
        },
        OFFLINE: {
            key: 'offline',
            name: '离线',
            color: '#6b7280',
            icon: '●'
        },
        TRAINING: {
            key: 'training',
            name: '训练中',
            color: '#3b82f6',
            icon: '●'
        },
        WAITING: {
            key: 'waiting',
            name: '等待',
            color: '#f59e0b',
            icon: '●'
        },
        ERROR: {
            key: 'error',
            name: '错误',
            color: '#ef4444',
            icon: '●'
        }
    },

    /**
     * 本地存储键名
     */
    STORAGE_KEYS: {
        USER_DATA: 'userData',
        BUSINESS_TYPE: 'businessType',
        CLIENT_PROJECTS: 'clientProjects',
        REMEMBER_CLIENT: 'rememberClient',
        REMEMBER_SERVER: 'rememberServer',
        THEME_PREFERENCE: 'themePreference',
        LANGUAGE_PREFERENCE: 'languagePreference',
        LAST_LOGIN: 'lastLogin'
    },

    /**
     * 默认配置值
     */
    DEFAULTS: {
        // 训练参数
        TRAINING: {
            MAX_ROUNDS: 1000,
            DEFAULT_ROUNDS: 100,
            MIN_PARTICIPANTS: 2,
            MAX_PARTICIPANTS: 100,
            HEARTBEAT_INTERVAL: 30000, // 30秒
            SESSION_TIMEOUT: 3600000   // 1小时
        },
        
        // 分页参数
        PAGINATION: {
            PAGE_SIZE: 20,
            MAX_PAGE_SIZE: 100
        },
        
        // 文件上传
        FILE_UPLOAD: {
            MAX_SIZE: 1024 * 1024 * 1024, // 1GB
            ALLOWED_TYPES: ['py', 'pkl', 'pth', 'h5', 'onnx', 'pb'],
            CHUNK_SIZE: 1024 * 1024 // 1MB
        },
        
        // 图表配置
        CHART: {
            ANIMATION_DURATION: 1000,
            REFRESH_INTERVAL: 2000,
            MAX_DATA_POINTS: 1000
        }
    },

    /**
     * 演示数据配置
     */
    DEMO: {
        CLIENTS: {
            AI: [
                { name: '上海一厂', address: 'http://shanghai.client.com' },
                { name: '武汉二厂', address: 'http://wuhan.client.com' },
                { name: '西安三厂', address: 'http://xian.client.com' },
                { name: '广州四厂', address: 'http://guangzhou.client.com' }
            ],
            BLOCKCHAIN: [
                { name: '工商银行', address: 'http://icbc.bank.com' },
                { name: '建设银行', address: 'http://ccb.bank.com' },
                { name: '招商银行', address: 'http://cmb.bank.com' }
            ]
        },
        
        ADMINS: {
            AI: [
                { id: 'admin', name: 'AI管理员' },
                { id: 'demo-admin', name: '演示管理员' }
            ],
            BLOCKCHAIN: [
                { id: 'blockchain-admin', name: '区块链管理员' },
                { id: 'demo-admin', name: '演示管理员' }
            ]
        }
    },

    /**
     * 错误消息配置
     */
    ERROR_MESSAGES: {
        NETWORK_ERROR: '网络连接错误，请检查网络设置',
        TIMEOUT_ERROR: '请求超时，请稍后重试',
        AUTH_FAILED: '身份认证失败，请重新登录',
        PERMISSION_DENIED: '权限不足，无法执行此操作',
        DATA_NOT_FOUND: '请求的数据不存在',
        INVALID_INPUT: '输入数据格式不正确',
        SERVER_ERROR: '服务器内部错误，请联系管理员',
        SESSION_EXPIRED: '会话已过期，请重新登录'
    },

    /**
     * 成功消息配置
     */
    SUCCESS_MESSAGES: {
        LOGIN_SUCCESS: '登录成功',
        LOGOUT_SUCCESS: '登出成功',
        PROJECT_CREATED: '项目创建成功',
        PROJECT_UPDATED: '项目更新成功',
        REQUEST_SUBMITTED: '申请提交成功',
        REQUEST_APPROVED: '申请已批准',
        REQUEST_REJECTED: '申请已拒绝',
        TRAINING_STARTED: '训练已开始',
        TRAINING_STOPPED: '训练已停止'
    },

    /**
     * 验证规则
     */
    VALIDATION: {
        USERNAME: {
            MIN_LENGTH: 2,
            MAX_LENGTH: 50,
            PATTERN: /^[a-zA-Z0-9\u4e00-\u9fa5_-]+$/
        },
        PASSWORD: {
            MIN_LENGTH: 6,
            MAX_LENGTH: 128
        },
        PROJECT_NAME: {
            MIN_LENGTH: 1,
            MAX_LENGTH: 100
        },
        PROJECT_DESCRIPTION: {
            MAX_LENGTH: 500
        },
        URL: {
            PATTERN: /^https?:\/\/.+/
        }
    },

    /**
     * 时间格式配置
     */
    TIME_FORMATS: {
        DATETIME: 'YYYY-MM-DD HH:mm:ss',
        DATE: 'YYYY-MM-DD',
        TIME: 'HH:mm:ss',
        TIMESTAMP: 'YYYY-MM-DD HH:mm:ss.SSS'
    }
};

// 冻结常量对象，防止修改
Object.freeze(FedConstants);

// 导出到全局
if (typeof window !== 'undefined') {
    window.FedConstants = FedConstants;
}

// 模块化导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FedConstants;
}