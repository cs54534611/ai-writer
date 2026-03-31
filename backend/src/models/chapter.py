"""Chapter 模型 - 正文章节"""

import uuid
from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel


class ChapterStatus(str, Enum):
    """章节状态"""
    WRITING = "writing"      # 创作中
    COMPLETED = "completed" # 已完成
    REVIEWED = "reviewed"   # 已审核


class ChapterBase(SQLModel):
    """章节基础字段"""
    outline_id: str | None = Field(
        default=None,
        max_length=36,
        description="关联的大纲节点ID",
    )
    title: str = Field(
        max_length=500,
        description="章节标题",
    )
    content: str = Field(
        default="",
        description="章节正文内容",
    )
    word_count: int = Field(
        default=0,
        ge=0,
        description="章节字数",
    )
    status: ChapterStatus = Field(
        default=ChapterStatus.WRITING,
        description="章节状态",
    )
    sort_order: int = Field(
        default=0,
        description="排序顺序",
    )


class Chapter(ChapterBase, table=True):
    """章节数据库模型"""
    __tablename__ = "chapters"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        max_length=36,
    )
    project_id: str = Field(
        max_length=36,
        index=True,
        description="项目ID",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="创建时间",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="更新时间",
    )

    class Config:
        use_enum_values = True
