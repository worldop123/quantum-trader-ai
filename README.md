# QuantumTrader AI量化交易系统

专业的AI量化交易平台，支持欧易（OKX）交易所，集成DeepSeek AI分析，提供策略回测、自动化交易等功能。

## 技术栈

### 后端
- **框架**: FastAPI
- **数据库**: SQLite + SQLAlchemy
- **认证**: JWT Token
- **加密**: AES (Fernet)
- **交易所**: OKX API (模拟盘优先)
- **AI**: DeepSeek API
- **通知**: PushPlus

### 前端
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **状态管理**: Pinia
- **UI组件**: Element Plus
- **图表**: ECharts
- **路由**: Vue Router

## 功能特性

### ✅ 已完成
1. **用户认证系统**
   - 用户注册/登录
   - JWT Token认证
   - 用户设置持久化（主题、语言、涨跌颜色等）

2. **API密钥管理**
   - AES加密存储
   - 脱敏显示（前4后4）
   - 支持添加/修改/删除
   - 密钥验证功能

3. **欧易模拟盘对接**
   - 账户余额查询
   - 持仓查询
   - 下单（限价/市价）
   - 撤单
   - 订单历史
   - 成交记录

4. **行情数据**
   - 实时行情
   - K线数据（多周期）
   - 深度数据
   - 交易对搜索

5. **ECharts图表**
   - K线图
   - 深度图
   - 资产走势图
   - 回测收益图

6. **DeepSeek AI功能**
   - 行情技术分析
   - 策略原理解释
   - 交易信号生成（参考）

7. **PushPlus通知推送**
   - 订单状态通知
   - 风险预警
   - 策略状态通知

8. **策略回测框架**
   - 均线交叉策略
   - 网格交易策略
   - 马丁格尔策略（高风险，仅供学习）
   - 回测指标（收益率、最大回撤、胜率、夏普比率等）

9. **真分页与搜索**
   - 订单列表分页
   - 成交记录分页
   - 策略列表搜索筛选
   - 交易对搜索

### 🚧 进行中
- 期权交易基础版
- 策略实盘运行
- WebSocket实时推送

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- npm 或 yarn

### 后端启动

1. 进入后端目录
```bash
cd backend
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量（.env文件已预置测试密钥）
```bash
# 欧易模拟盘API密钥（已配置）
OKX_API_KEY=your_api_key
OKX_API_SECRET=your_api_secret
OKX_PASSPHRASE=your_passphrase
OKX_DEMO=true

# DeepSeek API密钥（已配置）
DEEPSEEK_API_KEY=your_deepseek_key

# PushPlus通知Token（已配置）
PUSHPLUS_TOKEN=your_pushplus_token
```

4. 启动服务
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

5. 访问API文档
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### 前端启动

1. 进入项目目录
```bash
cd quantum-trader
```

2. 安装依赖
```bash
npm install
```

3. 配置环境变量（.env文件已预置）
```bash
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
```

4. 启动开发服务器
```bash
npm run dev
```

5. 访问应用
   - 前端地址: http://localhost:5173

## 默认账号

系统启动时会自动创建两个测试账号：

| 角色 | 邮箱 | 密码 |
|------|------|------|
| 普通用户 | test@quantumtrader.ai | Test123456 |
| 管理员 | admin@quantumtrader.ai | Admin123456 |

## 安全说明

### API密钥安全
1. **加密存储**: 所有API密钥使用AES-256加密存储在数据库中
2. **脱敏显示**: 前端和日志中只显示前4位和后4位，中间用*代替
3. **用户自主管理**: 用户可以自行添加、修改、删除API密钥
4. **模拟盘优先**: 开发测试阶段默认使用模拟盘，真实盘需手动切换

### 开发测试注意事项
1. ⚠️ **绝对不要用真实盘测试代码！**
2. 所有开发测试请使用欧易模拟盘（Demo Trading）
3. 真实盘API密钥仅做配置预留，测试阶段不要调用

## API密钥配置

### 欧易（OKX）
1. 登录欧易官网，进入API管理页面
2. 创建API密钥，勾选"交易"权限
3. 建议使用模拟盘API进行测试
4. 绑定IP白名单提高安全性

### DeepSeek
1. 登录DeepSeek开放平台
2. 创建API密钥
3. 用于行情分析、策略解释等AI功能

### PushPlus
1. 登录PushPlus官网
2. 获取个人Token
3. 用于接收订单通知、风险预警等消息

## 项目结构

```
quantum-trader/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API路由
│   │   │   ├── auth.py        # 认证相关
│   │   │   ├── user.py        # 用户设置、API密钥管理
│   │   │   ├── market.py      # 行情数据
│   │   │   ├── trading.py     # 交易功能
│   │   │   └── strategy.py    # 策略管理、回测、AI
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # Pydantic模型
│   │   ├── services/          # 业务服务
│   │   │   ├── auth_service.py
│   │   │   ├── okx_service.py
│   │   │   ├── ai_service.py
│   │   │   ├── notification_service.py
│   │   │   └── backtest_service.py
│   │   ├── utils/             # 工具函数
│   │   │   └── encryption.py  # 加密工具
│   │   ├── websocket/         # WebSocket
│   │   ├── config.py          # 配置
│   │   ├── database.py        # 数据库
│   │   └── main.py            # 主应用
│   ├── .env                   # 环境变量
│   └── requirements.txt       # Python依赖
│
├── src/                       # 前端源码
│   ├── api/                   # API接口
│   ├── components/            # 组件
│   ├── views/                 # 页面
│   ├── stores/                # 状态管理
│   ├── router/                # 路由
│   └── ...
│
└── README.md                  # 项目说明
```

## 开发进度

### 第一阶段 ✅
- [x] 后端基础框架搭建
- [x] 用户认证系统
- [x] API密钥加密存储
- [x] 欧易模拟盘对接
- [x] ECharts图表组件
- [x] DeepSeek AI功能接入
- [x] PushPlus通知推送
- [x] 真分页、搜索筛选
- [x] 策略回测框架

### 第二阶段 🚧
- [ ] 期权交易基础版
- [ ] WebSocket实时推送
- [ ] 策略实盘运行
- [ ] 更多策略类型

### 第三阶段 📋
- [ ] 风控系统
- [ ] 资金管理
- [ ] 多账户管理
- [ ] 移动端适配

## 风险提示

⚠️ **重要提示**
1. 加密货币交易风险极高，可能导致全部本金损失
2. 本系统仅供学习研究使用，不构成任何投资建议
3. 请谨慎评估风险，使用模拟盘充分测试后再考虑实盘
4. 马丁格尔等策略理论上存在爆仓风险，请务必谨慎使用
5. AI分析结果仅供参考，不构成交易建议

## License

MIT License
