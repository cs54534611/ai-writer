"""Relationship API 路由"""

from typing import Annotated, AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import get_db_manager
from src.models.relationship import Relationship
from src.models.character import Character
from src.schemas.relationship import (
    RelationshipCreate,
    RelationshipRead,
    RelationshipListResponse,
    RelationshipGraphResponse,
    RelationshipGraphNode,
    RelationshipGraphLink,
    SuggestRelationshipRequest,
)
from src.services.relationship_suggestion import get_relationship_suggestion_service

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


@router.post("/", response_model=RelationshipRead, status_code=status.HTTP_201_CREATED)
async def create_relationship(
    project_id: Annotated[str, Path(description="项目ID")],
    relationship_data: RelationshipCreate,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> Relationship:
    """创建新角色关系"""
    # 验证角色存在
    char_from = await db.execute(
        select(Character).where(
            Character.id == relationship_data.from_character_id,
            Character.project_id == project_id
        )
    )
    if not char_from.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Character {relationship_data.from_character_id} not found",
        )
    
    char_to = await db.execute(
        select(Character).where(
            Character.id == relationship_data.to_character_id,
            Character.project_id == project_id
        )
    )
    if not char_to.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Character {relationship_data.to_character_id} not found",
        )
    
    relationship = Relationship(
        project_id=project_id,
        **relationship_data.model_dump()
    )
    db.add(relationship)
    await db.flush()
    await db.refresh(relationship)
    return relationship


@router.get("/", response_model=RelationshipListResponse)
async def list_relationships(
    project_id: Annotated[str, Path(description="项目ID")],
    db: Annotated[AsyncSession, Depends(get_project_db)],
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
) -> RelationshipListResponse:
    """获取角色关系列表（分页）"""
    # 获取总数
    count_query = select(Relationship).where(Relationship.project_id == project_id)
    result = await db.execute(count_query)
    total = len(result.scalars().all())
    
    # 分页查询
    offset = (page - 1) * page_size
    query = (
        select(Relationship)
        .where(Relationship.project_id == project_id)
        .order_by(Relationship.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    relationships = result.scalars().all()
    
    return RelationshipListResponse(
        items=list(relationships),
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/graph", response_model=RelationshipGraphResponse)
async def get_relationship_graph(
    project_id: Annotated[str, Path(description="项目ID")],
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> RelationshipGraphResponse:
    """获取关系图数据（用于D3.js力导向图）"""
    # 获取所有角色作为节点
    char_result = await db.execute(
        select(Character).where(Character.project_id == project_id)
    )
    characters = char_result.scalars().all()
    
    # 获取所有关系作为链接
    rel_result = await db.execute(
        select(Relationship).where(Relationship.project_id == project_id)
    )
    relationships = rel_result.scalars().all()
    
    # 构建节点列表
    nodes = [
        RelationshipGraphNode(id=c.id, name=c.name)
        for c in characters
    ]
    
    # 构建链接列表
    links = [
        RelationshipGraphLink(
            source=r.from_character_id,
            target=r.to_character_id,
            type=r.relation_type,
            strength=r.strength
        )
        for r in relationships
    ]
    
    return RelationshipGraphResponse(nodes=nodes, links=links)


@router.delete("/{relationship_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_relationship(
    project_id: Annotated[str, Path(description="项目ID")],
    relationship_id: Annotated[str, Path(description="关系ID")],
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> None:
    """删除角色关系"""
    result = await db.execute(
        select(Relationship).where(
            Relationship.id == relationship_id,
            Relationship.project_id == project_id
        )
    )
    relationship = result.scalar_one_or_none()
    
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relationship {relationship_id} not found",
        )
    
    await db.delete(relationship)
    await db.flush()


@router.post("/suggest")
async def suggest_relationship(
    project_id: Annotated[str, Path(description="项目ID")],
    request: SuggestRelationshipRequest,
) -> dict:
    """AI 建议两个角色之间的关系类型
    
    根据两个角色的背景信息，AI 分析并推荐最合适的关系类型。
    
    - **char1_id**: 角色1的ID
    - **char2_id**: 角色2的ID
    
    返回建议的关系类型、理由和置信度。
    """
    service = get_relationship_suggestion_service()
    
    # 获取角色信息
    char1_profile = request.char1_profile
    char2_profile = request.char2_profile
    
    result = await service.suggest_relationship(char1_profile, char2_profile)
    
    return result
