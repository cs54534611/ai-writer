"""伏笔模型 - 伏笔追踪管理"""

import uuid
from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel


class ForeshadowingStatus(str, Enum):
    """伏笔状态"""
    PLANTED = "planted"     # 已埋下
    RESOLVED = "resolved"   # 已回收
    EXPIRED = "expired"     # 已失效


class ForeshadowingBase(SQLModel):
    """伏笔基础字段"""
    chapter_id: str = Field(
        max_length=36,
        description="埋下伏笔的章节ID",
    )
    description: str = Field(
        max_length=1000,
        description="伏笔内容描述",
    )
    status: ForeshadowingStatus = Field(
        default=ForeshadowingStatus.PLANTED,
        description="伏笔状态",
    )
    notes: str | None = Field(
        default=None,
        max_length=2000,
        description="备注信息",
    )


class Foreshadowing(ForeshadowingBase, table=True):
    """伏笔数据库模型"""
    __tablename__ = "foreshadowings"

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
    planted_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="埋下时间",
    )
    resolved_at: datetime | None = Field(
        default=None,
        description="回收时间",
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
