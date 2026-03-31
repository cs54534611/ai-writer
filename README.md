# AI Writer

一个基于 AI 的智能写作助手，支持文档生成、编辑和优化。

## 功能特性

- 🤖 AI 驱动的写作辅助
- 📄 多格式文档支持
- 🔄 实时编辑预览
- 💾 本地数据存储
- 🎨 现代化的用户界面

## 技术栈

- **后端**: Python 3.11+, FastAPI, SQLAlchemy
- **前端**: TypeScript, React, Vite, TailwindCSS
- **数据库**: SQLite (默认)
- **AI**: 支持多种 LLM 提供商 (OpenAI, Anthropic, 本地模型)

## 安装步骤

### 前置要求

- Python 3.11+
- Node.js 18+
- pnpm (推荐) 或 npm

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/ai-writer.git
cd ai-writer
```

### 2. 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 安装依赖
pip install -e .

# 或者使用 uv (推荐)
pip install uv
uv sync
```

### 3. 前端设置

```bash
cd frontend
pnpm install
```

### 4. 环境配置

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

详细配置说明见 [LLM 配置说明](#llm-配置说明)。

### 5. 初始化数据库

```bash
python scripts/init_db.py
```

## 快速开始

### 启动后端服务

```bash
cd backend
uv run uvicorn src.api.main:app --reload --port 8000
```

后端 API 文档: http://localhost:8000/docs

### 启动前端开发服务器

```bash
cd frontend
pnpm dev
```

前端应用: http://localhost:5173

## 本地开发指南

### 开发工具

- **后端**: 使用 `uv` 管理 Python 依赖和虚拟环境
- **前端**: 使用 `pnpm` 管理 Node.js 依赖
- **代码格式化**: 
  - 后端: `black`, `isort`
  - 前端: `prettier`, `eslint`

### 运行测试

**后端测试:**
```bash
cd backend
uv run pytest tests/ -v
```

**前端测试:**
```bash
cd frontend
pnpm test
```

### 代码规范检查

**后端:**
```bash
cd backend
uv run black src/
uv run isort src/
uv run ruff check src/
```

**前端:**
```bash
cd frontend
pnpm lint
pnpm format
```

## LLM 配置说明

AI Writer 支持多种 LLM 提供商。通过环境变量配置：

### OpenAI

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
OPENAI_BASE_URL=https://api.openai.com/v1
```

### Anthropic (Claude)

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

### 本地模型 (Ollama)

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### Azure OpenAI

```env
LLM_PROVIDER=azure
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://xxx.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-4
```

## 项目结构

```
ai-writer/
├── backend/              # Python 后端
│   ├── src/
│   │   ├── api/         # API 路由
│   │   ├── core/        # 核心配置
│   │   ├── models/      # 数据模型
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # 业务逻辑
│   │   └── utils/       # 工具函数
│   ├── tests/           # 测试文件
│   └── pyproject.toml   # 项目配置
├── frontend/            # React 前端
│   ├── src/
│   │   ├── components/ # React 组件
│   │   ├── pages/       # 页面
│   │   ├── hooks/       # 自定义 Hooks
│   │   ├── store/       # 状态管理
│   │   └── utils/       # 工具函数
│   └── package.json
├── docs/                # 文档
├── scripts/             # 脚本
│   └── init_db.py      # 数据库初始化
├── .env.example         # 环境变量示例
├── LICENSE              # AGPL-3.0 许可证
└── README.md
```

## License

本项目采用 [AGPL-3.0](LICENSE) 开源协议。
