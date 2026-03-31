"""Location 模型 - 世界地图地点"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class TerrainType(str, Enum):
    """地形类型"""
    PLAINS = "plains"              # 平原
    MOUNTAIN = "mountain"           # 山脉
    FOREST = "forest"              # 森林
    DESERT = "desert"              # 沙漠
    OCEAN = "ocean"                # 海洋
    RIVER = "river"                # 河流/湖泊
    CITY = "city"                  # 城市
    VILLAGE = "village"            # 村庄
    RUINS = "ruins"                # 遗迹
    SWAMP = "swamp"                # 沼泽
    SNOW = "snow"                  # 雪原
    VOLCANO = "volcano"            # 火山
    CAVE = "cave"                  # 洞穴
    SKY = "sky"                    # 天空
    ABYSS = "abyss"                # 深渊


class SpatialLayer(str, Enum):
    """空间层级（用于世界地图）"""
    CELESTIAL = "celestial"         # 天界/神界
    MATERIAL = "material"           # 人界/物质界
    UNDERWORLD = "underworld"       # 冥界/地狱
    REALM = "realm"                 # 秘境/异空间
    VOID = "void"                   # 虚空


class LocationBase(SQLModel):
    """地点基础字段"""
    name: str = Field(max_length=255, description="地点名称")
    parent_id: Optional[str] = Field(default=None, max_length=36, description="父级地点ID")
    layer: SpatialLayer = Field(default=SpatialLayer.MATERIAL, description="空间层级")
    position_x: float = Field(default=0.0, description="X坐标")
    position_y: float = Field(default=0.0, description="Y坐标")
    position_z: float = Field(default=0.0, description="Z坐标（层级高度）")
    terrain: Optional[TerrainType] = Field(default=None, description="地形类型")
    description: Optional[str] = Field(default=None, description="地点描述")


class Location(LocationBase, table=True):
    """地点数据库模型"""
    __tablename__ = "locations"

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

    class Config:
        use_enum_values = True
