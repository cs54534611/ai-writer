"""地点 API 路由"""

from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import get_db_manager
from src.models.location import Location, SpatialLayer
from src.schemas.location import (
    LocationCreate,
    LocationMapResponse,
    LocationRead,
    LocationUpdate,
)


router = APIRouter()


async def get_location_db(
    project_id: Annotated[str, Path(description="项目ID")]
) -> AsyncSession:
    """获取项目数据库会话"""
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


@router.post("/", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
async def create_location(
    project_id: str,
    location_data: LocationCreate,
    db: Annotated[AsyncSession, Depends(get_location_db)],
) -> Location:
    """创建地点"""
    location = Location(
        project_id=project_id,
        **location_data.model_dump(),
    )
    db.add(location)
    await db.flush()
    await db.refresh(location)
    return location


@router.get("/", response_model=list[LocationRead])
async def list_locations(
    project_id: str,
    db: Annotated[AsyncSession, Depends(get_location_db)],
    layer: Optional[SpatialLayer] = Query(default=None, description="按空间层级筛选"),
) -> list[Location]:
    """获取地点列表"""
    query = select(Location).where(Location.project_id == project_id)

    if layer:
        query = query.where(Location.layer == layer)

    query = query.order_by(Location.layer, Location.position_y, Location.position_x)
    result = await db.execute(query)
    locations = result.scalars().all()

    return list(locations)


@router.get("/map", response_model=LocationMapResponse)
async def get_location_map(
    project_id: str,
    db: Annotated[AsyncSession, Depends(get_location_db)],
) -> LocationMapResponse:
    """获取地图数据（用于前端渲染）"""
    result = await db.execute(
        select(Location)
        .where(Location.project_id == project_id)
        .order_by(Location.layer, Location.position_y, Location.position_x)
    )
    locations = result.scalars().all()

    # 获取所有层级
    layers = list(set(loc.layer for loc in locations))
    layer_order = ["celestial", "material", "underworld", "realm", "void"]
    layers.sort(key=lambda x: layer_order.index(x) if x in layer_order else 99)

    return LocationMapResponse(
        locations=list(locations),
        layers=layers,
    )


@router.put("/{location_id}", response_model=LocationRead)
async def update_location(
    project_id: str,
    location_id: str,
    location_data: LocationUpdate,
    db: Annotated[AsyncSession, Depends(get_location_db)],
) -> Location:
    """更新地点"""
    result = await db.execute(
        select(Location).where(
            Location.id == location_id,
            Location.project_id == project_id,
        )
    )
    location = result.scalar_one_or_none()

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location {location_id} not found",
        )

    update_data = location_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(location, key, value)

    location.updated_at = datetime.utcnow()
    await db.flush()
    await db.refresh(location)

    return location


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    project_id: str,
    location_id: str,
    db: Annotated[AsyncSession, Depends(get_location_db)],
) -> None:
    """删除地点"""
    result = await db.execute(
        select(Location).where(
            Location.id == location_id,
            Location.project_id == project_id,
        )
    )
    location = result.scalar_one_or_none()

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location {location_id} not found",
        )

    await db.delete(location)
    await db.flush()
