# AI Writer

一个基于 AI 的智能写作助手，支持文档生成、编辑和优化。

## 功能特性

### 核心功能
- 📝 **章节管理** - 创建、编辑、删除小说章节，支持 Markdown 编辑
- 👥 **角色管理** - 角色卡片、特征向量、相似角色推荐
- 🔗 **关系图谱** - 可视化角色关系网络
- 📍 **地点管理** - 故事发生地点的设定与管理
- 📋 **大纲规划** - 树形大纲编辑器，支持拖拽排序
- 💡 **灵感管理** - 收藏和整理写作灵感
- 🕐 **时间线** - 故事时间线可视化

### AI 辅助功能
- 🤖 **AI 续写** - 基于上下文智能续写章节
- 💬 **AI 对话** - 角色对话生成
- 🔍 **AI 审核** - 语法检查、敏感词过滤
- 📊 **AI 优化** - 大纲结构优化建议
- 🗺️ **AI 地图生成** - 基于设定生成地图描述
- 🔮 **灵感生成** - Fandom 风格灵感推荐

### 导出与导入
- 📤 **多格式导出** - 支持 JSON、Markdown、Word (docx)、TXT、Excel
- 📥 **多格式导入** - 支持从 JSON、ZIP、文件夹批量导入
- 📑 **章节导出** - 单章节或多章节导出

### 插件系统
- 🔌 **插件市场** - 可扩展的插件架构
- �钩子系统 - 支持 on_chapter_complete 等生命周期钩子
- ⚙️ **示例插件** - custom_instruction（自动签名）、voice_input（语音输入占位）

### 特色功能
- 🖼️ **图片库** - AI 生成图片与本地上传管理
- 📖 **Fandom 工作流** - 从参考资料提取灵感
- 🏠 **世界设定** - 人物/地点/物品/组织/概念分类管理

## 快速开始

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

### 6. 启动服务

**启动后端：**
```bash
cd backend
uv run uvicorn src.api.main:app --reload --port 8000
```
后端 API 文档: http://localhost:8000/docs

**启动前端（另开终端）：**
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
│   ├── plugins/         # 插件目录
│   │   ├── custom_instruction/  # 自定义签名插件
│   │   └── voice_input/         # 语音输入占位插件
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
