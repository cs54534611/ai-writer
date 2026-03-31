"""Faction API 路由 - 势力/组织管理"""

from datetime import datetime
from typing import Annotated, AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import get_db_manager
from src.models.faction import Faction

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


class FactionCreate(SQLModel):
    name: str
    parent_id: str | None = None
    color: str = "#6366f1"
    description: str | None = None


class FactionUpdate(SQLModel):
    name: str | None = None
    parent_id: str | None = None
    color: str | None = None
    description: str | None = None


class FactionRead(SQLModel):
    id: str
    project_id: str
    name: str
    parent_id: str | None
    color: str
    description: str | None
    created_at: datetime
    updated_at: datetime


@router.post("/", response_model=FactionRead, status_code=status.HTTP_201_CREATED)
async def create_faction(
    project_id: Annotated[str, Path(description="项目ID")],
    faction_data: FactionCreate,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> Faction:
    """创建新势力"""
    faction = Faction(
        project_id=project_id,
        **faction_data.model_dump()
    )
    db.add(faction)
    await db.flush()
    await db.refresh(faction)
    return faction


@router.get("/", response_model=list[FactionRead])
async def list_factions(
    project_id: Annotated[str, Path(description="项目ID")],
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> list[Faction]:
    """获取势力列表"""
    query = select(Faction).where(Faction.project_id == project_id).order_by(Faction.name)
    result = await db.execute(query)
    factions = result.scalars().all()
    return list(factions)


@router.get("/{faction_id}", response_model=FactionRead)
async def get_faction(
    project_id: Annotated[str, Path(description="项目ID")],
    faction_id: Annotated[str, Path(description="势力ID")],
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> Faction:
    """获取单个势力"""
    result = await db.execute(
        select(Faction).where(
            Faction.id == faction_id,
            Faction.project_id == project_id
        )
    )
    faction = result.scalar_one_or_none()
    
    if not faction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Faction {faction_id} not found",
        )
    
    return faction


@router.put("/{faction_id}", response_model=FactionRead)
async def update_faction(
    project_id: Annotated[str, Path(description="项目ID")],
    faction_id: Annotated[str, Path(description="势力ID")],
    faction_data: FactionUpdate,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> Faction:
    """更新势力"""
    result = await db.execute(
        select(Faction).where(
            Faction.id == faction_id,
            Faction.project_id == project_id
        )
    )
    faction = result.scalar_one_or_none()
    
    if not faction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Faction {faction_id} not found",
        )
    
    update_data = faction_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(faction, key, value)
    
    faction.updated_at = datetime.utcnow()
    await db.flush()
    await db.refresh(faction)
    
    return faction


@router.delete("/{faction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_faction(
    project_id: Annotated[str, Path(description="项目ID")],
    faction_id: Annotated[str, Path(description="势力ID")],
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> None:
    """删除势力"""
    result = await db.execute(
        select(Faction).where(
            Faction.id == faction_id,
            Faction.project_id == project_id
        )
    )
    faction = result.scalar_one_or_none()
    
    if not faction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Faction {faction_id} not found",
        )
    
    await db.delete(faction)
    await db.flush()


from sqlmodel import SQLModel  # 确保 SQLModel 可用
