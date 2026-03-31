"""TimelineEvent 模型 - 时间线事件"""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class TimelineEventBase(SQLModel):
    """时间线事件基础字段"""
    title: str = Field(max_length=255, description="事件标题")
    description: Optional[str] = Field(default=None, description="事件描述")
    time_point: str = Field(max_length=100, description="时间点描述，如「第1年3月」")
    character_ids: Optional[str] = Field(default=None, description="关联角色ID，JSON数组格式")
    location_id: Optional[str] = Field(default=None, max_length=36, description="关联地点ID")
    event_type: str = Field(default="主线", max_length=50, description="事件类型：主线/支线/暗线")
    sort_order: int = Field(default=0, description="排序顺序")


class TimelineEvent(TimelineEventBase, table=True):
    """时间线事件数据库模型"""
    __tablename__ = "timeline_events"

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
