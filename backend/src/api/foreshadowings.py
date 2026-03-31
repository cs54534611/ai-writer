"""伏笔管理 CRUD API 路由"""

from datetime import datetime
from typing import Annotated, AsyncGenerator, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from pydantic import BaseModel, Field
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import get_db_manager
from src.models.foreshadowing import Foreshadowing, ForeshadowingStatus


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


# Schema 定义
class ForeshadowingCreate(BaseModel):
    """创建伏笔的请求模型"""
    chapter_id: str = Field(max_length=36, description="章节ID")
    description: str = Field(max_length=1000, description="伏笔内容描述")
    notes: Optional[str] = Field(default=None, max_length=2000, description="备注")


class ForeshadowingUpdate(BaseModel):
    """更新伏笔的请求模型"""
    description: Optional[str] = Field(default=None, max_length=1000, description="伏笔内容描述")
    status: Optional[ForeshadowingStatus] = Field(default=None, description="伏笔状态")
    notes: Optional[str] = Field(default=None, max_length=2000, description="备注")


class ForeshadowingRead(BaseModel):
    """伏笔响应模型"""
    id: str
    project_id: str
    chapter_id: str
    description: str
    status: str
    notes: Optional[str]
    planted_at: datetime
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ForeshadowingListResponse(BaseModel):
    """伏笔列表响应模型"""
    items: list[ForeshadowingRead]
    total: int
    page: int
    page_size: int


@router.get("/", response_model=ForeshadowingListResponse)
async def list_foreshadowings(
    project_id: str,
    db: Annotated[AsyncSession, Depends(get_project_db)],
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=50, ge=1, le=200, description="每页数量"),
    chapter_id: Optional[str] = Query(default=None, description="按章节过滤"),
    status_filter: Optional[str] = Query(default=None, alias="status", description="按状态过滤"),
) -> ForeshadowingListResponse:
    """获取伏笔列表（分页）"""
    query = select(Foreshadowing).where(Foreshadowing.project_id == project_id)
    
    if chapter_id:
        query = query.where(Foreshadowing.chapter_id == chapter_id)
    if status_filter:
        query = query.where(Foreshadowing.status == status_filter)
    
    # 获取总数
    count_query = select(Foreshadowing).where(Foreshadowing.project_id == project_id)
    if chapter_id:
        count_query = count_query.where(Foreshadowing.chapter_id == chapter_id)
    if status_filter:
        count_query = count_query.where(Foreshadowing.status == status_filter)
    
    result = await db.execute(count_query)
    total = len(result.all())
    
    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    query = query.order_by(Foreshadowing.planted_at.desc())
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    return ForeshadowingListResponse(
        items=list(items),
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/", response_model=ForeshadowingRead, status_code=status.HTTP_201_CREATED)
async def create_foreshadowing(
    project_id: str,
    foreshadowing_data: ForeshadowingCreate,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> Foreshadowing:
    """创建伏笔"""
    foreshadowing = Foreshadowing(
        project_id=project_id,
        chapter_id=foreshadowing_data.chapter_id,
        description=foreshadowing_data.description,
        notes=foreshadowing_data.notes,
        status=ForeshadowingStatus.PLANTED,
    )
    db.add(foreshadowing)
    await db.flush()
    await db.refresh(foreshadowing)
    
    return foreshadowing


@router.get("/{foreshadowing_id}", response_model=ForeshadowingRead)
async def get_foreshadowing(
    project_id: str,
    foreshadowing_id: str,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> Foreshadowing:
    """获取单个伏笔"""
    result = await db.execute(
        select(Foreshadowing).where(
            Foreshadowing.project_id == project_id,
            Foreshadowing.id == foreshadowing_id,
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"伏笔 {foreshadowing_id} 未找到",
        )
    
    return item


@router.put("/{foreshadowing_id}", response_model=ForeshadowingRead)
async def update_foreshadowing(
    project_id: str,
    foreshadowing_id: str,
    foreshadowing_data: ForeshadowingUpdate,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> Foreshadowing:
    """更新伏笔"""
    result = await db.execute(
        select(Foreshadowing).where(
            Foreshadowing.project_id == project_id,
            Foreshadowing.id == foreshadowing_id,
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"伏笔 {foreshadowing_id} 未找到",
        )
    
    update_data = foreshadowing_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
    
    # 如果状态变更为已回收，设置回收时间
    if foreshadowing_data.status == ForeshadowingStatus.RESOLVED and item.status != ForeshadowingStatus.RESOLVED:
        item.resolved_at = datetime.utcnow()
    
    item.updated_at = datetime.utcnow()
    await db.flush()
    await db.refresh(item)
    
    return item


@router.delete("/{foreshadowing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_foreshadowing(
    project_id: str,
    foreshadowing_id: str,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> None:
    """删除伏笔"""
    result = await db.execute(
        select(Foreshadowing).where(
            Foreshadowing.project_id == project_id,
            Foreshadowing.id == foreshadowing_id,
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"伏笔 {foreshadowing_id} 未找到",
        )
    
    await db.delete(item)
    await db.flush()


@router.post("/{foreshadowing_id}/resolve", response_model=ForeshadowingRead)
async def resolve_foreshadowing(
    project_id: str,
    foreshadowing_id: str,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> Foreshadowing:
    """回收伏笔（标记为已回收）"""
    result = await db.execute(
        select(Foreshadowing).where(
            Foreshadowing.project_id == project_id,
            Foreshadowing.id == foreshadowing_id,
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"伏笔 {foreshadowing_id} 未找到",
        )
    
    item.status = ForeshadowingStatus.RESOLVED
    item.resolved_at = datetime.utcnow()
    item.updated_at = datetime.utcnow()
    
    await db.flush()
    await db.refresh(item)
    
    return item


@router.post("/{foreshadowing_id}/expire", response_model=ForeshadowingRead)
async def expire_foreshadowing(
    project_id: str,
    foreshadowing_id: str,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> Foreshadowing:
    """标记伏笔为失效"""
    result = await db.execute(
        select(Foreshadowing).where(
            Foreshadowing.project_id == project_id,
            Foreshadowing.id == foreshadowing_id,
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"伏笔 {foreshadowing_id} 未找到",
        )
    
    item.status = ForeshadowingStatus.EXPIRED
    item.updated_at = datetime.utcnow()
    
    await db.flush()
    await db.refresh(item)
    
    return item


@router.get("/stats/summary", response_model=dict)
async def get_foreshadowing_stats(
    project_id: str,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> dict:
    """获取伏笔统计信息"""
    # 获取各类状态的伏笔数量
    planted_result = await db.execute(
        select(Foreshadowing).where(
            Foreshadowing.project_id == project_id,
            Foreshadowing.status == ForeshadowingStatus.PLANTED,
        )
    )
    resolved_result = await db.execute(
        select(Foreshadowing).where(
            Foreshadowing.project_id == project_id,
            Foreshadowing.status == ForeshadowingStatus.RESOLVED,
        )
    )
    expired_result = await db.execute(
        select(Foreshadowing).where(
            Foreshadowing.project_id == project_id,
            Foreshadowing.status == ForeshadowingStatus.EXPIRED,
        )
    )
    
    all_result = await db.execute(
        select(Foreshadowing).where(Foreshadowing.project_id == project_id)
    )
    
    planted_count = len(planted_result.scalars().all())
    resolved_count = len(resolved_result.scalars().all())
    expired_count = len(expired_result.scalars().all())
    total_count = len(all_result.scalars().all())
    
    # 计算回收率
    resolution_rate = (resolved_count / total_count * 100) if total_count > 0 else 0
    
    return {
        "total": total_count,
        "planted": planted_count,
        "resolved": resolved_count,
        "expired": expired_count,
        "resolution_rate": round(resolution_rate, 1),
    }
