"""章节 API 路由 - CRUD + AI 写作"""

import json
import uuid
from datetime import datetime
from typing import Annotated, AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.responses import StreamingResponse
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import get_db_manager
from src.models.chapter import Chapter, ChapterStatus
from src.schemas.chapter import (
    ChapterCreate,
    ChapterListResponse,
    ChapterRead,
    ChapterUpdate,
    DialogueWriteRequest,
    WritingContinueRequest,
    WritingEnhanceRequest,
    WritingExpandRequest,
    WritingFeedbackRequest,
    WritingFeedbackResponse,
    WritingRewriteRequest,
)
from src.services.llm import get_llm_service
from src.services.writing import WritingService


router = APIRouter()


async def get_chapter_db(
    project_id: Annotated[str, Path(description="项目ID")],
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


def get_writing_service() -> WritingService:
    """获取写作服务实例"""
    llm = get_llm_service()
    return WritingService(llm)


# ========================
# CRUD 路由
# ========================

@router.post("/", response_model=ChapterRead, status_code=status.HTTP_201_CREATED)
async def create_chapter(
    project_id: str,
    chapter_data: ChapterCreate,
    db: Annotated[AsyncSession, Depends(get_chapter_db)],
) -> Chapter:
    """创建新章节"""
    chapter = Chapter(
        project_id=project_id,
        **chapter_data.model_dump(),
    )
    db.add(chapter)
    await db.flush()
    await db.refresh(chapter)
    return chapter


@router.get("/", response_model=ChapterListResponse)
async def list_chapters(
    project_id: str,
    db: Annotated[AsyncSession, Depends(get_chapter_db)],
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=50, ge=1, le=200, description="每页数量"),
    status_filter: str | None = Query(default=None, alias="status", description="状态过滤"),
) -> ChapterListResponse:
    """获取章节列表（分页）"""
    query = select(Chapter).where(Chapter.project_id == project_id)

    if status_filter:
        query = query.where(Chapter.status == status_filter)

    query = query.order_by(Chapter.sort_order, Chapter.created_at)

    # 获取总数（使用 COUNT 而非全量查询）
    from sqlmodel import func
    count_query = select(func.count()).select_from(Chapter).where(Chapter.project_id == project_id)
    if status_filter:
        count_query = count_query.where(Chapter.status == status_filter)
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    chapters = result.scalars().all()

    return ChapterListResponse(
        items=list(chapters),
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{chapter_id}", response_model=ChapterRead)
async def get_chapter(
    project_id: str,
    chapter_id: str,
    db: Annotated[AsyncSession, Depends(get_chapter_db)],
) -> Chapter:
    """获取单个章节"""
    result = await db.execute(
        select(Chapter).where(
            Chapter.id == chapter_id,
            Chapter.project_id == project_id,
        )
    )
    chapter = result.scalar_one_or_none()

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter {chapter_id} not found",
        )

    return chapter


@router.put("/{chapter_id}", response_model=ChapterRead)
async def update_chapter(
    project_id: str,
    chapter_id: str,
    chapter_data: ChapterUpdate,
    db: Annotated[AsyncSession, Depends(get_chapter_db)],
) -> Chapter:
    """更新章节"""
    result = await db.execute(
        select(Chapter).where(
            Chapter.id == chapter_id,
            Chapter.project_id == project_id,
        )
    )
    chapter = result.scalar_one_or_none()

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter {chapter_id} not found",
        )

    update_data = chapter_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(chapter, key, value)

    chapter.updated_at = datetime.utcnow()

    # 更新字数统计
    if "content" in update_data:
        chapter.word_count = len(update_data["content"])

    await db.flush()
    await db.refresh(chapter)

    return chapter


@router.delete("/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chapter(
    project_id: str,
    chapter_id: str,
    db: Annotated[AsyncSession, Depends(get_chapter_db)],
) -> None:
    """删除章节"""
    result = await db.execute(
        select(Chapter).where(
            Chapter.id == chapter_id,
            Chapter.project_id == project_id,
        )
    )
    chapter = result.scalar_one_or_none()

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter {chapter_id} not found",
        )

    await db.delete(chapter)
    await db.flush()


# ========================
# AI 写作路由
# ========================

@router.post("/{chapter_id}/write")
async def write_chapter(
    project_id: str,
    chapter_id: str,
    request: WritingContinueRequest,
    db: Annotated[AsyncSession, Depends(get_chapter_db)],
    writing_service: Annotated[WritingService, Depends(get_writing_service)],
) -> list[dict]:
    """
    AI 续写章节（多版本）

    返回续写结果列表，供前端选择。
    """
    result = await db.execute(
        select(Chapter).where(
            Chapter.id == chapter_id,
            Chapter.project_id == project_id,
        )
    )
    chapter = result.scalar_one_or_none()

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter {chapter_id} not found",
        )

    # 使用前文内容 + 提供的上下文进行续写
    context = request.context or chapter.content
    results = await writing_service.continue_writing(
        context=context,
        style=request.style,
        num_versions=request.num_versions,
    )

    return results


@router.post("/{chapter_id}/write/stream")
async def write_chapter_stream(
    project_id: str,
    chapter_id: str,
    request: WritingContinueRequest,
    db: Annotated[AsyncSession, Depends(get_chapter_db)],
    writing_service: Annotated[WritingService, Depends(get_writing_service)],
) -> StreamingResponse:
    """
    AI 续写章节（流式返回 SSE）

    前端可以通过 SSE 逐字显示生成内容。
    """
    result = await db.execute(
        select(Chapter).where(
            Chapter.id == chapter_id,
            Chapter.project_id == project_id,
        )
    )
    chapter = result.scalar_one_or_none()

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter {chapter_id} not found",
        )

    context = request.context or chapter.content

    async def event_generator() -> AsyncIterator[str]:
        async for token in writing_service.continue_writing_stream(
            context=context,
            style=request.style,
        ):
            # SSE 格式：data: {token}\n\n
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/{chapter_id}/expand")
async def expand_chapter(
    project_id: str,
    chapter_id: str,
    request: WritingExpandRequest,
    db: Annotated[AsyncSession, Depends(get_chapter_db)],
    writing_service: Annotated[WritingService, Depends(get_writing_service)],
) -> dict:
    """
    AI 扩写章节

    将章节中的某个段落扩写 N 倍。
    """
    result = await db.execute(
        select(Chapter).where(
            Chapter.id == chapter_id,
            Chapter.project_id == project_id,
        )
    )
    chapter = result.scalar_one_or_none()

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter {chapter_id} not found",
        )

    expanded = await writing_service.expand_writing(
        paragraph=request.paragraph,
        expand_ratio=request.expand_ratio,
    )

    return {"original": request.paragraph, "expanded": expanded}


@router.post("/{chapter_id}/rewrite")
async def rewrite_chapter(
    project_id: str,
    chapter_id: str,
    request: WritingRewriteRequest,
    db: Annotated[AsyncSession, Depends(get_chapter_db)],
    writing_service: Annotated[WritingService, Depends(get_writing_service)],
) -> dict:
    """
    AI 改写章节

    支持三种模式：
    - polish: 润色打磨
    - alternative: 完全不同角度的改写
    - tone: 语调转换
    """
    result = await db.execute(
        select(Chapter).where(
            Chapter.id == chapter_id,
            Chapter.project_id == project_id,
        )
    )
    chapter = result.scalar_one_or_none()

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter {chapter_id} not found",
        )

    rewritten = await writing_service.rewrite_writing(
        content=request.content,
        mode=request.mode,
        tone=request.tone,
    )

    return {"original": request.content, "rewritten": rewritten}


@router.post("/{chapter_id}/enhance")
async def enhance_chapter(
    project_id: str,
    chapter_id: str,
    request: WritingEnhanceRequest,
    db: Annotated[AsyncSession, Depends(get_chapter_db)],
    writing_service: Annotated[WritingService, Depends(get_writing_service)],
) -> dict:
    """
    AI 描写增强

    增强内容的感官描写（视觉、听觉、嗅觉、触觉等）。
    """
    result = await db.execute(
        select(Chapter).where(
            Chapter.id == chapter_id,
            Chapter.project_id == project_id,
        )
    )
    chapter = result.scalar_one_or_none()

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter {chapter_id} not found",
        )

    enhanced = await writing_service.enhance_description(
        content=request.content,
        senses=request.senses,
    )

    return {"original": request.content, "enhanced": enhanced}


@router.post("/{chapter_id}/feedback", response_model=WritingFeedbackResponse)
async def feedback_chapter(
    project_id: str,
    chapter_id: str,
    request: WritingFeedbackRequest,
    db: Annotated[AsyncSession, Depends(get_chapter_db)],
    writing_service: Annotated[WritingService, Depends(get_writing_service)],
) -> WritingFeedbackResponse:
    """
    AI 即时反馈

    对章节内容进行评分和反馈。
    """
    result = await db.execute(
        select(Chapter).where(
            Chapter.id == chapter_id,
            Chapter.project_id == project_id,
        )
    )
    chapter = result.scalar_one_or_none()

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter {chapter_id} not found",
        )

    feedback = await writing_service.instant_feedback(
        content=request.content,
        focus_areas=request.focus_areas,
    )

    return WritingFeedbackResponse(**feedback)


# 注意：/dialogue 路由必须在 /{chapter_id} 路由之前定义，
# 否则 "/dialogue" 会被 FastAPI 误匹配为 {chapter_id} = "dialogue"
@router.post("/dialogue")
async def dialogue_write(
    project_id: str,
    request: DialogueWriteRequest,
    writing_service: Annotated[WritingService, Depends(get_writing_service)],
) -> dict:
    """
    对话式写作（彩云小梦式）

    根据角色设定和场景进行对话式创作。
    """
    dialogue = await writing_service.dialogue_write(
        characters=request.characters,
        scene=request.scene,
        last_dialogue=request.last_dialogue,
    )

    return {"dialogue": dialogue}
