"""Inspiration 模型 - 灵感速记"""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class InspirationBase(SQLModel):
    """灵感基础字段"""
    content: str = Field(description="灵感内容")
    tags: Optional[str] = Field(default=None, description="标签，JSON数组格式")
    related_setting_ids: Optional[str] = Field(
        default=None,
        description="关联设定ID列表，JSON数组格式"
    )


class Inspiration(InspirationBase, table=True):
    """灵感速记数据库模型"""
    __tablename__ = "inspirations"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        max_length=36,
    )
    project_id: str = Field(
        max_length=36,
        description="所属项目ID",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="创建时间",
    )
