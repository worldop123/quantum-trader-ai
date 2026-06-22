# 安装指南

本文档详细说明如何在本地安装和运行 QuantumTrader AI。

---

## 环境要求

### 必需软件

| 软件 | 最低版本 | 推荐版本 | 说明 |
|------|----------|----------|------|
| Node.js | 18.0.0 | 20.x LTS | 前端运行环境 |
| Python | 3.10 | 3.12+ | 后端运行环境 |
| Git | 2.0 | 最新版 | 版本控制 |
| npm | 8.0 | 10.x | Node包管理器 |

### 可选软件

- **VS Code** - 推荐的代码编辑器
- **Postman** - API测试工具
- **DB Browser for SQLite** - 数据库查看工具

---

## 快速安装

### 1. 克隆项目

```bash
git clone https://github.com/QuantumTrader-AI/quantum-trader-ai.git
cd quantum-trader-ai
```

### 2. 后端安装

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Linux/Mac
source venv/bin/activate
# Windows
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的配置
```

### 3. 前端安装

```bash
# 回到项目根目录
cd ..

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件
```

### 4. 启动服务

**方式一：分别启动**

```bash
# 启动后端（在 backend 目录下）
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 启动前端（新开一个终端，在项目根目录）
npm run dev
```

**方式二：使用启动脚本**

```bash
# 给脚本添加执行权限
chmod +x start.sh

# 启动前后端
./start.sh all

# 仅启动后端
./start.sh backend

# 仅启动前端
./start.sh frontend
```

### 5. 访问应用

- **前端地址**: http://localhost:5173
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc

---

## 详细配置说明

### 后端配置（backend/.env）

#### 数据库配置

```env
DATABASE_URL=sqlite:///./quantum_trader.db
```

默认使用SQLite数据库，文件位于backend目录下。如需使用PostgreSQL，请修改为：

```env
DATABASE_URL=postgresql://user:password@localhost:5432/quantum_trader
```

#### JWT配置

```env
SECRET_KEY=your-secret-key-change-in-production-at-least-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

- **SECRET_KEY**: JWT签名密钥，生产环境必须修改为随机字符串
- **ALGORITHM**: 加密算法，默认HS256
- **ACCESS_TOKEN_EXPIRE_MINUTES**: Token过期时间（分钟），默认1440分钟（24小时）

#### 加密密钥配置

```env
ENCRYPTION_KEY=your-encryption-key-must-be-32-chars!
```

用于加密存储API密钥的密钥。

**重要提示：**
- 必须是32个字符
- 生产环境必须修改
- 密钥丢失将无法恢复已加密的API密钥

生成安全的加密密钥：
```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())
```

#### 欧易（OKX）配置

```env
OKX_API_KEY=your_okx_api_key
OKX_API_SECRET=your_okx_api_secret
OKX_PASSPHRASE=your_okx_passphrase
OKX_DEMO=true
```

- **OKX_API_KEY**: 欧易API Key
- **OKX_API_SECRET**: 欧易API Secret
- **OKX_PASSPHRASE**: 欧易API密码
- **OKX_DEMO**: 是否使用模拟盘，默认true

**获取API密钥：**
1. 注册欧易账号：https://www.okx.com
2. 开通模拟交易（推荐先测试）
3. 进入API管理页面
4. 创建API密钥，勾选"交易"权限
5. 建议绑定IP白名单提高安全性

#### DeepSeek AI配置

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_URL=https://api.deepseek.com
```

- **DEEPSEEK_API_KEY**: DeepSeek API密钥
- **DEEPSEEK_API_URL**: API地址，默认官方地址

**获取API密钥：**
1. 注册DeepSeek开放平台：https://platform.deepseek.com
2. 创建API密钥
3. 用于行情分析、策略解释等AI功能

#### PushPlus配置

```env
PUSHPLUS_TOKEN=your_pushplus_token
PUSHPLUS_URL=http://www.pushplus.plus/send
```

- **PUSHPLUS_TOKEN**: PushPlus个人Token
- **PUSHPLUS_URL**: 推送地址

**获取Token：**
1. 登录PushPlus官网：http://www.pushplus.plus
2. 关注公众号获取Token
3. 用于接收订单通知、风险预警等消息

#### 服务配置

```env
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

- **HOST**: 服务监听地址，默认0.0.0.0（所有地址）
- **PORT**: 服务端口，默认8000
- **CORS_ORIGINS**: 允许的跨域来源

### 前端配置（.env）

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
```

- **VITE_API_BASE_URL**: API基础地址
- **VITE_WS_URL**: WebSocket地址

---

## 测试账号

系统启动时会自动创建两个测试账号：

| 角色 | 邮箱 | 密码 | 权限 |
|------|------|------|------|
| 普通用户 | test@quantumtrader.ai | Test123456 | 普通交易功能 |
| 管理员 | admin@quantumtrader.ai | Admin123456 | 全部功能 + 管理后台 |

**注意：** 首次启动时会自动创建数据库和测试账号。

---

## 常见问题

### 1. 后端启动失败

**问题：** 提示端口被占用

**解决：**
```bash
# 查看占用8000端口的进程
lsof -i :8000
# 或
netstat -ano | findstr 8000  # Windows

# 杀掉进程或更换端口
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 2. 前端启动失败

**问题：** 提示依赖安装失败

**解决：**
```bash
# 清除缓存重新安装
rm -rf node_modules
rm package-lock.json
npm install
```

### 3. 数据库错误

**问题：** 数据库文件损坏或表不存在

**解决：**
```bash
# 删除数据库文件，重启服务会自动重建
cd backend
rm quantum_trader.db
```

### 4. API密钥验证失败

**问题：** 添加API密钥后验证失败

**检查：**
1. API密钥是否正确
2. 是否选择了正确的环境（模拟盘/实盘）
3. IP白名单是否包含当前IP
4. API权限是否勾选了"交易"

### 5. WebSocket连接失败

**问题：** 前端无法连接WebSocket

**检查：**
1. 后端服务是否正常启动
2. WebSocket地址是否正确
3. Token是否有效
4. 防火墙是否阻止了连接

### 6. 下单失败

**问题：** 下单时提示错误

**可能原因：**
1. API密钥配置错误
2. 账户余额不足
3. 风控设置拦截了订单
4. 交易对不存在或格式错误

**排查步骤：**
1. 检查API密钥是否验证通过
2. 查看账户余额
3. 检查风控设置
4. 查看后端日志获取详细错误信息

---

## 开发环境推荐配置

### VS Code 推荐插件

- **Python** - Python语言支持
- **Pylance** - Python语言服务器
- **Volar** - Vue 3支持
- **TypeScript Vue Plugin** - TypeScript Vue插件
- **Tailwind CSS IntelliSense** - TailwindCSS智能提示
- **ESLint** - 代码检查
- **Prettier** - 代码格式化
- **GitLens** - Git增强
- **SQLite** - SQLite数据库查看

### 浏览器推荐

- **Chrome / Edge** - 推荐使用
- **Vue DevTools** - Vue调试工具

---

## 生产环境部署

⚠️ **注意：** 本项目目前处于开发阶段，不建议直接用于生产环境。

如需部署到生产环境，请参考以下建议：

1. **使用PostgreSQL** 替代SQLite
2. **配置Nginx** 反向代理
3. **启用HTTPS** 加密传输
4. **配置防火墙** 限制访问
5. **定期备份数据库**
6. **监控系统运行状态**

---

## 下一步

安装完成后，你可以：

1. 📖 阅读 [README.md](README.md) 了解项目功能
2. 🛠️ 查看 [DEVELOPMENT.md](DEVELOPMENT.md) 了解开发指南
3. 🗺️ 查看 [ROADMAP.md](ROADMAP.md) 了解开发路线图
4. 🤝 查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何贡献

---

如有问题，请提交 [Issue](https://github.com/QuantumTrader-AI/quantum-trader-ai/issues)。
