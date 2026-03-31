"""Location 请求/响应 Schema"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.models.location import SpatialLayer, TerrainType


class LocationCreate(BaseModel):
    """创建地点请求"""
    name: str = Field(min_length=1, max_length=255, description="地点名称")
    parent_id: Optional[str] = Field(default=None, max_length=36, description="父级地点ID")
    layer: SpatialLayer = Field(default=SpatialLayer.MATERIAL, description="空间层级")
    position_x: float = Field(default=0.0, description="X坐标")
    position_y: float = Field(default=0.0, description="Y坐标")
    position_z: float = Field(default=0.0, description="Z坐标")
    terrain: Optional[TerrainType] = Field(default=None, description="地形类型")
    description: Optional[str] = Field(default=None, description="地点描述")


class LocationUpdate(BaseModel):
    """更新地点请求"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255, description="地点名称")
    parent_id: Optional[str] = Field(default=None, max_length=36, description="父级地点ID")
    layer: Optional[SpatialLayer] = Field(default=None, description="空间层级")
    position_x: Optional[float] = Field(default=None, description="X坐标")
    position_y: Optional[float] = Field(default=None, description="Y坐标")
    position_z: Optional[float] = Field(default=None, description="Z坐标")
    terrain: Optional[TerrainType] = Field(default=None, description="地形类型")
    description: Optional[str] = Field(default=None, description="地点描述")


class LocationRead(BaseModel):
    """地点响应"""
    id: str
    project_id: str
    name: str
    parent_id: Optional[str] = None
    layer: SpatialLayer = SpatialLayer.MATERIAL
    position_x: float = 0.0
    position_y: float = 0.0
    position_z: float = 0.0
    terrain: Optional[TerrainType] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LocationMapResponse(BaseModel):
    """地点地图响应（用于前端渲染）"""
    locations: list[LocationRead]
    layers: list[str] = Field(
        default_factory=lambda: [
            "celestial", "material", "underworld", "realm", "void"
        ],
        description="空间层级列表"
    )
