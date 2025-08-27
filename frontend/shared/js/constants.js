/**
 * 联邦学习平台 - 统一常量定义
 * 合并通用常量和各模块专用常量
 */

const UnifiedConstants = {
    
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
            
            // AI模块接口
            AI: {
                PROJECTS: '/ai/projects',
                MODELS: '/ai/models',
                DATASETS: '/ai/datasets',
                TRAINING_SESSIONS: '/ai/training/sessions'
            },
            
            // 区块链模块接口
            BLOCKCHAIN: {
                TRANSACTIONS: '/blockchain/transactions',
                CONTRACTS: '/blockchain/contracts',
                NETWORK_STATUS: '/blockchain/network/status'
            },
            
            // 密钥加密模块接口
            CRYPTO: {
                KEYS: '/crypto/keys',
                CERTIFICATES: '/crypto/certificates',
                OPERATIONS: '/crypto/operations'
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
                primary: '#3b82f6',
                secondary: '#1d4ed8',
                gradient: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)'
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
                primary: '#059669',
                secondary: '#047857',
                gradient: 'linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)'
            },
            models: [
                { name: 'FinNet-Risk', type: 'Risk Assessment' },
                { name: 'AML-Detector', type: 'Anti Money Laundering' },
                { name: 'Credit-Score', type: 'Credit Scoring' }
            ]
        },
        CRYPTO: {
            key: 'crypto',
            name: '密钥加密签名模块',
            description: '提供密钥管理、数据加密和数字签名功能',
            icon: 'shield-check',
            color: {
                primary: '#8b5cf6',
                secondary: '#6d28d9',
                gradient: 'linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%)'
            }
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
     * 密钥类型配置
     */
    KEY_TYPES: {
        RSA: {
            key: 'rsa',
            name: 'RSA密钥',
            description: '非对称加密，支持加密和数字签名',
            icon: 'key',
            sizes: [1024, 2048, 3072, 4096],
            defaultSize: 2048,
            usages: ['encryption', 'signing', 'both']
        },
        ECC: {
            key: 'ecc',
            name: 'ECC椭圆曲线',
            description: '高效的椭圆曲线加密，安全性高',
            icon: 'trending-up',
            sizes: [256, 384, 521],
            defaultSize: 256,
            usages: ['signing', 'encryption']
        },
        AES: {
            key: 'aes',
            name: 'AES对称密钥',
            description: '高效的对称加密算法',
            icon: 'lock-closed',
            sizes: [128, 192, 256],
            defaultSize: 256,
            usages: ['encryption']
        }
    },

    /**
     * 密钥用途配置
     */
    KEY_USAGES: {
        ENCRYPTION: {
            key: 'encryption',
            name: '加密',
            description: '用于数据加密和解密',
            icon: 'lock-closed',
            color: '#10b981'
        },
        SIGNING: {
            key: 'signing',
            name: '签名',
            description: '用于数字签名和验证',
            icon: 'pencil-alt',
            color: '#3b82f6'
        },
        BOTH: {
            key: 'both',
            name: '加密和签名',
            description: '可用于加密和签名操作',
            icon: 'shield-check',
            color: '#8b5cf6'
        }
    },

    /**
     * 密钥状态配置
     */
    KEY_STATUS: {
        ACTIVE: {
            key: 'active',
            name: '活跃',
            color: '#10b981',
            icon: 'check-circle'
        },
        EXPIRED: {
            key: 'expired',
            name: '过期',
            color: '#f59e0b',
            icon: 'clock'
        },
        REVOKED: {
            key: 'revoked',
            name: '吊销',
            color: '#ef4444',
            icon: 'ban'
        },
        ARCHIVED: {
            key: 'archived',
            name: '归档',
            color: '#6b7280',
            icon: 'archive'
        }
    },

    /**
     * 签名算法配置
     */
    SIGNATURE_ALGORITHMS: {
        RSA_PKCS1: {
            key: 'rsa_pkcs1',
            name: 'RSA PKCS#1 v1.5',
            description: '经典的RSA签名算法',
            hashAlgorithms: ['sha256', 'sha384', 'sha512']
        },
        RSA_PSS: {
            key: 'rsa_pss',
            name: 'RSA PSS',
            description: '概率签名方案，更安全的RSA签名',
            hashAlgorithms: ['sha256', 'sha384', 'sha512']
        },
        ECDSA: {
            key: 'ecdsa',
            name: 'ECDSA',
            description: '椭圆曲线数字签名算法',
            hashAlgorithms: ['sha256', 'sha384', 'sha512']
        }
    },

    /**
     * 哈希算法配置
     */
    HASH_ALGORITHMS: {
        SHA256: {
            key: 'sha256',
            name: 'SHA-256',
            description: '256位安全哈希算法',
            outputSize: 32
        },
        SHA384: {
            key: 'sha384',
            name: 'SHA-384',
            description: '384位安全哈希算法',
            outputSize: 48
        },
        SHA512: {
            key: 'sha512',
            name: 'SHA-512',
            description: '512位安全哈希算法',
            outputSize: 64
        },
        SHA3_256: {
            key: 'sha3_256',
            name: 'SHA3-256',
            description: 'SHA-3 256位哈希算法',
            outputSize: 32
        }
    },

    /**
     * 证书类型配置
     */
    CERTIFICATE_TYPES: {
        ROOT_CA: {
            key: 'root_ca',
            name: '根证书',
            description: '证书颁发机构根证书',
            icon: 'shield',
            color: '#dc2626'
        },
        INTERMEDIATE_CA: {
            key: 'intermediate_ca',
            name: '中间证书',
            description: '中间证书颁发机构',
            icon: 'link',
            color: '#f59e0b'
        },
        END_ENTITY: {
            key: 'end_entity',
            name: '终端证书',
            description: '终端实体证书',
            icon: 'user',
            color: '#10b981'
        },
        CODE_SIGNING: {
            key: 'code_signing',
            name: '代码签名',
            description: '代码签名证书',
            icon: 'code',
            color: '#3b82f6'
        }
    },

    /**
     * 安全级别配置
     */
    SECURITY_LEVELS: {
        LOW: {
            key: 'low',
            name: '低级',
            description: '基本安全保护',
            color: '#f59e0b',
            requirements: {
                keySize: 1024,
                hashAlgorithm: 'sha256'
            }
        },
        MEDIUM: {
            key: 'medium',
            name: '中级',
            description: '标准安全保护',
            color: '#10b981',
            requirements: {
                keySize: 2048,
                hashAlgorithm: 'sha256'
            }
        },
        HIGH: {
            key: 'high',
            name: '高级',
            description: '强安全保护',
            color: '#3b82f6',
            requirements: {
                keySize: 3072,
                hashAlgorithm: 'sha384'
            }
        },
        MAXIMUM: {
            key: 'maximum',
            name: '最高级',
            description: '最强安全保护',
            color: '#8b5cf6',
            requirements: {
                keySize: 4096,
                hashAlgorithm: 'sha512'
            }
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
        LAST_LOGIN: 'lastLogin',
        AUTH_TOKEN: 'authToken'
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
        },
        
        // 密钥加密配置
        CRYPTO: {
            KEY_SIZE: 2048,
            HASH_ALGORITHM: 'sha256',
            MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
            CHUNK_SIZE: 1024 * 1024 // 1MB
        }
    },

    /**
     * 文件类型配置
     */
    FILE_TYPES: {
        SUPPORTED_ENCRYPTION: ['.txt', '.doc', '.docx', '.pdf', '.json', '.xml'],
        SUPPORTED_SIGNING: ['.txt', '.doc', '.docx', '.pdf', '.json', '.xml', '.zip'],
        SUPPORTED_DATASETS: ['.csv', '.json', '.h5', '.pkl', '.npz'],
        SUPPORTED_MODELS: ['.pth', '.h5', '.onnx', '.pb', '.pkl']
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
        },
        KEY_NAME: {
            MIN_LENGTH: 1,
            MAX_LENGTH: 100,
            PATTERN: /^[a-zA-Z0-9\u4e00-\u9fa5_\s-]+$/
        },
        PASSPHRASE: {
            MIN_LENGTH: 8,
            MAX_LENGTH: 128,
            REQUIRED_PATTERNS: [
                /[a-z]/,    // 小写字母
                /[A-Z]/,    // 大写字母
                /[0-9]/,    // 数字
                /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/ // 特殊字符
            ]
        },
        CERTIFICATE_DN: {
            REQUIRED_FIELDS: ['CN'],
            OPTIONAL_FIELDS: ['O', 'OU', 'C', 'ST', 'L', 'EMAIL']
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
            ],
            CRYPTO: [
                { id: 'crypto-admin', name: '密钥管理员' },
                { id: 'demo-admin', name: '演示管理员' }
            ]
        }
    },

    /**
     * 错误消息配置
     */
    ERROR_MESSAGES: {
        // 通用错误
        NETWORK_ERROR: '网络连接错误，请检查网络设置',
        TIMEOUT_ERROR: '请求超时，请稍后重试',
        AUTH_FAILED: '身份认证失败，请重新登录',
        PERMISSION_DENIED: '权限不足，无法执行此操作',
        DATA_NOT_FOUND: '请求的数据不存在',
        INVALID_INPUT: '输入数据格式不正确',
        SERVER_ERROR: '服务器内部错误，请联系管理员',
        SESSION_EXPIRED: '会话已过期，请重新登录',
        
        // 密钥加密模块错误
        KEY_GENERATION_FAILED: '密钥生成失败',
        INVALID_PASSPHRASE: '密码格式不正确',
        KEY_NOT_FOUND: '密钥不存在',
        ENCRYPTION_FAILED: '加密操作失败',
        DECRYPTION_FAILED: '解密操作失败',
        SIGNATURE_FAILED: '签名操作失败',
        VERIFICATION_FAILED: '签名验证失败',
        CERTIFICATE_INVALID: '证书无效',
        CERTIFICATE_EXPIRED: '证书已过期',
        INSUFFICIENT_PERMISSIONS: '权限不足'
    },

    /**
     * 成功消息配置
     */
    SUCCESS_MESSAGES: {
        // 通用成功消息
        LOGIN_SUCCESS: '登录成功',
        LOGOUT_SUCCESS: '登出成功',
        PROJECT_CREATED: '项目创建成功',
        PROJECT_UPDATED: '项目更新成功',
        REQUEST_SUBMITTED: '申请提交成功',
        REQUEST_APPROVED: '申请已批准',
        REQUEST_REJECTED: '申请已拒绝',
        TRAINING_STARTED: '训练已开始',
        TRAINING_STOPPED: '训练已停止',
        
        // 密钥加密模块成功消息
        KEY_GENERATED: '密钥生成成功',
        KEY_EXPORTED: '密钥导出成功',
        KEY_REVOKED: '密钥吊销成功',
        ENCRYPTION_SUCCESS: '加密操作成功',
        DECRYPTION_SUCCESS: '解密操作成功',
        SIGNATURE_SUCCESS: '签名操作成功',
        VERIFICATION_SUCCESS: '签名验证成功',
        CERTIFICATE_CREATED: '证书创建成功',
        CERTIFICATE_VERIFIED: '证书验证成功'
    },

    /**
     * 时间格式配置
     */
    TIME_FORMATS: {
        DATETIME: 'YYYY-MM-DD HH:mm:ss',
        DATE: 'YYYY-MM-DD',
        TIME: 'HH:mm:ss',
        TIMESTAMP: 'YYYY-MM-DD HH:mm:ss.SSS'
    },

    /**
     * UI配置
     */
    UI: {
        COLORS: {
            PRIMARY: '#3b82f6',
            SECONDARY: '#6b7280',
            SUCCESS: '#10b981',
            WARNING: '#f59e0b',
            ERROR: '#ef4444',
            INFO: '#3b82f6'
        },
        PAGINATION: {
            PAGE_SIZE: 10,
            MAX_PAGE_SIZE: 50
        },
        ANIMATION: {
            DURATION: 300,
            EASING: 'ease-in-out'
        }
    }
};

// 冻结常量对象，防止修改
Object.freeze(UnifiedConstants);

// 导出到全局
if (typeof window !== 'undefined') {
    window.UnifiedConstants = UnifiedConstants;
    // 保持向后兼容
    window.FedConstants = UnifiedConstants;
    window.CryptoConstants = {
        MODULE: {
            NAME: UnifiedConstants.BUSINESS_TYPES.CRYPTO.name,
            VERSION: UnifiedConstants.APP.VERSION,
            DESCRIPTION: UnifiedConstants.BUSINESS_TYPES.CRYPTO.description,
            ICON: UnifiedConstants.BUSINESS_TYPES.CRYPTO.icon,
            COLOR: UnifiedConstants.BUSINESS_TYPES.CRYPTO.color.primary
        },
        API: {
            BASE_URL: UnifiedConstants.API.BASE_URL + '/crypto',
            ENDPOINTS: {
                KEYS: UnifiedConstants.API.ENDPOINTS.CRYPTO.KEYS,
                OPERATIONS: UnifiedConstants.API.ENDPOINTS.CRYPTO.OPERATIONS,
                CERTIFICATES: UnifiedConstants.API.ENDPOINTS.CRYPTO.CERTIFICATES
            }
        },
        KEY_TYPES: UnifiedConstants.KEY_TYPES,
        KEY_USAGES: UnifiedConstants.KEY_USAGES,
        KEY_STATUS: UnifiedConstants.KEY_STATUS,
        SIGNATURE_ALGORITHMS: UnifiedConstants.SIGNATURE_ALGORITHMS,
        HASH_ALGORITHMS: UnifiedConstants.HASH_ALGORITHMS,
        CERTIFICATE_TYPES: UnifiedConstants.CERTIFICATE_TYPES,
        SECURITY_LEVELS: UnifiedConstants.SECURITY_LEVELS,
        VALIDATION: {
            KEY_NAME: UnifiedConstants.VALIDATION.KEY_NAME,
            PASSPHRASE: UnifiedConstants.VALIDATION.PASSPHRASE,
            CERTIFICATE_DN: UnifiedConstants.VALIDATION.CERTIFICATE_DN
        },
        FILE_TYPES: {
            SUPPORTED_ENCRYPTION: UnifiedConstants.FILE_TYPES.SUPPORTED_ENCRYPTION,
            SUPPORTED_SIGNING: UnifiedConstants.FILE_TYPES.SUPPORTED_SIGNING,
            MAX_SIZE: UnifiedConstants.DEFAULTS.CRYPTO.MAX_FILE_SIZE,
            CHUNK_SIZE: UnifiedConstants.DEFAULTS.CRYPTO.CHUNK_SIZE
        },
        UI: UnifiedConstants.UI,
        ERROR_MESSAGES: {
            KEY_GENERATION_FAILED: UnifiedConstants.ERROR_MESSAGES.KEY_GENERATION_FAILED,
            INVALID_PASSPHRASE: UnifiedConstants.ERROR_MESSAGES.INVALID_PASSPHRASE,
            KEY_NOT_FOUND: UnifiedConstants.ERROR_MESSAGES.KEY_NOT_FOUND,
            ENCRYPTION_FAILED: UnifiedConstants.ERROR_MESSAGES.ENCRYPTION_FAILED,
            DECRYPTION_FAILED: UnifiedConstants.ERROR_MESSAGES.DECRYPTION_FAILED,
            SIGNATURE_FAILED: UnifiedConstants.ERROR_MESSAGES.SIGNATURE_FAILED,
            VERIFICATION_FAILED: UnifiedConstants.ERROR_MESSAGES.VERIFICATION_FAILED,
            CERTIFICATE_INVALID: UnifiedConstants.ERROR_MESSAGES.CERTIFICATE_INVALID,
            CERTIFICATE_EXPIRED: UnifiedConstants.ERROR_MESSAGES.CERTIFICATE_EXPIRED,
            INSUFFICIENT_PERMISSIONS: UnifiedConstants.ERROR_MESSAGES.INSUFFICIENT_PERMISSIONS
        },
        SUCCESS_MESSAGES: {
            KEY_GENERATED: UnifiedConstants.SUCCESS_MESSAGES.KEY_GENERATED,
            KEY_EXPORTED: UnifiedConstants.SUCCESS_MESSAGES.KEY_EXPORTED,
            KEY_REVOKED: UnifiedConstants.SUCCESS_MESSAGES.KEY_REVOKED,
            ENCRYPTION_SUCCESS: UnifiedConstants.SUCCESS_MESSAGES.ENCRYPTION_SUCCESS,
            DECRYPTION_SUCCESS: UnifiedConstants.SUCCESS_MESSAGES.DECRYPTION_SUCCESS,
            SIGNATURE_SUCCESS: UnifiedConstants.SUCCESS_MESSAGES.SIGNATURE_SUCCESS,
            VERIFICATION_SUCCESS: UnifiedConstants.SUCCESS_MESSAGES.VERIFICATION_SUCCESS,
            CERTIFICATE_CREATED: UnifiedConstants.SUCCESS_MESSAGES.CERTIFICATE_CREATED,
            CERTIFICATE_VERIFIED: UnifiedConstants.SUCCESS_MESSAGES.CERTIFICATE_VERIFIED
        }
    };
}

// 模块化导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UnifiedConstants;
}