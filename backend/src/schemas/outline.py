"""OutlineNode 请求/响应 Schema"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.models.outline import LineType, NarrativePOV


class OutlineNodeCreate(BaseModel):
    """创建大纲节点请求"""
    parent_id: Optional[str] = Field(default=None, max_length=36, description="父节点ID")
    title: str = Field(min_length=1, max_length=500, description="节点标题")
    summary: Optional[str] = Field(default=None, description="节点摘要/简介")
    word_target: int = Field(default=0, ge=0, description="目标字数")
    narrative_pov: Optional[NarrativePOV] = Field(default=None, description="叙事视角")
    sort_order: int = Field(default=0, description="排序顺序")
    line_type: LineType = Field(default=LineType.MAIN, description="线类型")


class OutlineNodeUpdate(BaseModel):
    """更新大纲节点请求"""
    parent_id: Optional[str] = Field(default=None, max_length=36, description="父节点ID")
    title: Optional[str] = Field(default=None, min_length=1, max_length=500, description="节点标题")
    summary: Optional[str] = Field(default=None, description="节点摘要/简介")
    word_target: Optional[int] = Field(default=None, ge=0, description="目标字数")
    narrative_pov: Optional[NarrativePOV] = Field(default=None, description="叙事视角")
    sort_order: Optional[int] = Field(default=None, description="排序顺序")
    line_type: Optional[LineType] = Field(default=None, description="线类型")


class OutlineNodeRead(BaseModel):
    """大纲节点响应"""
    id: str
    project_id: str
    parent_id: Optional[str] = None
    title: str
    summary: Optional[str] = None
    word_target: int = 0
    narrative_pov: Optional[NarrativePOV] = None
    sort_order: int = 0
    line_type: LineType = LineType.MAIN
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OutlineNodeTree(OutlineNodeRead):
    """大纲节点树形响应（包含子节点）"""
    children: list["OutlineNodeTree"] = Field(default_factory=list)


# 前向引用需要重新定义以支持递归
OutlineNodeTree.model_rebuild()
