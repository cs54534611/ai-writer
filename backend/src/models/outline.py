"""OutlineNode 模型 - 大纲节点"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class LineType(str, Enum):
    """大纲线类型"""
    MAIN = "main"          # 主线
    BRANCH = "branch"      # 支线
    SUBPLOT = "subplot"    # 副线


class NarrativePOV(str, Enum):
    """叙事视角"""
    FIRST = "first"            # 第一人称
    THIRD = "third"            # 第三人称
    THIRD_LIMITED = "third_limited"   # 第三人称限制视角
    THIRD_OMNISCIENT = "third_omniscient"  # 第三人称全知视角


class OutlineNodeBase(SQLModel):
    """大纲节点基础字段"""
    parent_id: Optional[str] = Field(default=None, max_length=36, description="父节点ID")
    title: str = Field(max_length=500, description="节点标题")
    summary: Optional[str] = Field(default=None, description="节点摘要/简介")
    word_target: int = Field(default=0, ge=0, description="目标字数")
    narrative_pov: Optional[NarrativePOV] = Field(default=None, description="叙事视角")
    sort_order: int = Field(default=0, description="排序顺序")
    line_type: LineType = Field(default=LineType.MAIN, description="线类型")


class OutlineNode(OutlineNodeBase, table=True):
    """大纲节点数据库模型"""
    __tablename__ = "outline_nodes"

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
