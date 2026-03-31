"""TimelineEvent API 路由 - 时间线事件管理"""

from datetime import datetime
from typing import Annotated, AsyncGenerator, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import get_db_manager
from src.models.timeline_event import TimelineEvent
from src.services.llm import get_llm_service
from src.services.timeline_generator import TimelineGenerator

router = APIRouter()


async def get_project_db(
    project_id: Annotated[str, Path(description="项目ID")]
) -> AsyncGenerator[AsyncSession, None]:
    """获取项目数据库会话的依赖"""
    db_manager = get_db_manager()
    if project_id not in db_manager._engines:
        await db_manager.init_project_db(project_id)
    
    engine = db_manager._engines[project_id]
    session = AsyncSession(engine, expire_on_commit=False)
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


class TimelineEventCreate(SQLModel):
    title: str
    description: str | None = None
    time_point: str
    character_ids: str | None = None
    location_id: str | None = None
    event_type: str = "主线"
    sort_order: int = 0


class TimelineEventUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    time_point: str | None = None
    character_ids: str | None = None
    location_id: str | None = None
    event_type: str | None = None
    sort_order: int | None = None


class TimelineEventRead(SQLModel):
    id: str
    project_id: str
    title: str
    description: str | None
    time_point: str
    character_ids: str | None
    location_id: str | None
    event_type: str
    sort_order: int
    created_at: datetime


@router.post("/", response_model=TimelineEventRead, status_code=status.HTTP_201_CREATED)
async def create_timeline_event(
    project_id: Annotated[str, Path(description="项目ID")],
    event_data: TimelineEventCreate,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> TimelineEvent:
    """创建时间线事件"""
    event = TimelineEvent(
        project_id=project_id,
        **event_data.model_dump()
    )
    db.add(event)
    await db.flush()
    await db.refresh(event)
    return event


@router.get("/", response_model=list[TimelineEventRead])
async def list_timeline_events(
    project_id: Annotated[str, Path(description="项目ID")],
    db: Annotated[AsyncSession, Depends(get_project_db)],
    event_type: Optional[str] = Query(default=None, description="按事件类型筛选：主线/支线/暗线"),
) -> list[TimelineEvent]:
    """获取时间线事件列表"""
    query = select(TimelineEvent).where(TimelineEvent.project_id == project_id)
    
    if event_type:
        query = query.where(TimelineEvent.event_type == event_type)
    
    query = query.order_by(TimelineEvent.sort_order, TimelineEvent.time_point)
    result = await db.execute(query)
    events = result.scalars().all()
    return list(events)


@router.get("/{event_id}", response_model=TimelineEventRead)
async def get_timeline_event(
    project_id: Annotated[str, Path(description="项目ID")],
    event_id: Annotated[str, Path(description="事件ID")],
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> TimelineEvent:
    """获取单个时间线事件"""
    result = await db.execute(
        select(TimelineEvent).where(
            TimelineEvent.id == event_id,
            TimelineEvent.project_id == project_id
        )
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TimelineEvent {event_id} not found",
        )
    
    return event


@router.put("/{event_id}", response_model=TimelineEventRead)
async def update_timeline_event(
    project_id: Annotated[str, Path(description="项目ID")],
    event_id: Annotated[str, Path(description="事件ID")],
    event_data: TimelineEventUpdate,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> TimelineEvent:
    """更新时间线事件"""
    result = await db.execute(
        select(TimelineEvent).where(
            TimelineEvent.id == event_id,
            TimelineEvent.project_id == project_id
        )
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TimelineEvent {event_id} not found",
        )
    
    update_data = event_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(event, key, value)
    
    await db.flush()
    await db.refresh(event)
    
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_timeline_event(
    project_id: Annotated[str, Path(description="项目ID")],
    event_id: Annotated[str, Path(description="事件ID")],
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> None:
    """删除时间线事件"""
    result = await db.execute(
        select(TimelineEvent).where(
            TimelineEvent.id == event_id,
            TimelineEvent.project_id == project_id
        )
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TimelineEvent {event_id} not found",
        )
    
    await db.delete(event)
    await db.flush()


@router.post("/generate")
async def generate_timeline_from_outline(
    project_id: Annotated[str, Path(description="项目ID")],
) -> dict:
    """
    AI 从大纲自动生成时间线事件
    
    读取项目大纲，调用 LLM 提取关键事件，
    生成时间线事件列表（包含 time_point, event_type, sort_order）
    """
    llm = get_llm_service()
    generator = TimelineGenerator(llm)
    
    events = await generator.generate_from_outline(project_id)
    
    return {
        "events": events,
        "count": len(events),
        "message": "时间线事件已生成并保存" if events else "未找到可生成的事件",
    }
