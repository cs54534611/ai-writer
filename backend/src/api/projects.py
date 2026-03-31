"""项目 CRUD API 路由"""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import get_db_manager
from src.models.project import Project
from src.schemas.project import (
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    ProjectListResponse,
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


async def get_default_db() -> AsyncGenerator[AsyncSession, None]:
    """获取默认数据库会话（用于列表查询等不需要特定项目的操作）"""
    # 使用一个默认的项目 ID 来初始化默认数据库
    default_project_id = "_default"
    db_manager = get_db_manager()
    if default_project_id not in db_manager._engines:
        await db_manager.init_project_db(default_project_id)
    
    engine = db_manager._engines[default_project_id]
    session = AsyncSession(engine, expire_on_commit=False)
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: Annotated[AsyncSession, Depends(get_default_db)],
) -> Project:
    """创建新项目"""
    project = Project(**project_data.model_dump())
    db.add(project)
    await db.flush()
    await db.refresh(project)
    return project


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    db: Annotated[AsyncSession, Depends(get_default_db)],
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    status_filter: str = Query(default=None, alias="status", description="状态过滤"),
) -> ProjectListResponse:
    """获取项目列表（分页）"""
    query = select(Project)
    
    if status_filter:
        query = query.where(Project.status == status_filter)
    
    query = query.order_by(Project.updated_at.desc())
    
    # 获取总数
    count_query = select(Project)
    if status_filter:
        count_query = count_query.where(Project.status == status_filter)
    result = await db.execute(count_query)
    total = len(result.all())
    
    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    projects = result.scalars().all()
    
    return ProjectListResponse(
        items=list(projects),
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: str,
    db: Annotated[AsyncSession, Depends(get_default_db)],
) -> Project:
    """获取单个项目"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    return project


@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    db: Annotated[AsyncSession, Depends(get_default_db)],
) -> Project:
    """更新项目"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    update_data = project_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    
    project.updated_at = datetime.utcnow()
    await db.flush()
    await db.refresh(project)
    
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db: Annotated[AsyncSession, Depends(get_default_db)],
) -> None:
    """删除项目"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    await db.delete(project)
    await db.flush()
