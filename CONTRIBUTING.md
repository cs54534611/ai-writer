# 贡献指南

感谢您对 AI Writer 项目的关注！我们欢迎各种形式的贡献，包括但不限于代码、文档、问题反馈和功能建议。

## 如何贡献

### 1. Fork 仓库

首先，Fork 本仓库到您的 GitHub 账户。

### 2. 克隆您的 Fork

```bash
git clone https://github.com/yourusername/ai-writer.git
cd ai-writer
```

### 3. 添加上游仓库

```bash
git remote add upstream https://github.com/originalowner/ai-writer.git
```

### 4. 创建功能分支

```bash
git checkout -b feature/your-feature-name
# 或修复 bug
git checkout -b fix/your-bug-fix
```

## 开发环境搭建

### 后端

```bash
cd backend

# 使用 uv (推荐)
pip install uv
uv sync

# 激活虚拟环境
uv venv .venv
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows

# 安装开发依赖
uv pip install -e ".[dev]"

# 初始化数据库
python ../scripts/init_db.py
```

### 前端

```bash
cd frontend

# 安装 pnpm (如果没有)
npm install -g pnpm

# 安装依赖
pnpm install

# 复制环境变量
cp .env.example .env
```

### 运行开发服务器

```bash
# 后端
cd backend
uv run uvicorn src.api.main:app --reload --port 8000

# 前端 (新终端)
cd frontend
pnpm dev
```

## 代码规范

### Python (后端)

我们使用以下工具维护代码风格：

- **black** - 代码格式化
- **isort** - import 排序
- **ruff** - 代码检查

格式化代码：

```bash
cd backend
uv run black src/
uv run isort src/
uv run ruff check src/ --fix
```

运行检查：

```bash
cd backend
uv run ruff check src/
uv run mypy src/
```

### TypeScript/React (前端)

我们使用以下工具：

- **ESLint** - 代码检查
- **Prettier** - 代码格式化

格式化代码：

```bash
cd frontend
pnpm format
pnpm lint
```

## 提交规范

请遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

类型 (type):

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档变更
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具变更

示例：

```
feat(editor): 添加实时预览功能

fix(api): 修复文档保存接口的并发问题

docs(readme): 更新安装说明
```

## Pull Request 流程

### 1. 保持分支同步

在创建 PR 之前，确保您的分支与上游同步：

```bash
git fetch upstream
git rebase upstream/main
```

### 2. 推送您的分支

```bash
git push origin feature/your-feature-name
```

### 3. 创建 Pull Request

1. 访问您的 Fork 仓库
2. 点击 "New Pull Request"
3. 选择您的分支并填写 PR 描述
4. 确保所有 CI 检查通过

### PR 描述模板

```markdown
## 描述
简要说明您的更改。

## 更改类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 破坏性变更
- [ ] 文档更新

## 测试
描述您是如何测试这些更改的。

## 截图（如适用）
添加截图帮助审查。
```

## 测试

### 后端测试

```bash
cd backend
uv run pytest tests/ -v

# 带覆盖率
uv run pytest tests/ -v --cov=src --cov-report=html
```

### 前端测试

```bash
cd frontend
pnpm test
pnpm test:coverage
```

## 报告问题

请使用 GitHub Issues 报告问题。提供以下信息：

- 清晰的标题和描述
- 复现步骤
- 预期行为 vs 实际行为
- 环境信息（操作系统、Python/Node.js 版本等）
- 错误日志（如有）

## 许可证

通过贡献代码，您同意您的贡献将采用 [AGPL-3.0](LICENSE) 许可证。
