"""Project 请求/响应 Schema"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.models.project import ProjectStatus


class ProjectCreate(BaseModel):
    """创建项目请求"""
    name: str = Field(min_length=1, max_length=255, description="项目名称")
    description: Optional[str] = Field(default=None, description="项目描述")
    genre: Optional[str] = Field(default=None, max_length=100, description="题材类型")
    total_words_target: int = Field(default=0, ge=0, description="目标总字数")


class ProjectUpdate(BaseModel):
    """更新项目请求"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255, description="项目名称")
    description: Optional[str] = Field(default=None, description="项目描述")
    genre: Optional[str] = Field(default=None, max_length=100, description="题材类型")
    total_words_target: Optional[int] = Field(default=None, ge=0, description="目标总字数")
    status: Optional[ProjectStatus] = Field(default=None, description="项目状态")


class ProjectRead(BaseModel):
    """项目响应"""
    id: str
    name: str
    description: Optional[str] = None
    genre: Optional[str] = None
    total_words_target: int = 0
    status: ProjectStatus = ProjectStatus.DRAFT
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    """项目列表响应"""
    items: list[ProjectRead]
    total: int
    page: int = 1
    page_size: int = 20
