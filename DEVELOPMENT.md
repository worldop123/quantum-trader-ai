# QuantumTrader AI 开发指南

本文档为 QuantumTrader AI 项目的开发指南，旨在帮助开发者快速了解项目架构、代码规范和开发流程。

## 目录

- [项目架构](#项目架构)
- [技术栈](#技术栈)
- [代码规范](#代码规范)
- [开发环境搭建](#开发环境搭建)
- [调试技巧](#调试技巧)
- [测试指南](#测试指南)
- [部署说明](#部署说明)
- [常见问题](#常见问题)

---

## 项目架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端 (Vue 3)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  页面层   │  │  组件层   │  │  状态管理  │  │  API层   │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                    REST API + WebSocket
                               │
┌──────────────────────────────┴──────────────────────────────┐
│                       后端 (FastAPI)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ API路由层 │  │ 服务层    │  │ 模型层    │  │ 工具层    │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                    SQLite + SQLAlchemy
                               │
┌──────────────────────────────┴──────────────────────────────┐
│                    外部服务集成                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ OKX交易所 │  │ DeepSeek  │  │ PushPlus │  │ llama.cpp│    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 后端架构

后端采用分层架构设计：

1. **API 层** (`app/api/`)
   - 处理 HTTP 请求和响应
   - 参数验证
   - 调用服务层
   - 返回统一格式的响应

2. **服务层** (`app/services/`)
   - 核心业务逻辑
   - 数据处理和计算
   - 调用外部 API
   - 风控检查

3. **模型层** (`app/models/`)
   - 数据库表定义
   - SQLAlchemy ORM 模型
   - 数据关系定义

4. **Schema 层** (`app/schemas/`)
   - Pydantic 数据模型
   - 请求/响应数据验证
   - 数据序列化

5. **工具层** (`app/utils/`)
   - 加密工具
   - 通用工具函数
   - 辅助函数

6. **WebSocket 层** (`app/websocket/`)
   - WebSocket 连接管理
   - 消息推送
   - 订阅管理

### 前端架构

前端采用 Vue 3 + TypeScript 架构：

1. **页面层** (`src/views/`)
   - 页面级组件
   - 路由对应页面
   - 业务逻辑组装

2. **组件层** (`src/components/`)
   - 可复用组件
   - 图表组件
   - 通用组件

3. **状态管理** (`src/stores/`)
   - Pinia 状态管理
   - 全局状态共享
   - 用户信息、交易数据等

4. **API 层** (`src/api/`)
   - HTTP 请求封装
   - 接口定义
   - 请求拦截和响应处理

5. **工具层** (`src/utils/`)
   - WebSocket 工具
   - 防抖节流
   - 通用工具函数

6. **路由层** (`src/router/`)
   - 路由配置
   - 路由守卫
   - 页面导航

---

## 技术栈

### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.12+ | 编程语言 |
| FastAPI | 0.100+ | Web 框架 |
| SQLAlchemy | 2.0+ | ORM 框架 |
| SQLite | 3.0+ | 数据库 |
| Pydantic | 2.0+ | 数据验证 |
| python-jose | - | JWT 认证 |
| passlib | - | 密码哈希 |
| cryptography | - | 加密解密 |
| websockets | - | WebSocket |
| httpx | - | HTTP 客户端 |
| uvicorn | - | ASGI 服务器 |

### 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.4+ | 前端框架 |
| TypeScript | 5.0+ | 类型系统 |
| Vite | 5.0+ | 构建工具 |
| Pinia | 2.0+ | 状态管理 |
| Vue Router | 4.0+ | 路由管理 |
| ECharts | 5.4+ | 图表库 |
| Element Plus | 2.0+ | UI 组件库 |
| TailwindCSS | 3.4+ | CSS 框架 |
| Axios | 1.6+ | HTTP 客户端 |

---

## 代码规范

### Python 代码规范

#### 命名规范

- **变量名**: snake_case（小写+下划线）
  ```python
  user_name = "test"
  max_position_size = 1000
  ```

- **函数名**: snake_case
  ```python
  def get_user_balance(user_id: int) -> float:
      pass
  ```

- **类名**: PascalCase（大驼峰）
  ```python
  class TradingService:
      pass
  ```

- **常量**: UPPER_SNAKE_CASE
  ```python
  MAX_DAILY_LOSS = 500
  DEFAULT_TIMEFRAME = "1h"
  ```

- **模块名**: snake_case
  ```
  auth_service.py
  strategy_engine.py
  ```

#### 类型注解

所有函数必须添加类型注解：

```python
def calculate_position_pnl(
    position: Position,
    current_price: float
) -> dict[str, float]:
    """计算持仓盈亏"""
    pnl = (current_price - position.entry_price) * position.quantity
    pnl_ratio = pnl / (position.entry_price * position.quantity) * 100
    return {
        "pnl": pnl,
        "pnl_ratio": pnl_ratio
    }
```

#### 文档字符串

所有公共函数和类必须有 docstring：

```python
class RiskService:
    """风控服务类

    提供三层风控检查：系统级、策略级、单交易级
    支持三级熔断机制
    """

    def check_single_trade_risk(
        self,
        order: OrderCreate,
        user_id: int
    ) -> tuple[bool, str]:
        """检查单交易风控

        Args:
            order: 订单信息
            user_id: 用户ID

        Returns:
            tuple[bool, str]: (是否通过, 失败原因)
        """
        pass
```

#### 导入规范

导入按以下顺序分组：

1. 标准库导入
2. 第三方库导入
3. 本地应用导入

每组之间空一行：

```python
import os
from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.trading import OrderCreate
```

### Vue/TypeScript 代码规范

#### 组件命名

- **组件文件名**: PascalCase
  ```
  KLineChart.vue
  NumberTicker.vue
  ```

- **组件名**: PascalCase
  ```typescript
  export default defineComponent({
    name: 'KLineChart'
  })
  ```

#### Props 定义

Props 必须定义完整类型和默认值：

```typescript
interface Props {
  value: number
  change?: number
  precision?: number
  prefix?: string
  suffix?: string
}

const props = withDefaults(defineProps<Props>(), {
  change: 0,
  precision: 2,
  prefix: '',
  suffix: ''
})
```

#### 组合式 API

优先使用 `<script setup>` 语法：

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(false)
const data = ref<DataItem[]>([])

const total = computed(() => data.value.length)

async function fetchData() {
  loading.value = true
  try {
    // 数据获取逻辑
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>
```

#### 样式规范

- 使用 TailwindCSS 进行样式开发
- 复杂样式使用 scoped style
- 避免使用 !important
- 颜色使用 CSS 变量

```vue
<template>
  <div class="card p-4 rounded-lg bg-slate-800 border border-cyan-500/30">
    <h3 class="text-lg font-bold text-cyan-400">{{ title }}</h3>
  </div>
</template>

<style scoped>
.card {
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
}
</style>
```

### Git 提交规范

#### 提交信息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type 类型

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具相关

#### 示例

```
feat(strategy): 添加布林带策略实盘运行

- 实现布林带策略信号计算
- 添加参数配置界面
- 集成风控检查
- 支持止盈止损自动执行

Closes #123
```

---

## 开发环境搭建

### 后端环境搭建

#### 1. 前置要求

- Python 3.12 或更高版本
- pip 包管理器
- 虚拟环境（推荐）

#### 2. 克隆项目

```bash
git clone https://github.com/worldop123/quantum-trader-ai.git
cd quantum-trader-ai
```

#### 3. 创建虚拟环境

```bash
cd backend
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 4. 安装依赖

```bash
pip install -r requirements.txt
```

#### 5. 配置环境变量

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入必要的配置：

```env
# 数据库配置
DATABASE_URL=sqlite:///./quantum_trader.db

# JWT配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 加密密钥（用于API密钥加密）
ENCRYPTION_KEY=your-encryption-key-here

# DeepSeek API配置
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# PushPlus配置
PUSHPLUS_TOKEN=your-pushplus-token
```

#### 6. 启动后端服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后，访问以下地址：

- API 文档: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 前端环境搭建

#### 1. 前置要求

- Node.js 18 或更高版本
- npm 或 yarn 包管理器

#### 2. 安装依赖

```bash
# 在项目根目录
npm install
```

#### 3. 配置环境变量

创建 `.env.development` 文件：

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_BASE_URL=ws://localhost:8000/ws
```

#### 4. 启动前端服务

```bash
npm run dev
```

服务启动后，访问 http://localhost:5173

### 测试账号

系统启动时自动创建两个测试账号：

| 角色 | 邮箱 | 密码 |
|------|------|------|
| 普通用户 | test@quantumtrader.ai | Test123456 |
| 管理员 | admin@quantumtrader.ai | Admin123456 |

---

## 调试技巧

### 后端调试

#### 使用 Swagger UI 测试 API

FastAPI 自动生成的 Swagger UI 是测试 API 的最佳工具：

1. 访问 http://localhost:8000/docs
2. 点击 `Authorize` 按钮，输入 JWT Token
3. 选择要测试的接口
4. 点击 `Try it out`
5. 填写参数，点击 `Execute`
6. 查看响应结果

#### 日志调试

在代码中添加日志输出：

```python
import logging

logger = logging.getLogger(__name__)

def some_function():
    logger.debug("调试信息")
    logger.info("普通信息")
    logger.warning("警告信息")
    logger.error("错误信息")
```

查看日志输出：

```bash
# 启动时设置日志级别
uvicorn app.main:app --log-level debug
```

#### VS Code 调试

在 `.vscode/launch.json` 中添加配置：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
        "--reload"
      ],
      "cwd": "${workspaceFolder}/backend",
      "jinja": true
    }
  ]
}
```

### 前端调试

#### Vue DevTools

安装 Vue DevTools 浏览器扩展：

- Chrome: Vue.js devtools
- Firefox: Vue.js devtools

功能：
- 查看组件树
- 检查组件 Props 和 State
- 查看 Pinia 状态
- 时间旅行调试
- 性能分析

#### 浏览器控制台

使用 `console` API 进行调试：

```typescript
console.log('普通日志')
console.warn('警告')
console.error('错误')
console.table('表格数据')
console.dir('对象详情')
```

#### Network 面板

检查 API 请求：

1. 打开浏览器开发者工具
2. 切换到 Network 面板
3. 查看请求和响应
4. 检查请求头、响应头、请求体、响应体
5. 查看请求耗时

#### WebSocket 调试

检查 WebSocket 连接：

1. 打开浏览器开发者工具
2. 切换到 Network 面板
3. 筛选 WS (WebSocket)
4. 点击 WebSocket 连接
5. 查看 Messages 标签
6. 查看发送和接收的消息

### 数据库调试

#### 查看数据库内容

使用 SQLite 工具查看数据库：

- DB Browser for SQLite（桌面工具）
- sqlite-web（Web 界面）
- VS Code SQLite 插件

#### 数据库位置

默认数据库文件位于：
```
backend/quantum_trader.db
```

---

## 测试指南

### 后端测试

#### 运行测试

```bash
cd backend
pytest
```

#### 测试覆盖率

```bash
pytest --cov=app --cov-report=html
```

#### 编写测试

测试文件放在 `tests/` 目录，文件名以 `test_` 开头：

```python
# tests/test_auth.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login():
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@quantumtrader.ai",
            "password": "Test123456"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### 前端测试

#### 单元测试

使用 Vitest 进行单元测试：

```bash
npm run test:unit
```

#### E2E 测试

使用 Playwright 进行端到端测试：

```bash
# 安装 Playwright
npx playwright install

# 运行测试
npm run test:e2e

# 查看测试报告
npx playwright show-report
```

### 手动测试清单

#### 用户认证

- [ ] 用户注册
- [ ] 用户登录
- [ ] Token 刷新
- [ ] 获取用户信息
- [ ] 修改密码

#### 交易功能

- [ ] 查询余额
- [ ] 查询持仓
- [ ] 限价单下单
- [ ] 市价单下单
- [ ] 撤单
- [ ] 查询订单历史
- [ ] 查询成交记录

#### 行情功能

- [ ] 获取实时行情
- [ ] 获取 K 线数据
- [ ] 获取深度数据
- [ ] 交易对搜索

#### 策略功能

- [ ] 创建策略
- [ ] 启动策略
- [ ] 暂停策略
- [ ] 停止策略
- [ ] 查看策略日志
- [ ] 策略回测

#### 风控功能

- [ ] 查看风控设置
- [ ] 修改风控参数
- [ ] 查看风控状态
- [ ] 查看风控日志

---

## 部署说明

### 开发环境部署

#### 后端

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 前端

```bash
npm run dev
```

### 生产环境部署

#### 后端部署

使用 Gunicorn + Uvicorn：

```bash
pip install gunicorn

gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile access.log \
  --error-logfile error.log
```

#### 前端部署

构建生产版本：

```bash
npm run build
```

构建产物在 `dist/` 目录，可以部署到：

- Nginx
- CDN
- Vercel
- Netlify

#### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket代理
    location /ws/ {
        proxy_pass http://127.0.0.1:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### Docker 部署

#### 后端 Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 前端 Dockerfile

```dockerfile
FROM node:18-alpine as builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./data/quantum_trader.db
    volumes:
      - ./data:/app/data

  frontend:
    build: .
    ports:
      - "80:80"
    depends_on:
      - backend
```

---

## 常见问题

### 后端相关

#### Q: 后端启动失败，提示端口被占用？

A: 检查 8000 端口是否被其他程序占用：

```bash
# Linux/Mac
lsof -i :8000

# Windows
netstat -ano | findstr :8000
```

可以修改启动端口：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

#### Q: 数据库连接失败？

A: 检查以下几点：
1. 数据库文件是否存在
2. 数据库路径是否正确
3. 文件权限是否正确
4. DATABASE_URL 配置是否正确

#### Q: API 请求返回 401 Unauthorized？

A: 检查以下几点：
1. 是否在请求头中携带了 Authorization
2. Token 格式是否正确（Bearer <token>）
3. Token 是否过期
4. Token 是否有效

#### Q: 欧易 API 调用失败？

A: 检查以下几点：
1. API Key 是否正确
2. Secret Key 是否正确
3. Passphrase 是否正确
4. 是否是模拟盘环境
5. 网络是否能访问欧易 API
6. API 权限是否正确

### 前端相关

#### Q: 前端连不上后端？

A: 检查以下几点：
1. 后端服务是否启动
2. VITE_API_BASE_URL 配置是否正确
3. CORS 配置是否正确
4. 端口是否正确

#### Q: WebSocket 连接失败？

A: 检查以下几点：
1. 后端 WebSocket 端点是否正确
2. VITE_WS_BASE_URL 配置是否正确
3. Token 是否有效
4. 网络连接是否正常

#### Q: 图表不显示？

A: 检查以下几点：
1. ECharts 是否正确安装
2. 容器是否有高度
3. 数据格式是否正确
4. 是否有 JS 报错

### 策略相关

#### Q: 策略启动后没有反应？

A: 检查以下几点：
1. 策略参数是否正确
2. API 密钥是否配置
3. 风控设置是否阻止了交易
4. 策略日志是否有报错
5. 行情数据是否正常获取

#### Q: 策略下单失败？

A: 检查以下几点：
1. 余额是否充足
2. 风控检查是否通过
3. 订单参数是否正确
4. API 密钥是否有权限
5. 是否是模拟盘

---

## 性能优化

### 后端优化

1. **数据库优化**
   - 添加索引
   - 使用连接池
   - 优化查询语句

2. **缓存优化**
   - 行情数据缓存
   - 用户信息缓存
   - 使用 Redis（可选）

3. **异步处理**
   - 策略运行异步
   - 通知推送异步
   - 耗时任务后台处理

### 前端优化

1. **代码分割**
   - 路由懒加载
   - 组件按需加载
   - 第三方库拆分

2. **性能优化**
   - 虚拟列表
   - 防抖节流
   - 图表数据优化

3. **构建优化**
   - Tree Shaking
   - 压缩代码
   - CDN 加速

---

## 安全注意事项

### API 密钥安全

1. **加密存储**
   - 所有 API 密钥使用 AES-256 加密存储
   - 加密密钥通过环境变量配置

2. **脱敏显示**
   - 前端只显示前 4 位和后 4 位
   - 中间用 * 代替
   - 日志中也要脱敏

3. **禁止明文**
   - 不要在代码中硬编码密钥
   - 不要在日志中打印完整密钥
   - 不要在错误信息中暴露密钥

### 用户数据安全

1. **密码哈希**
   - 使用 bcrypt 哈希密码
   - 不存储明文密码

2. **JWT 安全**
   - 使用强密钥
   - 设置合理的过期时间
   - 支持 Token 刷新

3. **输入验证**
   - 所有用户输入都要验证
   - 防止 SQL 注入
   - 防止 XSS 攻击

### 交易安全

1. **风控检查**
   - 所有下单必须经过风控检查
   - 不可绕过风控
   - 三级熔断机制

2. **模拟盘优先**
   - 开发测试只用模拟盘
   - 真实盘需额外确认
   - 明确标注环境

3. **操作确认**
   - 重要操作需要二次确认
   - 撤单、平仓等操作
   - 风控参数修改

---

## 贡献指南

详细的贡献指南请参考 [CONTRIBUTING.md](./CONTRIBUTING.md)。

---

## 相关文档

- [README.md](./README.md) - 项目介绍
- [INSTALL.md](./INSTALL.md) - 安装指南
- [ROADMAP.md](./ROADMAP.md) - 开发路线图
- [DEVELOPMENT_PROMPT.md](./DEVELOPMENT_PROMPT.md) - AI 开发提示词
- [CONTRIBUTING.md](./CONTRIBUTING.md) - 贡献指南

---

**最后更新：** 2026-06-22
