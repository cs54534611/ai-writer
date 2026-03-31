# AI Writer - 需求规格说明书

> 版本：v2.0 | 日期：2026-03-31 | 状态：持续更新

---

## 一、项目概述

**AI Writer** 是一款面向中文网络小说作者的 AI 创作辅助平台，核心差异是将 AI-Reader 的"小说世界观提取"能力反过来——从"阅读分析已有小说"变为"创作阶段构建世界观"。

**目标用户**：新人网文作者、业余创作者、资深老手、工作室写手、同人文作者

**技术栈**：
- 前端：React 19 + TypeScript + Vite + Tailwind CSS + TanStack Query + Recharts
- 后端：Python + FastAPI（async）+ SQLModel + aiosqlite
- 数据库：SQLite（per-project）+ ChromaDB（向量检索/RAG）
- LLM：Ollama（本地）+ DeepSeek/MiniMax API（云端）
- AI 绘图：Stable Diffusion（本地）+ DALL-E（云端）

---

## 二、已完成功能

### 书架管理
| 需求ID | 功能 | 验收标准 | 状态 |
|--------|------|----------|------|
| FE-PROJ-001 | 多项目创建/编辑/删除 | 可创建项目并保存到 SQLite | DONE |
| FE-PROJ-002 | 项目列表分页查询 | 支持分页、状态过滤 | DONE |
| FE-PROJ-003 | 项目复制/归档 | 项目可复制和标记状态 | DONE |

### 人物关系图谱
| 需求ID | 功能 | 验收标准 | 状态 |
|--------|------|----------|------|
| FE-CHAR-001 | 角色卡 CRUD | 角色姓名/性别/性格/背景/弧光 | DONE |
| FE-CHAR-002 | 角色关系管理 | 创建/编辑/删除角色间关系 | DONE |
| FE-CHAR-003 | 力导向图可视化 | D3.js 实现，支持拖拽/缩放/过滤 | DONE |
| BE-CHAR-001 | AI 关系建议 | 输入两个角色背景，AI 建议关系走向 | DONE |
| BE-CHAR-002 | 别名自动合并 | "师父"="掌门"="老者" 自动识别合并 | TODO |

### 灵感速记
| 需求ID | 功能 | 验收标准 | 状态 |
|--------|------|----------|------|
| FE-INS-001 | 灵感碎片记录 | 文字灵感快速记录 | DONE |
| FE-INS-002 | AI 自动标签分类 | AI 为灵感打标签（人物/场景/情节等） | DONE |
| FE-INS-003 | 一键升格 | 灵感可升格为角色卡或大纲条目 | DONE |
| BE-INS-001 | 语音输入 | 全局快捷键 Ctrl+Shift+N 呼起语音 | DONE |

### 正文撰写
| 需求ID | 功能 | 验收标准 | 状态 |
|--------|------|----------|------|
| FE-WRITE-001 | 智能编辑器 | 沉浸式全屏写作模式 | DONE |
| FE-WRITE-002 | 自动保存 | 每30秒自动保存 | DONE |
| FE-WRITE-003 | 字数统计 | 章节/卷/全书实时统计 | DONE |
| FE-WRITE-004 | AI 续写 | 基于上下文和设定的智能续写 | DONE |
| FE-WRITE-005 | AI 多版本候选 | 一次生成2-3个不同走向 | DONE |
| FE-WRITE-006 | AI 改写 | 润色/替代表达/口味调整 | DONE |
| FE-WRITE-007 | 对话式写作 | 与 AI 进行角色扮演对话推进剧情 | DONE |
| BE-WRITE-001 | RAG 上下文感知续写 | ChromaDB 向量检索 + 设定集上下文 | DONE |
| BE-WRITE-002 | 风格控制 | 模仿作者文风/对话稠密/描写稠密 | TODO |

### AI 即时反馈
| 需求ID | 功能 | 验收标准 | 状态 |
|--------|------|----------|------|
| FE-FEEDBACK-001 | 选中章节 AI 反馈 | AI 给出"三个可改进方向" | DONE |
| FE-FEEDBACK-002 | 多维度反馈 | 节奏/角色/情节/文笔可选 | DONE |

### AI 描写增强
| 需求ID | 功能 | 验收标准 | 状态 |
|--------|------|----------|------|
| BE-ENHANCE-001 | 感官细节补充 | 选中段落，AI 自动补充感官细节 | TODO |
| BE-ENHANCE-002 | 网文风格增强 | 修仙/法术/战斗场景专属描写增强 | TODO |

### 阅读审查
| 需求ID | 功能 | 验收标准 | 状态 |
|--------|------|----------|------|
| FE-REVIEW-001 | 前后矛盾检测 | 人物特征/关系状态/时间线矛盾检测 | DONE |
| FE-REVIEW-002 | 角色 OOC 检测 | AI 对照角色设定检测言行出戏 | DONE |
| FE-REVIEW-003 | 敏感词检测 | 内置敏感词库 + 自定义敏感词分级 | DONE |

### 世界观与设定
| 需求ID | 功能 | 验收标准 | 状态 |
|--------|------|----------|------|
| BE-SETTING-001 | 五类实体设定 | 人物/地点/物品/组织/概念 | DONE |
| BE-SETTING-002 | AI 辅助生成设定 | AI 辅助生成设定条目 | TODO |
| BE-EXPORT-001 | 设定集导出 | MD/JSON 多格式导出 | DONE |

### 世界地图
| 需求ID | 功能 | 验收标准 | 状态 |
|--------|------|----------|------|
| FE-LOC-001 | 层级地点管理 | 天界/人间/冥界/秘境等多层级 | DONE |
| FE-FACTION-001 | 势力分布图 | 组织架构树 + 势力关系网络 | DONE |
| BE-MAP-001 | AI 地图生成 | 关键词生成地图骨架 | TODO |
| FE-MAP-001 | 程序化地形 | 程序化地形 + 人物轨迹动画 | TODO |
| FE-MAP-002 | 手绘风格地图 | rough.js 手绘风格地图 | TODO |

### 时间线
| 需求ID | 功能 | 验收标准 | 状态 |
|--------|------|----------|------|
| BE-TIMELINE-001 | 多泳道视图 | 不同角色并行叙事线 | DONE |
| BE-TIMELINE-002 | AI 事件排列 | AI 从大纲提取关键事件自动排列 | TODO |

### 大纲规划
| 需求ID | 功能 | 验收标准 | 状态 |
|--------|------|----------|------|
| FE-OUTLINE-001 | 树形大纲 | 卷→章→节→场景 树形结构 | DONE |
| FE-OUTLINE-002 | AI 大纲生成 | 按题材生成大纲模板 | DONE |
| FE-OUTLINE-003 | 伏笔管理 | 记录埋下的伏笔，合适时提醒回收 | DONE |
| FE-OUTLINE-004 | 主线/支线/暗线分类 | 分类标记不同叙事线 | DONE |
| BE-OUTLINE-001 | AI 字数分配 | 10万/50万/100万字智能分配 | TODO |

### 导入导出
| 需求ID | 功能 | 验收标准 | 状态 |
|--------|------|----------|------|
| FE-EXPORT-001 | .aiwriter 格式导入/导出 | 全量备份和恢复 | DONE |
| FE-EXPORT-002 | TXT/MD 导入 | 拖拽上传，智能章节切分 | DONE |
| FE-EXPORT-003 | 多格式导出 | MD/TXT/JSON 导出 | DONE |

### 同人创作
| 需求ID | 功能 | 验收标准 | 状态 |
|--------|------|----------|------|
| FE-FANDOM-001 | IP 设定导入 | 手动输入或 AI 分析原著文本提取 | DONE |
| FE-FANDOM-002 | 同人设定追踪 | 自动追踪同人设定与原著差异 | DONE |

### AI 插图生成
| 需求ID | 功能 | 验收标准 | 状态 |
|--------|------|----------|------|
| FE-IMAGE-001 | 角色/场景配图 | 根据设定生成配图 | DONE |
| FE-IMAGE-002 | 多风格支持 | 写实/动漫/水墨古风 | DONE |

### 插件系统
| 需求ID | 功能 | 验收标准 | 状态 |
|--------|------|----------|------|
| FE-PLUGIN-001 | 插件架构 | CSP 沙箱隔离的插件机制 | DONE |
| FE-PLUGIN-002 | 内置插件 | 日志备份插件、字数目标插件 | DONE |
| FE-PLUGIN-003 | hello_world 示例 | 插件开发示例 | DONE |

### 创作旅程仪表盘
| 需求ID | 功能 | 验收标准 | 状态 |
|--------|------|----------|------|
| FE-JOURNEY-001 | 进度仪表盘 | 可视化创作进度 | DONE |
| FE-JOURNEY-002 | AI 建议 | AI 给出下一步建议 | DONE |
| FE-JOURNEY-003 | 目标进度对比 | 目标字数 vs 实际进度 | DONE |
| FE-JOURNEY-004 | 写作趋势图表 | 近7天写作字数柱状图 | DONE |

---

## 三、数据模型

### SQLite 表
| 表名 | 说明 | 状态 |
|------|------|------|
| projects | 小说项目 | DONE |
| characters | 角色 | DONE |
| relationships | 角色关系 | DONE |
| locations | 地点 | DONE |
| factions | 势力组织 | DONE |
| timeline_events | 时间线事件 | DONE |
| world_settings | 世界观设定 | DONE |
| outline_nodes | 大纲节点 | DONE |
| chapters | 章节 | DONE |
| inspirations | 灵感碎片 | DONE |
| review_reports | 审查报告 | DONE |
| sensitive_words | 敏感词库 | DONE |
| foreshadowings | 伏笔 | DONE |
| plugins | 插件 | DONE |

### ChromaDB Collections
| Collection | 说明 | 状态 |
|------------|------|------|
| project_{id}_world_settings | 世界观设定向量检索 | DONE |
| project_{id}_chapters | 正文片段向量检索（RAG） | DONE |
| project_{id}_character_profiles | 角色特征向量 | TODO |

---

## 四、技术依赖

| 依赖 | 用途 | 状态 |
|------|------|------|
| Ollama (qwen3:8b) | 本地 LLM | 需配置 |
| DeepSeek/MiniMax API | 云端 LLM | 需配置 |
| Stable Diffusion | 本地绘图 | 需配置 |
| DALL-E/通义万相 | 云端绘图 | 需配置 |
| jieba | 中文 NLP 分词 | 需集成 |
| D3.js | 力导向图可视化 | DONE |
| react-force-graph-2d | 关系图谱 | DONE |
| rough.js | 手绘风格 | 需集成 |
| Leaflet | 地图 | 需集成 |
| recharts | 仪表盘图表 | DONE |

---

## 五、版本对照

| 版本 | 功能集 | 状态 |
|------|--------|------|
| v1.0 | 核心 MVP（书架/灵感/人物图谱/AI写作/审查） | DONE |
| v1.1 | 增强（大纲/时间线/势力分布/描写增强） | 开发中 |
| v1.2 | 完善（ChromaDB RAG/AI地图/事件排列） | 规划中 |
| v1.3 | 平台化（插件市场/云端协作） | 规划中 |

---

## 六、待完成功能汇总

### 高优先级（v1.1）
- AI 描写增强（感官细节/网文风格）
- AI 从大纲自动排列时间线事件
- AI 字数分配章节节奏优化
- AI 地图生成（关键词生成地图骨架）

### 中优先级（v1.2）
- ChromaDB 角色特征向量收集
- 角色别名自动合并（jieba NLP）
- rough.js 手绘风格地图
- 程序化地形 + 人物轨迹动画

### 低优先级（v1.3+）
- 插件市场 / 第三方 AI 指令模板
- 云端协作 / 多用户实时同步
- Word/Excel/PDF 导出

---

## 七、已完成的 Agent 迭代记录

| Sprint | Agent | 主要产出 |
|--------|-------|----------|
| Sprint 1 | Requirements | 生成 SPEC.md 需求规格 |
| Sprint 1 | Development | 敏感词系统、伏笔管理、TXT 智能切章 |
| Sprint 1 | Testing | 前端 hooks 测试 |
| Sprint 1 | Quality | 代码风格统一 |
| Sprint 2 | ChromaDB Agent | ChromaDBManager、章节向量化、RAG 续写 |
| Sprint 2 | Timeline Agent | Faction/TimelineEvent、多泳道视图、LocationsPage |
| Sprint 2 | Experience Agent | 语音输入、AI关系建议、多格式导出 |
