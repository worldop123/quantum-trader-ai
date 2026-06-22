# 贡献指南

感谢您对 QuantumTrader AI 的关注！我们欢迎任何形式的贡献，包括但不限于代码、文档、Bug 报告、功能建议等。

---

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发环境搭建](#开发环境搭建)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [Pull Request 流程](#pull-request-流程)
- [Issue 模板](#issue-模板)
- [社区](#社区)

---

## 行为准则

参与本项目即表示您同意遵守以下行为准则：

1. **尊重他人** - 友善、耐心地对待其他贡献者
2. **包容差异** - 欢迎不同背景和经验的人
3. **建设性反馈** - 提供有价值的反馈和建议
4. **对自己的行为负责** - 对自己的代码和言论负责
5. **关注社区利益** - 以项目整体利益为重

---

## 如何贡献

### 1. 报告 Bug

如果您发现了 Bug，请通过 Issue 报告。报告时请包含：

- **清晰的标题** - 简要描述问题
- **复现步骤** - 详细说明如何复现问题
- **预期行为** - 您期望的正确行为
- **实际行为** - 实际发生的错误行为
- **环境信息** - 操作系统、Python 版本、Node 版本等
- **截图/日志** - 如果有，请附上

### 2. 功能建议

如果您有新功能的想法，欢迎通过 Issue 提出。建议时请说明：

- **功能描述** - 这个功能是什么
- **使用场景** - 为什么需要这个功能
- **实现思路** - 您对实现方式的想法（可选）
- **参考资料** - 相关的链接或参考（可选）

### 3. 贡献代码

如果您想贡献代码，请遵循以下流程：

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

---

## 开发环境搭建

### 前置要求

- Python 3.12+
- Node.js 18+
- npm 或 yarn
- Git

### 后端环境

```bash
# 克隆仓库
git clone https://github.com/your-username/quantum-trader-ai.git
cd quantum-trader-ai

# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要的配置

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 前端环境

```bash
# 进入前端目录（项目根目录）
cd quantum-trader-ai

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 启动开发服务器
npm run dev
```

### 测试账号

| 角色 | 邮箱 | 密码 |
|------|------|------|
| 普通用户 | test@quantumtrader.ai | Test123456 |
| 管理员 | admin@quantumtrader.ai | Admin123456 |

---

## 代码规范

### Python 代码规范

1. **遵循 PEP 8**
   - 缩进 4 个空格
   - 行长度不超过 120 字符
   - 空行分隔函数和类

2. **类型注解**
   - 所有函数都要有类型注解
   - 复杂类型使用 `typing` 模块

   ```python
   def calculate_rsi(prices: list[float], period: int = 14) -> float:
       """计算RSI指标"""
       pass
   ```

3. **Docstring**
   - 所有公共函数和类都要有 docstring
   - 使用 Google 风格或 NumPy 风格

   ```python
   def get_balance(user_id: int) -> dict:
       """
       获取用户账户余额
       
       Args:
           user_id: 用户ID
           
       Returns:
           包含余额信息的字典
           
       Raises:
           UserNotFoundError: 用户不存在
       """
       pass
   ```

4. **命名规范**
   - 函数名：snake_case
   - 类名：PascalCase
   - 常量：UPPER_SNAKE_CASE
   - 变量：snake_case

### Vue / TypeScript 代码规范

1. **Vue 3 Composition API**
   - 使用 `<script setup>` 语法
   - 优先使用组合式 API

2. **TypeScript 类型**
   - 所有 props 要有类型
   - 所有函数要有返回类型
   - 定义接口 interface

   ```typescript
   interface Position {
     symbol: string
     quantity: number
     avgPrice: number
     currentPrice: number
     pnl: number
     pnlRatio: number
   }
   ```

3. **组件命名**
   - 组件名：PascalCase
   - 组件文件名和组件名一致
   - 多单词命名（避免单个单词）

4. **命名规范**
   - 函数名：camelCase
   - 组合式函数：use 开头
   - 常量：UPPER_SNAKE_CASE

### 通用规范

1. **注释**
   - 复杂逻辑必须有注释
   - 业务规则要说明原因
   - TODO/FIXME 要标注日期和说明

   ```python
   # TODO: 2024-06-22 优化性能，当前算法时间复杂度O(n²)
   ```

2. **错误处理**
   - 所有可能出错的地方都要有错误处理
   - 友好的错误提示
   - 记录错误日志

3. **安全性**
   - API 密钥加密存储
   - 输入验证
   - 防止 SQL 注入和 XSS

---

## 提交规范

我们遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范。

### 提交格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

| 类型 | 说明 |
|------|------|
| feat | 新功能 |
| fix | 修复 Bug |
| docs | 文档更新 |
| style | 代码格式（不影响功能） |
| refactor | 重构（既不是新功能也不是修 Bug） |
| perf | 性能优化 |
| test | 测试相关 |
| chore | 构建/工具等辅助工具的变动 |
| ci | CI/CD 相关 |

### Scope 范围（可选）

影响的模块，如：`auth`, `trading`, `strategy`, `websocket`, `ui` 等。

### Subject 主题

简短描述，不超过 50 字符，使用祈使句。

### Body 正文（可选）

详细描述，可以分成多行。

### Footer 页脚（可选）

- 关闭 Issue：`Closes #123`
- 破坏性变更：`BREAKING CHANGE: 描述`

### 示例

```
feat(strategy): 添加布林带策略

实现布林带策略的回测和实盘运行功能
- 支持参数配置（周期、标准差倍数）
- 支持止盈止损
- 经过风控检查

Closes #45
```

```
fix(websocket): 修复断线重连后订阅丢失的问题

- 重连后自动恢复之前的订阅
- 添加订阅状态持久化
- 优化重连逻辑

Closes #123
```

---

## Pull Request 流程

### 提交前检查

在提交 Pull Request 之前，请确保：

- [ ] 代码符合项目的代码规范
- [ ] 所有新功能都有相应的测试（如果适用）
- [ ] 所有测试通过
- [ ] 文档已更新（如果需要）
- [ ] 代码没有明显的性能问题
- [ ] 没有引入安全漏洞
- [ ] 提交信息符合规范

### PR 描述模板

```
## 描述
简要描述这个 PR 做了什么。

## 类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 性能优化
- [ ] 文档更新
- [ ] 代码重构
- [ ] 其他

## 关联 Issue
Closes #123

## 测试
- [ ] 单元测试
- [ ] 集成测试
- [ ] 手动测试

## 截图（如果适用）
附上相关截图

## 注意事项
有什么需要特别注意的吗？
```

### 代码审查

- 所有 PR 都需要至少一个维护者审查
- 审查者可能会提出修改建议
- 请及时响应审查意见
- 审查通过后会被合并

---

## Issue 模板

### Bug 报告模板

```
## Bug 描述
简要描述这个 Bug 是什么。

## 复现步骤
1. 前往 '...'
2. 点击 '....'
3. 滚动到 '....'
4. 看到错误

## 预期行为
描述您期望发生的事情。

## 实际行为
描述实际发生的事情。

## 环境信息
- 操作系统：
- Python 版本：
- Node 版本：
- 浏览器：

## 截图/日志
如果适用，请附上截图或错误日志。
```

### 功能建议模板

```
## 功能描述
简要描述您想要的功能。

## 使用场景
描述这个功能的使用场景，为什么需要它。

## 实现思路
您对实现方式有什么想法吗？（可选）

## 参考资料
相关的链接、文档或参考项目。（可选）
```

---

## 社区

- **GitHub Issues** - Bug 报告、功能建议
- **Discussions** - 讨论、问答、交流
- **贡献者** - 感谢所有贡献者

---

## 感谢

感谢您为 QuantumTrader AI 做出的贡献！每一份贡献都很重要。

---

**最后更新：** 2024-06-22
