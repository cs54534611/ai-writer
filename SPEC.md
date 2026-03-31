# AI Writer - Sprint 1 需求规格说明书

> 版本：v1.0 | 日期：2026-03-27 | 状态：草稿

---

## 一、项目概述

**AI Writer** 是一款面向中文网络小说作者的 AI 创作辅助平台，核心差异是将 AI-Reader 的"小说世界观提取"能力反过来——从"阅读分析已有小说"变为"创作阶段构建世界观"。

**目标用户**：新人网文作者、业余创作者、资深老手、工作室写手、同人文作者

**技术栈**：
- 前端：React 19 + TypeScript + Vite + Tailwind CSS 4 + shadcn/ui
- 桌面：Tauri 2（Rust）+ Python sidecar
- 后端：Python + FastAPI（async）+ aiosqlite
- 数据库：SQLite（结构化数据）+ ChromaDB（向量检索/RAG）
- LLM：Ollama（本地 qwen3:8b）+ 云端 API（DeepSeek/MiniMax/Claude/GPT）

---

## 二、已完成功能

| 需求ID | 模块 | 功能 | 验收标准 | 状态 |
|--------|------|------|----------|------|
| FE-PROJ-001 | 书架管理 | 多项目创建/编辑/删除 | 可创建项目并保存到 SQLite | DONE |
| FE-PROJ-002 | 书架管理 | 项目列表分页查询 | 支持分页、状态过滤 | DONE |
| FE-PROJ-003 | 书架管理 | 项目复制/归档 | 项目可复制和标记状态 | DONE |
| FE-CHAR-001 | 人物关系图谱 | 角色卡 CRUD | 角色姓名/性别/性格/背景/弧光 | DONE |
| FE-CHAR-002 | 人物关系图谱 | 角色关系管理 | 创建/编辑/删除角色间关系 | DONE |
| FE-CHAR-003 | 人物关系图谱 | 力导向图可视化 | D3.js 实现，支持拖拽/缩放/过滤 | DONE |
| FE-INS-001 | 灵感速记 | 灵感碎片记录 | 文字灵感快速记录 | DONE |
| FE-INS-002 | 灵感速记 | AI 自动标签分类 | AI 为灵感打标签（人物/场景/情节等） | DONE |
| FE-INS-003 | 灵感速记 | 一键升格 | 灵感可升格为角色卡或大纲条目 | DONE |
| FE-WRITE-001 | 正文撰写 | 智能编辑器 | 沉浸式全屏写作模式 | DONE |
| FE-WRITE-002 | 正文撰写 | 自动保存 | 每30秒自动保存 | DONE |
| FE-WRITE-003 | 正文撰写 | 字数统计 | 章节/卷/全书实时统计 | DONE |
| FE-WRITE-004 | 正文撰写 | AI 续写 | 基于上下文和设定的智能续写 | DONE |
| FE-WRITE-005 | 正文撰写 | AI 多版本候选 | 一次生成2-3个不同走向 | DONE |
| FE-WRITE-006 | 正文撰写 | AI 改写 | 润色/替代表达/口味调整 | DONE |
| FE-WRITE-007 | 正文撰写 | 对话式写作 | 与 AI 进行角色扮演对话推进剧情 | DONE |
| FE-FEEDBACK-001 | AI 即时反馈 | 选中章节 AI 反馈 | AI 给出"三个可改进方向" | DONE |
| FE-FEEDBACK-002 | AI 即时反馈 | 多维度反馈 | 节奏/角色/情节/文笔可选 | DONE |
| FE-REVIEW-001 | 阅读审查 | 前后矛盾检测 | 人物特征/关系状态/时间线矛盾检测 | DONE |
| FE-REVIEW-002 | 阅读审查 | 角色 OOC 检测 | AI 对照角色设定检测言行出戏 | DONE |
| FE-REVIEW-003 | 阅读审查 | 敏感词检测 | 内置敏感词库 + 自定义敏感词分级 | DONE |
| FE-EXPORT-001 | 导入导出 | .aiwriter 格式导入/导出 | 全量备份和恢复 | DONE |
| FE-EXPORT-002 | 导入导出 | TXT/MD 导入 | 拖拽上传，智能章节切分 | DONE |
| FE-EXPORT-003 | 导入导出 | 多格式导出 | MD/Word/Excel/PDF 导出 | DONE |
| FE-FANDOM-001 | 同人创作 | IP 设定导入 | 手动输入或 AI 分析原著文本提取 | DONE |
| FE-FANDOM-002 | 同人创作 | 同人设定追踪 | 自动追踪同人设定与原著差异 | DONE |
| FE-IMAGE-001 | AI 插图生成 | 角色/场景配图 | 根据设定生成配图 | DONE |
| FE-IMAGE-002 | AI 插图生成 | 多风格支持 | 写实/动漫/水墨古风 | DONE |
| FE-PLUGIN-001 | 插件系统 | 插件架构 | CSP 沙箱隔离的插件机制 | DONE |
| FE-PLUGIN-002 | 插件系统 | 内置插件 | 日志备份插件、字数目标插件 | DONE |
| FE-JOURNEY-001 | 创作旅程 | 进度仪表盘 | 可视化创作进度 | DONE |
| FE-JOURNEY-002 | 创作旅程 | AI 建议 | AI 给出下一步建议 | DONE |
| FE-JOURNEY-003 | 创作旅程 | 目标进度对比 | 目标字数 vs 实际进度 | DONE |
| FE-OUTLINE-001 | 大纲规划 | 树形大纲 | 卷→章→节→场景 树形结构 | DONE |
| FE-OUTLINE-002 | 大纲规划 | AI 大纲生成 | 按题材生成大纲模板 | DONE |
| FE-OUTLINE-003 | 大纲规划 | 伏笔管理 | 记录埋下的伏笔，合适时提醒回收 | DONE |
| FE-OUTLINE-004 | 大纲规划 | 主线/支线/暗线分类 | 分类标记不同叙事线 | DONE |

---

## 三、Sprint 1 待完成功能

### 3.1 MUST（必须完成）

| 需求ID | 模块 | 功能 | 验收标准 | 依赖 |
|--------|------|------|----------|------|
| BE-DB-001 | 数据库 | 多项目隔离 | 每个项目独立 SQLite 文件 | 无 |
| BE-DB-002 | 数据库 | ChromaDB 向量检索 | RAG 续写需要向量检索能力 | 无 |
| BE-WRITE-001 | 正文撰写 | 上下文感知续写 | 读取大纲+人物设定+世界观背景续写 | DB-002 |
| BE-WRITE-002 | 正文撰写 | 风格控制 | 模仿作者文风/对话稠密/描写稠密 | 无 |
| BE-CHAR-001 | 人物关系图谱 | AI 关系建议 | 输入两个角色背景，AI 建议关系走向 | LLM |
| BE-CHAR-002 | 人物关系图谱 | 别名自动合并 | "师父"="掌门"="老者" 自动识别合并 | NLP |
| BE-MAP-001 | 世界地图 | AI 地图生成 | "修仙世界/东方玄幻/5大洲" → 自动生成地图骨架 | LLM |
| BE-MAP-002 | 世界地图 | 多层级空间 | 天界/人间/冥界/秘境等层级 | 无 |
| BE-MAP-003 | 世界地图 | 势力分布图 | 组织架构树 + 势力关系网络 | 无 |
| BE-TIMELINE-001 | 时间线 | 多泳道视图 | 不同角色并行叙事线 | 无 |
| BE-TIMELINE-002 | 时间线 | AI 事件排列 | AI 从大纲提取关键事件自动排列 | LLM |
| BE-SETTING-001 | 设定集百科 | 五类实体 | 人物/地点/物品/组织/概念 | 无 |
| BE-SETTING-002 | 设定集百科 | AI 辅助生成 | AI 辅助生成设定条目 | LLM |
| BE-INS-001 | 灵感速记 | 语音输入 | 全局快捷键 Ctrl+Shift+N 呼起语音 | 无 |
| BE-ENHANCE-001 | AI 描写增强 | 感官细节补充 | 选中段落，AI 自动补充感官细节 | LLM |
| BE-ENHANCE-002 | AI 描写增强 | 网文风格增强 | 修仙/法术/战斗场景专属描写增强 | LLM |
| BE-EXPORT-001 | 设定集导出 | 富文本导出 | MD/Word/Excel/PDF 多格式 | 无 |

### 3.2 SHOULD（计划 Sprint 2）

| 需求ID | 模块 | 功能 | 验收标准 | 依赖 |
|--------|------|------|----------|------|
| FE-MAP-001 | 世界地图 | 程序化地形 | 程序化地形 + 人物轨迹动画 | MUST 功能 |
| FE-MAP-002 | 世界地图 | 手绘风格 | rough.js 手绘风格地图 | 无 |
| FE-OUTLINE-001 | 大纲规划 | AI 字数分配 | AI 按字数分配章节节奏 | 无 |
| BE-OUTLINE-001 | 大纲规划 | 章节节奏优化 | 10万/50万/100万字智能分配 | 无 |
| BE-WRITE-001 | 正文撰写 | RAG 续写 | 参考设定集进行 RAG 续写 | ChromaDB |

### 3.3 COULD（未来版本）

| 需求ID | 模块 | 功能 | 验收标准 | 依赖 |
|--------|------|------|----------|------|
| FE-PLUGIN-001 | 插件系统 | 第三方扩展 | 开放自定义 AI 指令模板 | MUST 功能 |
| FE-PLUGIN-002 | 插件系统 | 第三方画图集成 | 第三方画图工具集成 | 无 |
| FE-COLLAB-001 | 云端协作 | 工作室场景 | 多用户协作写作 | 无 |
| FE-COLLAB-002 | 云端协作 | 实时同步 | 协作写作实时同步 | 无 |

---

## 四、数据模型

### 4.1 SQLite 表结构

| 表名 | 说明 | 状态 |
|------|------|------|
| projects | 小说项目 | DONE |
| characters | 角色 | DONE |
| relationships | 角色关系 | DONE |
| locations | 地点 | DONE |
| factions | 势力组织 | TODO |
| timeline_events | 时间线事件 | TODO |
| world_settings | 世界观设定 | TODO |
| outline_nodes | 大纲节点 | DONE |
| chapters | 章节 | DONE |
| inspirations | 灵感碎片 | DONE |
| review_reports | 审查报告 | DONE |
| plugins | 插件 | DONE |

### 4.2 ChromaDB Collections

| Collection | 说明 | 状态 |
|------------|------|------|
| project_{id}_world_settings | 世界观设定向量检索 | TODO |
| project_{id}_chapters | 正文片段向量检索 | TODO |
| project_{id}_character_profiles | 角色特征向量 | TODO |

---

## 五、技术依赖

| 依赖 | 用途 | 状态 |
|------|------|------|
| Ollama (qwen3:8b) | 本地 LLM | 需配置 |
| DeepSeek/MiniMax API | 云端 LLM | 需配置 |
| Stable Diffusion | 本地绘图 | 需配置 |
| DALL-E/通义万相 | 云端绘图 | 需配置 |
| jieba | 中文 NLP 分词 | 需集成 |
| D3.js | 力导向图可视化 | DONE |
| react-force-graph-2d | 关系图谱 | 需集成 |
| rough.js | 手绘风格 | 需集成 |
| Leaflet | 地图 | 需集成 |

---

## 六、版本对照

| 版本 | 功能集 | 状态 |
|------|--------|------|
| v1.0 | 核心 MVP（书架/灵感/人物图谱/AI写作/审查） | 开发中 |
| v1.1 | 增强（大纲/时间线/势力分布/描写增强） | 规划中 |
| v1.2 | 完善（矛盾检测/OOC检测/插图/设定集百科） | 规划中 |
| v1.3 | 平台化（插件/同人/协作/仪表盘） | 规划中 |

---

## 七、优先级说明

- **MUST**：Sprint 1 必须完成，否则无法构成可用 MVP
- **SHOULD**：Sprint 2 计划，重要但不阻断核心流程
- **COULD**：未来版本，功能增强和平台化

---

## 八、备注

1. 当前前端已完成大部分 UI 组件，后端 API 骨架已搭建
2. 多项目隔离和 ChromaDB 向量检索是 RAG 续写的前置依赖
3. AI 描写增强需要等待 LLM 服务配置完成
4. 世界地图编辑器需要 D3.js 力导向图完成后才能集成
