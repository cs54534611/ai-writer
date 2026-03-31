"""世界设定 API 路由"""

import json
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import get_db_manager
from src.models.world_setting import WorldSetting, SettingCategory
from src.schemas.world_setting import (
    WorldSettingCreate,
    WorldSettingRead,
    WorldSettingUpdate,
)


router = APIRouter()


async def get_setting_db(
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


@router.post("/", response_model=WorldSettingRead, status_code=status.HTTP_201_CREATED)
async def create_world_setting(
    project_id: str,
    setting_data: WorldSettingCreate,
    db: Annotated[AsyncSession, Depends(get_setting_db)],
) -> WorldSetting:
    """创建设定"""
    setting = WorldSetting(
        project_id=project_id,
        **setting_data.model_dump(),
    )
    db.add(setting)
    await db.flush()
    await db.refresh(setting)
    return WorldSettingRead.from_orm_with_relations(setting)


@router.get("/", response_model=list[WorldSettingRead])
async def list_world_settings(
    project_id: str,
    db: Annotated[AsyncSession, Depends(get_setting_db)],
    category: Optional[SettingCategory] = Query(default=None, description="按类别筛选"),
) -> list[WorldSettingRead]:
    """获取设定列表"""
    query = select(WorldSetting).where(WorldSetting.project_id == project_id)

    if category:
        query = query.where(WorldSetting.category == category)

    query = query.order_by(WorldSetting.updated_at.desc())
    result = await db.execute(query)
    settings = result.scalars().all()

    return [WorldSettingRead.from_orm_with_relations(s) for s in settings]


@router.put("/{setting_id}", response_model=WorldSettingRead)
async def update_world_setting(
    project_id: str,
    setting_id: str,
    setting_data: WorldSettingUpdate,
    db: Annotated[AsyncSession, Depends(get_setting_db)],
) -> WorldSetting:
    """更新设定"""
    result = await db.execute(
        select(WorldSetting).where(
            WorldSetting.id == setting_id,
            WorldSetting.project_id == project_id,
        )
    )
    setting = result.scalar_one_or_none()

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"WorldSetting {setting_id} not found",
        )

    update_data = setting_data.model_dump(exclude_unset=True)

    # 处理 related_setting_ids
    if "related_setting_ids" in update_data:
        related_ids = update_data.pop("related_setting_ids")
        if related_ids is not None:
            setting.set_related_setting_ids(related_ids)

    for key, value in update_data.items():
        setattr(setting, key, value)

    setting.updated_at = datetime.utcnow()
    await db.flush()
    await db.refresh(setting)

    return WorldSettingRead.from_orm_with_relations(setting)


@router.delete("/{setting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_world_setting(
    project_id: str,
    setting_id: str,
    db: Annotated[AsyncSession, Depends(get_setting_db)],
) -> None:
    """删除设定"""
    result = await db.execute(
        select(WorldSetting).where(
            WorldSetting.id == setting_id,
            WorldSetting.project_id == project_id,
        )
    )
    setting = result.scalar_one_or_none()

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"WorldSetting {setting_id} not found",
        )

    await db.delete(setting)
    await db.flush()
