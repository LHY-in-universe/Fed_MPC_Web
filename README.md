# Fed_MPC_Web - 联邦学习平台

基于Web的联邦学习平台，支持AI大模型和金融区块链两种业务类型，提供普通训练和MPC隐私保护训练两种模式。

## 功能特性

- ✅ 双业务类型支持（AI大模型 / 金融区块链）
- ✅ 多用户角色（客户端 / 总服务器管理员）
- ✅ 训练模式切换（普通训练 / MPC安全多方计算）
- ✅ 项目管理（本地项目 / 联合训练申请）
- ✅ 实时训练监控和可视化
- ✅ 客户端管理和权限控制
- ✅ 模型文件管理
- ✅ 完整的认证和路由系统

## 技术栈

### 前端
- HTML5, CSS3, JavaScript (原生)
- TailwindCSS - UI框架
- Chart.js - 图表可视化
- 响应式设计

### 后端 (预留接口)
- Python Flask - Web框架
- JWT - 用户认证
- RESTful API 设计
- MySQL - 数据库 (待集成)

## 项目结构

```
Fed_MPC_Web/
├── frontend/                   # 前端文件
│   ├── index.html             # 主入口页面
│   ├── login/                 # 登录相关页面
│   │   ├── business-type.html # 业务类型选择
│   │   ├── client-login.html  # 客户端登录
│   │   └── server-login.html  # 服务器登录
│   ├── client/                # 客户端页面
│   │   └── dashboard.html     # 客户端仪表盘
│   ├── server/                # 服务器管理页面
│   │   └── admin-dashboard.html # 管理员仪表盘
│   └── shared/                # 共享组件
│       ├── auth.js           # 认证系统
│       └── router.js         # 路由系统
├── backend/                   # 后端API (预留)
│   ├── app.py                # Flask主应用
│   ├── config.py             # 配置文件
│   ├── routes/               # API路由
│   │   ├── auth.py          # 认证接口
│   │   ├── client.py        # 客户端接口
│   │   ├── server.py        # 服务器接口
│   │   └── training.py      # 训练接口
│   └── requirements.txt      # Python依赖
└── README.md                  # 项目说明
```

## 快速开始

### 前端运行

1. 使用任意HTTP服务器服务前端文件，例如：

```bash
# 使用Python内置服务器
cd frontend
python -m http.server 8080

# 或使用Node.js服务器
npx serve -p 8080

# 或使用Live Server (VS Code插件)
```

2. 访问 `http://localhost:8080` 开始使用

### 后端运行 (可选)

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
python app.py
```

后端API将在 `http://localhost:5000` 启动

## 使用指南

### 1. 选择业务类型
- 访问首页，选择 "AI大模型业务" 或 "金融区块链业务"

### 2. 选择登录类型
- **客户端登录**：适合参与方，可创建项目、申请联合训练
- **总服务器登录**：适合管理员，可管理所有客户端和审批申请

### 3. 演示账号
- **客户端**：上海一厂、武汉二厂、西安三厂、广州四厂 (金融：工商银行、建设银行、招商银行)
- **服务器**：管理员演示登录

### 4. 主要功能

#### 客户端功能
- 创建本地训练项目
- 申请联合训练（需要总服务器审批）
- 切换训练模式（普通/MPC）
- 实时监控训练进度
- 查看参与节点状态

#### 总服务器功能
- 管理所有客户端连接
- 审批联合训练申请
- 监控全局训练项目
- 管理模型文件下载
- 查看系统统计信息

### 5. 训练模式说明

#### 普通训练模式
- 训练过程透明
- 总服务器可查看详细训练数据
- 训练效率高
- 适用于数据隐私要求不高的场景

#### MPC训练模式
- 使用安全多方计算技术
- 总服务器无法获取具体训练数据
- 保护参与方数据隐私
- 部分训练信息被加密显示

## 后端API接口设计

### 正常训练模式
- **数据来源**: 总服务器Python训练文件直接读取
- **数据内容**: 准确率、训练轮次、全局模型损失、参与节点状态、心跳信息
- **数据存储**: 实时写入MySQL数据库，支持进度恢复

### MPC训练模式  
- **客户端数据**: 准确率、训练轮次、全局模型损失（本地Python文件读取）
- **服务器数据**: 参与客户端节点、状态、心跳（中间服务器读取）
- **隐私保护**: 训练过程核心信息对总服务器不可见

### API端点

#### 认证接口 `/api/auth`
- `POST /login` - 用户登录
- `POST /logout` - 用户登出  
- `GET /verify` - 验证token
- `POST /refresh` - 刷新token

#### 客户端接口 `/api/client`
- `GET /projects` - 获取项目列表
- `POST /projects` - 创建新项目
- `GET /projects/:id` - 获取项目详情
- `POST /training-requests` - 提交联合训练申请

#### 服务器接口 `/api/server`
- `GET /dashboard` - 获取仪表盘数据
- `GET /clients` - 获取客户端列表
- `POST /clients` - 添加客户端
- `POST /training-requests/:id/approve` - 批准训练申请
- `GET /models` - 获取模型列表

#### 训练接口 `/api/training`
- `POST /sessions` - 创建训练会话
- `POST /sessions/:id/start` - 开始训练
- `POST /sessions/:id/round` - 提交轮次数据
- `GET /sessions/:id/logs` - 获取训练日志

## 开发说明

### 前端开发
- 所有页面使用原生JavaScript开发
- 使用localStorage进行数据持久化
- 支持响应式设计
- 模拟真实的联邦学习训练过程

### 后端接口 (预留)
- 提供完整的RESTful API设计
- 支持JWT身份认证
- 预留MySQL数据库集成
- 支持文件上传下载
- 包含完整的错误处理

### 数据存储
- 前端使用localStorage存储用户数据和项目信息
- 后端提供完整的API接口规范
- 数据库Schema设计已预留

## 扩展计划

- [ ] 集成MySQL数据库
- [ ] 实现真实的联邦学习算法
- [ ] 添加更多的模型支持
- [ ] 实现文件上传下载功能
- [ ] 添加WebSocket实时通信
- [ ] 增加更多的图表和监控功能
- [ ] 实现容器化部署

## 技术支持

如有问题或建议，请查看项目文档或提交Issue。