"""Project 模型 - 小说项目"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class ProjectStatus(str, Enum):
    """项目状态"""
    ACTIVE = "active"          # 活跃创作中
    ARCHIVED = "archived"      # 已归档
    DRAFT = "draft"            # 草稿


class ProjectBase(SQLModel):
    """项目基础字段"""
    name: str = Field(max_length=255, description="项目名称")
    description: Optional[str] = Field(default=None, description="项目描述")
    genre: Optional[str] = Field(default=None, max_length=100, description="题材类型")
    total_words_target: int = Field(default=0, ge=0, description="目标总字数")
    status: ProjectStatus = Field(default=ProjectStatus.DRAFT, description="项目状态")


class Project(ProjectBase, table=True):
    """项目数据库模型"""
    __tablename__ = "projects"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        max_length=36,
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
