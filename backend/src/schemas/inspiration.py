"""Inspiration 请求/响应 Schema"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class InspirationCreate(BaseModel):
    """创建灵感请求"""
    content: str = Field(min_length=1, description="灵感内容")
    tags: Optional[str] = Field(default=None, description="标签，JSON数组格式")
    related_setting_ids: Optional[str] = Field(
        default=None,
        description="关联设定ID列表，JSON数组格式"
    )


class InspirationUpdate(BaseModel):
    """更新灵感请求"""
    content: Optional[str] = Field(default=None, min_length=1, description="灵感内容")
    tags: Optional[str] = Field(default=None, description="标签，JSON数组格式")
    related_setting_ids: Optional[str] = Field(
        default=None,
        description="关联设定ID列表，JSON数组格式"
    )


class InspirationRead(BaseModel):
    """灵感响应"""
    id: str
    project_id: str
    content: str
    tags: Optional[str] = None
    related_setting_ids: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class InspirationListResponse(BaseModel):
    """灵感列表响应"""
    items: list[InspirationRead]
    total: int
    page: int = 1
    page_size: int = 20
