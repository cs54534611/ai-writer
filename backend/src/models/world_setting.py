"""WorldSetting 模型 - 世界设定"""

import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class SettingCategory(str, Enum):
    """设定类别"""
    CHARACTER = "character"    # 人物
    LOCATION = "location"      # 地点
    ITEM = "item"              # 物品
    ORGANIZATION = "organization"  # 组织
    CONCEPT = "concept"        # 概念


class WorldSettingBase(SQLModel):
    """世界设定基础字段"""
    category: SettingCategory = Field(description="设定类别")
    name: str = Field(max_length=255, description="设定名称")
    content: Optional[str] = Field(default=None, description="设定内容")


class WorldSetting(WorldSettingBase, table=True):
    """世界设定数据库模型"""
    __tablename__ = "world_settings"

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
    embedding: Optional[str] = Field(default=None, description="向量嵌入(JSON)")
    related_setting_ids: Optional[str] = Field(
        default=None,
        description="关联设定ID列表(JSON)"
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

    def get_related_setting_ids(self) -> list[str]:
        """获取关联设定ID列表"""
        if not self.related_setting_ids:
            return []
        try:
            return json.loads(self.related_setting_ids)
        except json.JSONDecodeError:
            return []

    def set_related_setting_ids(self, ids: list[str]) -> None:
        """设置关联设定ID列表"""
        self.related_setting_ids = json.dumps(ids)
