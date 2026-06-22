<div align="center">

# QuantumTrader AI

**全自动AI量化交易系统，支持多交易所、多策略、AI驱动**

[![GitHub stars](https://img.shields.io/github/stars/worldop123/quantum-trader-ai?style=social)](https://github.com/worldop123/quantum-trader-ai)
[![GitHub forks](https://img.shields.io/github/forks/worldop123/quantum-trader-ai?style=social)](https://github.com/worldop123/quantum-trader-ai)
[![License](https://img.shields.io/github/license/worldop123/quantum-trader-ai)](https://github.com/worldop123/quantum-trader-ai/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/vue-3.x-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal.svg)](https://fastapi.tiangolo.com/)

[文档](#文档) · [快速开始](#快速开始) · [功能特性](#功能特性) · [技术栈](#技术栈) · [贡献指南](#贡献指南)

</div>

---

## ⚠️ 免责声明

**重要提示：**

> 本项目仅供学习研究使用，不构成任何投资建议。
> 
> - 加密货币交易存在高风险，可能导致全部本金损失
> - 请务必使用模拟盘进行测试，不要直接用实盘
> - AI分析结果仅供参考，不保证收益
> - 使用本系统产生的任何损失，开发者不承担责任
> - 请在充分了解风险后谨慎使用

---

## 📖 项目简介

QuantumTrader AI 是一个开源的AI驱动量化交易系统，专注于加密货币交易。系统采用前后端分离架构，集成了多种经典交易策略、AI分析能力、风控系统和实时数据推送。

无论你是量化交易新手还是资深开发者，都可以基于这个系统快速搭建自己的交易机器人。

---

## ✨ 功能特性

### 🔧 核心功能

- **多交易所支持** - 目前支持欧易（OKX），架构可扩展
- **6种经典策略** - 均线交叉、网格、RSI、MACD、布林带、定投
- **策略回测** - 历史数据回测，评估策略效果
- **实盘运行** - 策略自动运行，24小时无人值守
- **三级风控** - 系统级+策略级+单交易级，资金安全第一
- **AI智能分析** - DeepSeek AI驱动，行情分析、策略解释

### 📊 专业图表

- **K线图** - 蜡烛图 + 4种指标（MA/MACD/RSI/BOLL）
- **资金曲线** - 总资产走势，多时间范围
- **深度图** - 买卖盘深度，实时更新
- **资产分布** - 饼图展示各币种持仓占比
- **策略收益** - 策略收益曲线，实时更新
- **回测分析** - 收益曲线 + 回撤曲线，双图联动

### 📡 实时推送

- **WebSocket架构** - 订阅机制、心跳保活、自动重连
- **行情实时更新** - 价格、涨跌幅实时跳动
- **订单状态推送** - 成交、撤单实时通知
- **持仓盈亏推送** - 未实现盈亏实时变化
- **余额变动推送** - 成交后余额实时更新

### 🎯 期权交易

- **T型报价** - 看涨左/行权价中/看跌右
- **希腊字母** - Delta/Gamma/Theta/Vega完整显示
- **多到期日** - 支持多个到期日切换
- **完整交互** - 选期权 → 下单 → 持仓 → 平仓

### 📱 响应式设计

- **PC端** - 完整功能，专业交易终端体验
- **平板端** - 自适应布局，兼顾功能和体验
- **移动端** - 底部导航，卡片式布局，触摸友好

### 🔐 安全可靠

- **API密钥加密** - AES-256加密存储，脱敏显示
- **JWT认证** - 安全的用户认证系统
- **强制风控** - 下单前必检，不可绕过
- **三级熔断** - 亏损达到阈值自动暂停

---

## 🛠️ 技术栈

### 前端

- **Vue 3** - 渐进式JavaScript框架
- **TypeScript** - 类型安全
- **Vite** - 下一代前端构建工具
- **Pinia** - Vue状态管理
- **Element Plus** - Vue 3组件库
- **ECharts** - 数据可视化图表库
- **Vue Router** - 官方路由
- **TailwindCSS** - 实用优先的CSS框架

### 后端

- **Python 3.12+** - 简洁优雅的编程语言
- **FastAPI** - 高性能异步Web框架
- **SQLAlchemy** - Python ORM工具
- **SQLite** - 轻量级数据库（可扩展PostgreSQL）
- **JWT** - JSON Web Token认证
- **WebSocket** - 实时双向通信
- **Fernet** - AES-256加密

### 外部服务

- **欧易（OKX）** - 加密货币交易所
- **DeepSeek** - AI大模型
- **PushPlus** - 微信消息推送
- **llama.cpp** - 本地模型推理（开发中）

---

## 🚀 快速开始

### 环境要求

- Node.js >= 18.0.0
- Python >= 3.12
- Git

### 一键启动

```bash
# 克隆项目
git clone https://github.com/QuantumTrader-AI/quantum-trader-ai.git
cd quantum-trader-ai

# 启动脚本
./start.sh all
```

### 详细安装

请查看 [INSTALL.md](INSTALL.md) 获取详细的安装说明。

### 测试账号

系统启动时自动创建两个测试账号：

| 角色 | 邮箱 | 密码 |
|------|------|------|
| 普通用户 | test@quantumtrader.ai | Test123456 |
| 管理员 | admin@quantumtrader.ai | Admin123456 |

### 访问地址

- 前端：http://localhost:5173
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

---

## 📁 项目结构

```
quantum-trader-ai/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── api/               # API路由
│   │   ├── models/            # 数据模型
│   │   ├── services/          # 业务服务
│   │   ├── websocket/         # WebSocket
│   │   ├── utils/             # 工具函数
│   │   ├── config.py          # 配置
│   │   ├── database.py        # 数据库
│   │   └── main.py            # 入口
│   ├── .env.example           # 环境变量示例
│   └── requirements.txt       # Python依赖
├── src/                        # 前端代码
│   ├── api/                   # API接口层
│   ├── components/            # 组件
│   │   ├── charts/            # 图表组件
│   │   ├── common/            # 通用组件
│   │   ├── layout/            # 布局组件
│   │   └── option/            # 期权组件
│   ├── views/                 # 页面
│   ├── stores/                # 状态管理
│   ├── utils/                 # 工具函数
│   ├── router/                # 路由
│   └── App.vue                # 根组件
├── .env.example                # 前端环境变量示例
├── .gitignore                  # Git忽略文件
├── start.sh                    # 启动脚本
├── README.md                   # 项目说明
├── INSTALL.md                  # 安装说明
├── DEVELOPMENT.md              # 开发指南
├── DEVELOPMENT_PROMPT.md       # 开发提示词文档
├── ROADMAP.md                  # 开发路线图
├── CONTRIBUTING.md             # 贡献指南
└── LICENSE                     # 开源协议
```

---

## 📚 文档

- [README.md](README.md) - 项目介绍（本文档）
- [INSTALL.md](INSTALL.md) - 详细安装说明
- [DEVELOPMENT.md](DEVELOPMENT.md) - 开发指南
- [DEVELOPMENT_PROMPT.md](DEVELOPMENT_PROMPT.md) - 开发提示词文档（给AI/开发者的完整开发指南）
- [ROADMAP.md](ROADMAP.md) - 开发路线图
- [CONTRIBUTING.md](CONTRIBUTING.md) - 贡献指南

---

## 🗺️ 开发路线图

### ✅ 已完成

- [x] 后端基础框架
- [x] 用户认证系统
- [x] API密钥加密存储
- [x] 欧易模拟盘对接
- [x] 行情数据接口
- [x] DeepSeek AI功能
- [x] PushPlus通知推送
- [x] 策略回测框架
- [x] WebSocket实时推送
- [x] 三级风控系统
- [x] 策略实盘运行引擎（6个策略）
- [x] 6个专业图表组件
- [x] 期权交易页面
- [x] 响应式设计基础

### 🔄 进行中

- [ ] 页面级WebSocket集成
- [ ] 移动端页面全面适配
- [ ] llama.cpp本地模型集成

### 📋 计划中

- [ ] 更多策略类型
- [ ] 更多交易所支持
- [ ] 策略社区/分享
- [ ] 合约交易支持
- [ ] 移动端APP
- [ ] 机器学习预测模型

详细路线图请查看 [ROADMAP.md](ROADMAP.md)

---

## 🤝 贡献指南

我们欢迎任何形式的贡献！

### 如何贡献

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

### 代码规范

- 前端遵循 Vue 3 + TypeScript 最佳实践
- 后端遵循 PEP 8 规范
- 提交信息遵循 [Conventional Commits](https://www.conventionalcommits.org/)

详细说明请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## ⚠️ 风险提示

**请务必仔细阅读：**

1. **加密货币交易风险极高**，价格波动大，可能导致全部本金损失
2. **本项目仅供学习研究**，不构成任何投资建议
3. **请务必使用模拟盘测试**，不要直接用实盘资金
4. **历史收益不代表未来表现**，策略可能失效
5. **AI分析结果仅供参考**，不保证准确性
6. **请根据自己的风险承受能力谨慎决策**
7. **使用本系统产生的任何损失，开发者不承担责任**

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 💬 交流讨论

- **GitHub Issues** - 提交Bug和功能建议
- **Discussions** - 技术交流和讨论
- **文档** - 查看详细文档

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐ Star 支持一下！**

Made with ❤️ by QuantumTrader AI Team

</div>
