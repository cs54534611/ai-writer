"""Character 请求/响应 Schema"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CharacterCreate(BaseModel):
    """创建角色请求"""
    name: str = Field(min_length=1, max_length=255, description="角色名称")
    aliases: Optional[str] = Field(default=None, description="角色别名，JSON数组格式")
    gender: Optional[str] = Field(default=None, max_length=50, description="性别")
    age: Optional[str] = Field(default=None, max_length=50, description="年龄")
    personality: Optional[str] = Field(default=None, description="性格特点")
    background: Optional[str] = Field(default=None, description="角色背景")
    arc: Optional[str] = Field(default=None, description="人物弧光")
    avatar_url: Optional[str] = Field(default=None, max_length=500, description="角色头像URL")


class CharacterUpdate(BaseModel):
    """更新角色请求"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255, description="角色名称")
    aliases: Optional[str] = Field(default=None, description="角色别名，JSON数组格式")
    gender: Optional[str] = Field(default=None, max_length=50, description="性别")
    age: Optional[str] = Field(default=None, max_length=50, description="年龄")
    personality: Optional[str] = Field(default=None, description="性格特点")
    background: Optional[str] = Field(default=None, description="角色背景")
    arc: Optional[str] = Field(default=None, description="人物弧光")
    avatar_url: Optional[str] = Field(default=None, max_length=500, description="角色头像URL")


class CharacterRead(BaseModel):
    """角色响应"""
    id: str
    project_id: str
    name: str
    aliases: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[str] = None
    personality: Optional[str] = None
    background: Optional[str] = None
    arc: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CharacterListResponse(BaseModel):
    """角色列表响应"""
    items: list[CharacterRead]
    total: int
    page: int = 1
    page_size: int = 20
