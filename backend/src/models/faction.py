"""Faction 模型 - 势力/组织"""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class FactionBase(SQLModel):
    """势力基础字段"""
    name: str = Field(max_length=255, description="势力名称")
    parent_id: Optional[str] = Field(default=None, max_length=36, description="上级势力ID")
    color: str = Field(default="#6366f1", max_length=20, description="地图显示颜色")
    description: Optional[str] = Field(default=None, description="势力描述")


class Faction(FactionBase, table=True):
    """势力数据库模型"""
    __tablename__ = "factions"

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
