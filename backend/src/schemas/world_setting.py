"""WorldSetting 请求/响应 Schema"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.models.world_setting import SettingCategory


class WorldSettingCreate(BaseModel):
    """创建设定请求"""
    category: SettingCategory = Field(description="设定类别")
    name: str = Field(min_length=1, max_length=255, description="设定名称")
    content: Optional[str] = Field(default=None, description="设定内容")


class WorldSettingUpdate(BaseModel):
    """更新设定请求"""
    category: Optional[SettingCategory] = Field(default=None, description="设定类别")
    name: Optional[str] = Field(default=None, min_length=1, max_length=255, description="设定名称")
    content: Optional[str] = Field(default=None, description="设定内容")


class WorldSettingRead(BaseModel):
    """设定响应"""
    id: str
    project_id: str
    category: SettingCategory
    name: str
    content: Optional[str] = None
    related_setting_ids: Optional[list[str]] = Field(default=None, description="关联设定ID列表")
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_with_relations(cls, model) -> "WorldSettingRead":
        """从ORM模型转换，处理related_setting_ids JSON"""
        data = {
            "id": model.id,
            "project_id": model.project_id,
            "category": model.category,
            "name": model.name,
            "content": model.content,
            "related_setting_ids": model.get_related_setting_ids(),
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        }
        return cls(**data)
