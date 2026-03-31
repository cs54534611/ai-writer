"""大纲节点 API 路由"""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import get_db_manager
from src.models.outline import OutlineNode
from src.schemas.outline import (
    OutlineNodeCreate,
    OutlineNodeRead,
    OutlineNodeTree,
    OutlineNodeUpdate,
)
from src.services.llm import get_llm_service
from src.services.outline_optimizer import OutlineOptimizer


router = APIRouter()


async def get_outline_db(
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


def build_outline_tree(nodes: list[OutlineNode]) -> list[OutlineNodeTree]:
    """构建大纲树形结构"""
    node_dict: dict[str, OutlineNodeTree] = {}
    root_nodes: list[OutlineNodeTree] = []

    # 先将所有节点转换为树节点
    for node in nodes:
        node_dict[node.id] = OutlineNodeTree(
            id=node.id,
            project_id=node.project_id,
            parent_id=node.parent_id,
            title=node.title,
            summary=node.summary,
            word_target=node.word_target,
            narrative_pov=node.narrative_pov,
            sort_order=node.sort_order,
            line_type=node.line_type,
            created_at=node.created_at,
            updated_at=node.updated_at,
            children=[],
        )

    # 构建父子关系
    for node in nodes:
        tree_node = node_dict[node.id]
        if node.parent_id and node.parent_id in node_dict:
            node_dict[node.parent_id].children.append(tree_node)
        else:
            root_nodes.append(tree_node)

    # 对每个层级的子节点按 sort_order 排序
    def sort_children(node: OutlineNodeTree) -> None:
        node.children.sort(key=lambda x: x.sort_order)
        for child in node.children:
            sort_children(child)

    root_nodes.sort(key=lambda x: x.sort_order)
    for root in root_nodes:
        sort_children(root)

    return root_nodes


class ReorderRequest(BaseModel):
    """批量重排序请求"""
    items: list[dict] = Field(
        description="重排序项列表，格式: [{id: str, sort_order: int, parent_id: str | null}]"
    )


@router.post("/", response_model=OutlineNodeRead, status_code=status.HTTP_201_CREATED)
async def create_outline(
    project_id: str,
    outline_data: OutlineNodeCreate,
    db: Annotated[AsyncSession, Depends(get_outline_db)],
) -> OutlineNode:
    """创建大纲节点"""
    outline = OutlineNode(
        project_id=project_id,
        **outline_data.model_dump(),
    )
    db.add(outline)
    await db.flush()
    await db.refresh(outline)
    return outline


@router.get("/", response_model=list[OutlineNodeTree])
async def list_outlines(
    project_id: str,
    db: Annotated[AsyncSession, Depends(get_outline_db)],
) -> list[OutlineNodeTree]:
    """获取大纲树（树形结构）"""
    result = await db.execute(
        select(OutlineNode)
        .where(OutlineNode.project_id == project_id)
        .order_by(OutlineNode.sort_order)
    )
    nodes = result.scalars().all()
    return build_outline_tree(list(nodes))


@router.put("/{outline_id}", response_model=OutlineNodeRead)
async def update_outline(
    project_id: str,
    outline_id: str,
    outline_data: OutlineNodeUpdate,
    db: Annotated[AsyncSession, Depends(get_outline_db)],
) -> OutlineNode:
    """更新大纲节点"""
    result = await db.execute(
        select(OutlineNode).where(
            OutlineNode.id == outline_id,
            OutlineNode.project_id == project_id,
        )
    )
    outline = result.scalar_one_or_none()

    if not outline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Outline {outline_id} not found",
        )

    update_data = outline_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(outline, key, value)

    outline.updated_at = datetime.utcnow()
    await db.flush()
    await db.refresh(outline)

    return outline


@router.delete("/{outline_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_outline(
    project_id: str,
    outline_id: str,
    db: Annotated[AsyncSession, Depends(get_outline_db)],
) -> None:
    """删除大纲节点"""
    result = await db.execute(
        select(OutlineNode).where(
            OutlineNode.id == outline_id,
            OutlineNode.project_id == project_id,
        )
    )
    outline = result.scalar_one_or_none()

    if not outline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Outline {outline_id} not found",
        )

    await db.delete(outline)
    await db.flush()


@router.put("/reorder", response_model=list[OutlineNodeTree])
async def reorder_outlines(
    project_id: str,
    reorder_data: ReorderRequest,
    db: Annotated[AsyncSession, Depends(get_outline_db)],
) -> list[OutlineNodeTree]:
    """批量重排序大纲节点"""
    updated_ids: list[str] = []

    for item in reorder_data.items:
        outline_id = item.get("id")
        if not outline_id:
            continue

        result = await db.execute(
            select(OutlineNode).where(
                OutlineNode.id == outline_id,
                OutlineNode.project_id == project_id,
            )
        )
        outline = result.scalar_one_or_none()

        if outline:
            if "sort_order" in item:
                outline.sort_order = item["sort_order"]
            if "parent_id" in item:
                outline.parent_id = item["parent_id"]
            outline.updated_at = datetime.utcnow()
            updated_ids.append(outline_id)

    await db.flush()

    # 返回更新后的树
    result = await db.execute(
        select(OutlineNode)
        .where(OutlineNode.project_id == project_id)
        .order_by(OutlineNode.sort_order)
    )
    nodes = result.scalars().all()
    return build_outline_tree(list(nodes))


class OptimizeRequest(BaseModel):
    """智能优化章节节奏请求"""
    target_words: int = Field(
        default=100000,
        ge=10000,
        le=10000000,
        description="目标总字数（1万-1000万）"
    )


@router.post("/optimize")
async def optimize_chapter_rhythm(
    project_id: str,
    optimize_data: OptimizeRequest,
) -> dict:
    """
    AI 智能优化章节字数分配
    
    根据目标总字数，智能分配每个大纲节点的建议字数。
    - 开头（前10%）：15% 字数
    - 中段（60%）：55% 字数
    - 结尾（30%）：30% 字数
    - 主线章节比支线章节分配更多字数
    """
    llm = get_llm_service()
    optimizer = OutlineOptimizer(llm)
    
    result = await optimizer.optimize_chapter_rhythm(
        project_id=project_id,
        target_words=optimize_data.target_words,
    )
    
    return result
