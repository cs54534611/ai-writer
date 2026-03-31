"""Character CRUD API 路由"""

from datetime import datetime
from typing import Annotated, AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import get_db_manager
from src.models.character import Character
from src.schemas.character import (
    CharacterCreate,
    CharacterUpdate,
    CharacterRead,
    CharacterListResponse,
)

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


@router.post("/", response_model=CharacterRead, status_code=status.HTTP_201_CREATED)
async def create_character(
    project_id: Annotated[str, Path(description="项目ID")],
    character_data: CharacterCreate,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> Character:
    """创建新角色"""
    character = Character(
        project_id=project_id,
        **character_data.model_dump()
    )
    db.add(character)
    await db.flush()
    await db.refresh(character)
    return character


@router.get("/", response_model=CharacterListResponse)
async def list_characters(
    project_id: Annotated[str, Path(description="项目ID")],
    db: Annotated[AsyncSession, Depends(get_project_db)],
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
) -> CharacterListResponse:
    """获取角色列表（分页）"""
    # 获取总数（使用 COUNT 而非全量查询）
    from sqlmodel import func
    count_query = select(func.count()).select_from(Character).where(Character.project_id == project_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    # 分页查询
    offset = (page - 1) * page_size
    query = (
        select(Character)
        .where(Character.project_id == project_id)
        .order_by(Character.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    characters = result.scalars().all()
    
    return CharacterListResponse(
        items=list(characters),
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{character_id}", response_model=CharacterRead)
async def get_character(
    project_id: Annotated[str, Path(description="项目ID")],
    character_id: Annotated[str, Path(description="角色ID")],
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> Character:
    """获取单个角色"""
    result = await db.execute(
        select(Character).where(
            Character.id == character_id,
            Character.project_id == project_id
        )
    )
    character = result.scalar_one_or_none()
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {character_id} not found",
        )
    
    return character


@router.put("/{character_id}", response_model=CharacterRead)
async def update_character(
    project_id: Annotated[str, Path(description="项目ID")],
    character_id: Annotated[str, Path(description="角色ID")],
    character_data: CharacterUpdate,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> Character:
    """更新角色"""
    result = await db.execute(
        select(Character).where(
            Character.id == character_id,
            Character.project_id == project_id
        )
    )
    character = result.scalar_one_or_none()
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {character_id} not found",
        )
    
    update_data = character_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(character, key, value)
    
    character.updated_at = datetime.utcnow()
    await db.flush()
    await db.refresh(character)
    
    return character


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(
    project_id: Annotated[str, Path(description="项目ID")],
    character_id: Annotated[str, Path(description="角色ID")],
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> None:
    """删除角色"""
    result = await db.execute(
        select(Character).where(
            Character.id == character_id,
            Character.project_id == project_id
        )
    )
    character = result.scalar_one_or_none()
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {character_id} not found",
        )
    
    await db.delete(character)
    await db.flush()
