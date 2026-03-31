"""Inspiration API 路由"""

from typing import Annotated, AsyncGenerator, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import get_db_manager
from src.models.inspiration import Inspiration
from src.schemas.inspiration import (
    InspirationCreate,
    InspirationUpdate,
    InspirationRead,
    InspirationListResponse,
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


@router.post("/", response_model=InspirationRead, status_code=status.HTTP_201_CREATED)
async def create_inspiration(
    project_id: Annotated[str, Path(description="项目ID")],
    inspiration_data: InspirationCreate,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> Inspiration:
    """创建新灵感"""
    inspiration = Inspiration(
        project_id=project_id,
        **inspiration_data.model_dump()
    )
    db.add(inspiration)
    await db.flush()
    await db.refresh(inspiration)
    return inspiration


@router.get("/", response_model=InspirationListResponse)
async def list_inspirations(
    project_id: Annotated[str, Path(description="项目ID")],
    db: Annotated[AsyncSession, Depends(get_project_db)],
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    tag: Optional[str] = Query(default=None, description="标签筛选"),
) -> InspirationListResponse:
    """获取灵感列表（支持标签筛选）"""
    # 构建基础查询
    base_query = select(Inspiration).where(Inspiration.project_id == project_id)
    
    # 如果有标签筛选，添加过滤条件
    # tags 存储为 JSON 数组字符串，如 '["人物", "剧情"]'
    if tag:
        # 使用 LIKE 进行简单匹配
        base_query = base_query.where(Inspiration.tags.like(f'%"{tag}"%'))
    
    # 获取总数（使用 COUNT 而非全量查询）
    from sqlmodel import func
    count_query = select(func.count()).select_from(Inspiration).where(Inspiration.project_id == project_id)
    if tag:
        count_query = count_query.where(Inspiration.tags.like(f'%"{tag}"%'))
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    # 分页查询
    offset = (page - 1) * page_size
    query = (
        base_query
        .order_by(Inspiration.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    inspirations = result.scalars().all()
    
    return InspirationListResponse(
        items=list(inspirations),
        total=total,
        page=page,
        page_size=page_size,
    )


@router.put("/{inspiration_id}", response_model=InspirationRead)
async def update_inspiration(
    project_id: Annotated[str, Path(description="项目ID")],
    inspiration_id: Annotated[str, Path(description="灵感ID")],
    inspiration_data: InspirationUpdate,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> Inspiration:
    """更新灵感"""
    result = await db.execute(
        select(Inspiration).where(
            Inspiration.id == inspiration_id,
            Inspiration.project_id == project_id
        )
    )
    inspiration = result.scalar_one_or_none()
    
    if not inspiration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inspiration {inspiration_id} not found",
        )
    
    update_data = inspiration_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(inspiration, key, value)
    
    await db.flush()
    await db.refresh(inspiration)
    
    return inspiration


@router.delete("/{inspiration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inspiration(
    project_id: Annotated[str, Path(description="项目ID")],
    inspiration_id: Annotated[str, Path(description="灵感ID")],
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> None:
    """删除灵感"""
    result = await db.execute(
        select(Inspiration).where(
            Inspiration.id == inspiration_id,
            Inspiration.project_id == project_id
        )
    )
    inspiration = result.scalar_one_or_none()
    
    if not inspiration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inspiration {inspiration_id} not found",
        )
    
    await db.delete(inspiration)
    await db.flush()
