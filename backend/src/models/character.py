"""Character 模型 - 小说角色"""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class CharacterBase(SQLModel):
    """角色基础字段"""
    name: str = Field(max_length=255, description="角色名称")
    aliases: Optional[str] = Field(default=None, description="角色别名，JSON数组格式")
    gender: Optional[str] = Field(default=None, max_length=50, description="性别")
    age: Optional[str] = Field(default=None, max_length=50, description="年龄")
    personality: Optional[str] = Field(default=None, description="性格特点")
    background: Optional[str] = Field(default=None, description="角色背景")
    arc: Optional[str] = Field(default=None, description="人物弧光")
    avatar_url: Optional[str] = Field(default=None, max_length=500, description="角色头像URL")


class Character(CharacterBase, table=True):
    """角色数据库模型"""
    __tablename__ = "characters"

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
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="更新时间",
    )
