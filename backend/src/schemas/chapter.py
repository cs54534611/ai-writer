"""Chapter 请求/响应 Schema"""

from datetime import datetime

from pydantic import BaseModel, Field

from src.models.chapter import ChapterStatus


class ChapterCreate(BaseModel):
    """创建章节请求"""
    outline_id: str | None = Field(
        default=None,
        max_length=36,
        description="关联的大纲节点ID",
    )
    title: str = Field(
        min_length=1,
        max_length=500,
        description="章节标题",
    )
    content: str = Field(
        default="",
        description="章节正文内容",
    )
    sort_order: int = Field(
        default=0,
        description="排序顺序",
    )


class ChapterUpdate(BaseModel):
    """更新章节请求"""
    outline_id: str | None = Field(
        default=None,
        max_length=36,
        description="关联的大纲节点ID",
    )
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
        description="章节标题",
    )
    content: str | None = Field(
        default=None,
        description="章节正文内容",
    )
    status: ChapterStatus | None = Field(
        default=None,
        description="章节状态",
    )
    sort_order: int | None = Field(
        default=None,
        description="排序顺序",
    )


class ChapterRead(BaseModel):
    """章节响应"""
    id: str
    project_id: str
    outline_id: str | None = None
    title: str
    content: str = ""
    word_count: int = 0
    status: ChapterStatus = ChapterStatus.WRITING
    sort_order: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChapterListResponse(BaseModel):
    """章节列表响应"""
    items: list[ChapterRead]
    total: int
    page: int = 1
    page_size: int = 20


class WritingContinueRequest(BaseModel):
    """续写请求"""
    context: str = Field(
        description="前文内容（用于续写的上下文）",
    )
    style: str = Field(
        default="default",
        description="续写风格：default/dialog_heavy/desc_heavy/fastpaced/slowpaced",
    )
    num_versions: int = Field(
        default=1,
        ge=1,
        le=3,
        description="生成版本数量（1-3）",
    )


class WritingExpandRequest(BaseModel):
    """扩写请求"""
    paragraph: str = Field(
        description="要扩写的段落",
    )
    expand_ratio: float = Field(
        default=2.0,
        gt=1.0,
        le=5.0,
        description="扩写倍数（1.0-5.0）",
    )


class WritingRewriteRequest(BaseModel):
    """改写请求"""
    content: str = Field(
        description="要改写的内容",
    )
    mode: str = Field(
        default="polish",
        description="改写模式：polish/alternative/tone",
    )
    tone: str | None = Field(
        default=None,
        description="当 mode=tone 时，指定目标语调",
    )


class WritingEnhanceRequest(BaseModel):
    """描写增强请求"""
    content: str = Field(
        description="要增强描写的内容",
    )
    senses: list[str] | None = Field(
        default=None,
        description="要增强的感官：visual/auditory/olfactory/tactile/smell/taste",
    )


class WritingFeedbackRequest(BaseModel):
    """即时反馈请求"""
    content: str = Field(
        description="要反馈的内容",
    )
    focus_areas: list[str] | None = Field(
        default=None,
        description="反馈重点：pacing/character/plot/writing",
    )


class WritingFeedbackResponse(BaseModel):
    """即时反馈响应"""
    score: int = Field(description="综合评分（1-10）")
    strengths: list[str] = Field(description="优点列表")
    issues: list[str] = Field(description="问题列表")
    suggestions: list[str] = Field(description="建议列表")


class DialogueWriteRequest(BaseModel):
    """对话式写作请求"""
    characters: list[dict] = Field(
        description="角色设定列表，每个包含 name, personality, background 等",
    )
    scene: str = Field(
        description="场景描述",
    )
    last_dialogue: str = Field(
        description="最后一句对话（AI 从这里继续）",
    )
