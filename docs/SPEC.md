# AI Writer - Sprint 1 需求规格说明书（SPEC.md）

> 版本：v1.0.0 | 日期：2026-03-27 | Sprint：Sprint 1 - 项目基础设施 + 书架管理

---

## 一、Sprint 概述

**Sprint 目标**：完成项目基础设施搭建，实现书架管理核心功能（项目管理 CRUD）。

**交付物**：
- 完整的后端 API（FastAPI + SQLite）
- 前端骨架（React + TypeScript）
- CI/CD 自动化配置
- 可运行的项目原型

**团队**：Requirements Agent / Backend Agent / Frontend Agent / DevOps Agent

---

## 二、需求规格

### REQ-001 | 项目基础设施 - 目录结构

**模块**：基础设施
**标题**：项目目录结构初始化
**优先级**：Must Have

**功能描述**：
```
ai-writer/
├── backend/
│   ├── src/
│   │   ├── api/          # API 路由
│   │   ├── core/         # 核心配置（数据库、LLM）
│   │   ├── models/       # SQLModel 数据模型
│   │   ├── schemas/      # Pydantic 请求/响应 schema
│   │   ├── services/     # 业务逻辑
│   │   └── utils/       # 工具函数
│   ├── tests/
│   │   ├── unit/        # 单元测试
│   │   └── integration/ # 集成测试
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/   # UI 组件
│   │   ├── pages/       # 页面
│   │   ├── hooks/       # React Hooks
│   │   ├── store/       # Zustand 状态管理
│   │   └── utils/      # 工具函数
│   └── package.json
├── docs/
│   ├── SPEC.md          # 本文档
│   └── DESIGN.md        # 产品设计
├── scripts/
│   └── init_db.py       # 数据库初始化
├── .github/workflows/
│   └── ci.yml           # CI/CD 配置
└── README.md
```

**验收标准**：
- [ ] 目录结构与设计一致
- [ ] 所有 `__init__.py` 文件存在
- [ ] pyproject.toml 和 package.json 依赖完整

---

### REQ-002 | 项目基础设施 - 数据库初始化

**模块**：基础设施
**标题**：SQLite 数据库初始化
**优先级**：Must Have
**依赖**：REQ-001

**数据库路径**：`~/.aiwriter/projects/{project_id}/project.db`

**表结构**：

```sql
-- Project 表
CREATE TABLE projects (
    id TEXT PRIMARY KEY,           -- UUID
    name TEXT NOT NULL,
    genre TEXT,                     -- 题材：修仙/都市/玄幻/穿越等
    description TEXT,
    total_words_target INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',    -- active/archived/deleted
    created_at TEXT NOT NULL,        -- ISO8601
    updated_at TEXT NOT NULL
);

-- Character 表（预留，Sprint 2）
CREATE TABLE characters (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    aliases TEXT,                    -- JSON 数组
    gender TEXT,
    age TEXT,
    appearance TEXT,
    personality TEXT,
    background TEXT,
    arc TEXT,                       -- 人物弧光
    avatar_url TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Relationship 表（预留，Sprint 2）
CREATE TABLE relationships (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    from_character_id TEXT REFERENCES characters(id) ON DELETE CASCADE,
    to_character_id TEXT REFERENCES characters(id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL,
    direction TEXT DEFAULT 'bidirectional',
    strength INTEGER DEFAULT 5,
    created_at TEXT NOT NULL
);

-- Chapter 表（预留，Sprint 2）
CREATE TABLE chapters (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    outline_id TEXT,
    title TEXT NOT NULL,
    content TEXT DEFAULT '',
    word_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'draft',    -- draft/writing/completed/reviewed
    sort_order INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Inspiration 表（预留，Sprint 2）
CREATE TABLE inspirations (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    tags TEXT,                      -- JSON 数组
    related_setting_ids TEXT,        -- JSON 数组
    created_at TEXT NOT NULL
);
```

**验收标准**：
- [ ] 数据库文件在正确路径创建
- [ ] 所有表按上述结构创建
- [ ] 支持外键约束
- [ ] 初始化脚本幂等（重复执行不报错）

---

### REQ-003 | 项目基础设施 - FastAPI 入口

**模块**：基础设施
**标题**：FastAPI 应用入口 + 依赖注入
**优先级**：Must Have
**依赖**：REQ-001

**功能描述**：
```python
# src/api/main.py
app = FastAPI(
    title="AI Writer API",
    version="0.1.0",
    description="AI 小说创作辅助平台后端 API"
)

# CORS 配置（开发允许 localhost:5173）
# 路由挂载：/api/v1/projects
# 健康检查：GET /health
```

**配置管理（`src/core/config.py`）**：
```python
# 环境变量
AIWRITER_DB_PATH: str      # 数据库根目录，默认 ~/.aiwriter
AIWRITER_LLM_PROVIDER: str  # ollama / openai / deepseek
AIWRITER_LLM_BASE_URL: str  # LLM API 地址
AIWRITER_LLM_API_KEY: str   # API Key（可选）
AIWRITER_LLM_MODEL: str     # 模型名称
```

**验收标准**：
- [ ] `GET /health` 返回 `{"status": "ok", "version": "0.1.0"}`
- [ ] CORS 允许前端开发服务器访问
- [ ] 所有配置从环境变量读取（无硬编码）

---

### REQ-004 | 书架管理 - 项目 CRUD API

**模块**：书架管理
**标题**：项目创建/查询/更新/删除
**优先级**：Must Have
**依赖**：REQ-002, REQ-003

#### 1. 创建项目

**接口**：`POST /api/v1/projects`

**请求 Schema**（`ProjectCreate`）：
```python
{
    "name": str,          # 必填，项目名称
    "genre": str,         # 可选，题材
    "description": str,    # 可选，简介
    "total_words_target": int  # 可选，字数目标，默认为 0
}
```

**响应 Schema**（`Project`）：
```python
{
    "id": str,               # UUID
    "name": str,
    "genre": str,
    "description": str,
    "total_words_target": int,
    "status": str,
    "created_at": str,       # ISO8601
    "updated_at": str
}
```

**业务逻辑**：
1. 生成 UUID 作为 id
2. 状态默认为 "active"
3. 创建时间戳
4. 在 `~/.aiwriter/projects/{id}/` 下初始化数据库

**验收标准**：
- [ ] 返回 201 Created
- [ ] 响应包含完整 Project 字段
- [ ] 项目目录自动创建
- [ ] 重名项目允许（不强制唯一）

#### 2. 查询项目列表

**接口**：`GET /api/v1/projects`

**Query 参数**：
```
?page=1           # 页码，默认 1
?page_size=20     # 每页数量，默认 20，最大 100
?sort_by=updated_at  # 排序字段：name/created_at/updated_at
?sort_order=desc     # 排序方向：asc/desc
?status=active       # 筛选状态，默认显示 active
?search=关键词       # 搜索项目名称/简介
```

**响应 Schema**（`ProjectListResponse`）：
```python
{
    "items": [Project, ...],  # 项目列表
    "total": int,             # 总数
    "page": int,              # 当前页
    "page_size": int,         # 每页数量
    "pages": int               # 总页数
}
```

**验收标准**：
- [ ] 支持分页
- [ ] 支持排序
- [ ] 支持状态筛选
- [ ] 支持关键词搜索（模糊匹配 name 或 description）

#### 3. 查询单个项目

**接口**：`GET /api/v1/projects/{id}`

**路径参数**：`id` - 项目 UUID

**响应 Schema**：`Project`

**验收标准**：
- [ ] 返回 200 OK
- [ ] 无效 UUID 返回 404 Not Found

#### 4. 更新项目

**接口**：`PUT /api/v1/projects/{id}`

**请求 Schema**（`ProjectUpdate`）：
```python
{
    "name": str,              # 可选
    "genre": str,             # 可选
    "description": str,       # 可选
    "total_words_target": int, # 可选
    "status": str             # 可选：active/archived
}
```

**响应 Schema**：`Project`

**验收标准**：
- [ ] 返回 200 OK
- [ ] 支持部分更新（不传的字段不变）
- [ ] updated_at 自动更新为当前时间
- [ ] 无效 UUID 返回 404

#### 5. 删除项目

**接口**：`DELETE /api/v1/projects/{id}`

**Query 参数**：
```
?hard=false   # 软删除（改 status=deleted），默认 false
```

**响应**：`204 No Content`

**验收标准**：
- [ ] soft delete（默认）：仅改 status = "deleted"
- [ ] hard delete（?hard=true）：删除数据库文件和所有数据
- [ ] 无效 UUID 返回 404

---

### REQ-005 | 书架管理 - 项目统计

**模块**：书架管理
**标题**：项目统计数据 API
**优先级**：Should Have
**依赖**：REQ-004

**接口**：`GET /api/v1/projects/{id}/stats`

**响应 Schema**：
```python
{
    "id": str,
    "name": str,
    "total_words": int,       # 累计字数
    "chapter_count": int,      # 章节数
    "character_count": int,    # 角色数
    "outline_progress": float, # 大纲完成度 0.0-1.0
    "writing_progress": float,  # 写作完成度 0.0-1.0
    "updated_at": str
}
```

**验收标准**：
- [ ] 各统计数据准确
- [ ] 进度计算公式：writing_progress = total_words / total_words_target

---

### REQ-006 | 书架管理 - 导入导出

**模块**：书架管理
**标题**：.aiwriter 格式导入导出
**优先级**：Should Have
**依赖**：REQ-004

#### 导出

**接口**：`POST /api/v1/projects/{id}/export`

**响应**：
```
Content-Type: application/json
Content-Disposition: attachment; filename="{project_name}.aiwriter"
```

**.aiwriter 格式**（JSON 压缩包）：
```json
{
    "version": "1.0",
    "exported_at": "2026-03-27T10:00:00Z",
    "project": { /* Project 所有字段 */ },
    "chapters": [ /* Chapter 所有字段 */ ],
    "characters": [ /* Character 所有字段 */ ],
    "relationships": [ /* Relationship 所有字段 */ ]
}
```

**验收标准**：
- [ ] 导出为完整 JSON 文件
- [ ] 包含所有关联数据
- [ ] 文件名格式：`{project_name}_{date}.aiwriter`

#### 导入

**接口**：`POST /api/v1/projects/import`

**请求**：`multipart/form-data`
```
file: .aiwriter 文件
```

**响应 Schema**：`Project`

**验收标准**：
- [ ] 解析 .aiwriter 文件
- [ ] 导入后创建新项目（id 重新生成）
- [ ] 关联数据（chapters/characters）一并导入
- [ ] 无效文件返回 400 Bad Request

---

### REQ-007 | 书架管理 - 文件上传解析

**模块**：书架管理
**标题**：TXT/MD 文件上传智能解析
**优先级**：Should Have
**依赖**：REQ-004

**接口**：`POST /api/v1/projects/{id}/upload`

**请求**：`multipart/form-data`
```
file: TXT 或 MD 文件
encoding: utf-8/gbk（自动检测，默认 utf-8）
chunk_mode: auto/chapter/section/paragraph
```

**业务逻辑**：
1. 读取文件内容
2. 智能章节切分（识别"第X章"模式）
3. 生成 Chapter 记录

**响应 Schema**：
```python
{
    "project_id": str,
    "chapters_created": int,
    "total_words": int,
    "chunks": [
        { "title": str, "word_count": int, "content_preview": str }
    ]
}
```

**验收标准**：
- [ ] 支持 UTF-8 和 GBK 编码
- [ ] 正确识别"第X章"标题
- [ ] 返回切分结果预览
- [ ] 文件超过 10MB 返回 413

---

## 三、技术规范

### 3.1 后端规范

**框架**：FastAPI + Uvicorn（ASGI）
**数据模型**：SQLModel（SQLAlchemy + Pydantic）
**数据库**：SQLite + aiosqlite（异步）
**验证**：Pydantic V2
**测试**：pytest + pytest-asyncio + httpx

**错误响应格式**：
```json
{
    "detail": "错误描述",
    "code": "PROJECT_NOT_FOUND"
}
```

**HTTP 状态码**：
- 200 OK：查询/更新成功
- 201 Created：创建成功
- 204 No Content：删除成功
- 400 Bad Request：请求参数错误
- 404 Not Found：资源不存在
- 413 Payload Too Large：文件过大
- 500 Internal Server Error：服务器错误

### 3.2 前端规范

**框架**：React 19 + TypeScript 5
**构建工具**：Vite 5
**路由**：React Router DOM 6
**数据获取**：TanStack React Query 5
**状态管理**：Zustand 4（预留）
**样式**：Tailwind CSS 3

**API 代理**：Vite 开发服务器代理 `/api` → `http://localhost:8000`

### 3.3 代码规范

**Python**：
- 类型注解（mypy strict）
- docstring（Google 风格）
- 异步优先（async/await）
- 错误处理：try/except + 自定义异常类

**TypeScript**：
- 严格模式（strict: true）
- 接口 > 类型别名
- 组件：函数组件 + Hooks
- 样式：Tailwind CSS class

---

## 四、非功能需求

| 类型 | 要求 |
|------|------|
| **性能** | API 响应时间 < 200ms（不含 LLM 调用） |
| **容量** | 单项目支持 100 万字正文 |
| **兼容性** | Python 3.9+，Node.js 18+ |
| **可移植性** | 数据存储在 ~/.aiwriter，数据可迁移 |

---

## 五、Sprint 2 预告

- REQ-008：灵感速记 CRUD
- REQ-009：人物关系图谱 CRUD
- REQ-010：角色关系网络 API
- REQ-011：世界地图基础 API
- REQ-012：大纲节点 CRUD

---

*本文档由 Requirements Agent 生成 | 2026-03-27*
