/**
 * 密钥加密签名模块 - 常量定义
 * 定义加密模块专用的常量和配置信息
 */

const CryptoConstants = {
    
    /**
     * 模块基本信息
     */
    MODULE: {
        NAME: '密钥加密签名模块',
        VERSION: '1.0.0',
        DESCRIPTION: '提供密钥管理、数据加密和数字签名功能',
        ICON: 'shield-check',
        COLOR: '#8b5cf6'
    },

    /**
     * API端点配置
     */
    API: {
        BASE_URL: 'http://localhost:5000/api/crypto',
        ENDPOINTS: {
            // 密钥管理
            KEYS: {
                LIST: '/keys',
                CREATE: '/keys/generate',
                DETAIL: '/keys/{keyId}',
                EXPORT: '/keys/{keyId}/export',
                REVOKE: '/keys/{keyId}/revoke'
            },
            
            // 加密操作
            OPERATIONS: {
                ENCRYPT: '/operations/encrypt',
                DECRYPT: '/operations/decrypt',
                SIGN: '/operations/sign',
                VERIFY: '/operations/verify'
            },
            
            // 证书管理
            CERTIFICATES: {
                LIST: '/certificates',
                CREATE: '/certificates/generate',
                DETAIL: '/certificates/{certId}',
                VERIFY: '/certificates/{certId}/verify',
                REVOKE: '/certificates/{certId}/revoke'
            }
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
     * 操作类型配置
     */
    OPERATION_TYPES: {
        DOCUMENT_SIGNING: {
            key: 'document_signing',
            name: '文档签名',
            description: '对文档进行数字签名',
            icon: 'document-text'
        },
        DATA_ENCRYPTION: {
            key: 'data_encryption',
            name: '数据加密',
            description: '对敏感数据进行加密',
            icon: 'lock-closed'
        },
        MESSAGE_SIGNING: {
            key: 'message_signing',
            name: '消息签名',
            description: '对消息进行数字签名',
            icon: 'chat-alt'
        },
        FILE_ENCRYPTION: {
            key: 'file_encryption',
            name: '文件加密',
            description: '对文件进行加密保护',
            icon: 'folder-open'
        }
    },

    /**
     * 验证规则
     */
    VALIDATION: {
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
     * 文件类型配置
     */
    FILE_TYPES: {
        SUPPORTED_ENCRYPTION: ['.txt', '.doc', '.docx', '.pdf', '.json', '.xml'],
        SUPPORTED_SIGNING: ['.txt', '.doc', '.docx', '.pdf', '.json', '.xml', '.zip'],
        MAX_SIZE: 10 * 1024 * 1024, // 10MB
        CHUNK_SIZE: 1024 * 1024 // 1MB
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
     * UI配置
     */
    UI: {
        COLORS: {
            PRIMARY: '#8b5cf6',
            SECONDARY: '#a78bfa',
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
    },

    /**
     * 错误消息
     */
    ERROR_MESSAGES: {
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
     * 成功消息
     */
    SUCCESS_MESSAGES: {
        KEY_GENERATED: '密钥生成成功',
        KEY_EXPORTED: '密钥导出成功',
        KEY_REVOKED: '密钥吊销成功',
        ENCRYPTION_SUCCESS: '加密操作成功',
        DECRYPTION_SUCCESS: '解密操作成功',
        SIGNATURE_SUCCESS: '签名操作成功',
        VERIFICATION_SUCCESS: '签名验证成功',
        CERTIFICATE_CREATED: '证书创建成功',
        CERTIFICATE_VERIFIED: '证书验证成功'
    }
};

// 冻结常量对象，防止修改
Object.freeze(CryptoConstants);

// 导出到全局
if (typeof window !== 'undefined') {
    window.CryptoConstants = CryptoConstants;
}

// 模块化导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CryptoConstants;
}