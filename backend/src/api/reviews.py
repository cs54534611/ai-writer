"""审查 API 路由 - 矛盾检测/OOC/敏感词"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.api.chapters import get_chapter_db
from src.models.character import Character
from src.schemas.review import (
    ChapterReviewRequest,
    ContradictionCheckRequest,
    FullReviewRequest,
    OOCCheckRequest,
    ReviewIssueSchema,
    ReviewResultSchema,
    SensitiveWordCheckRequest,
)
from src.services.review import ReviewService, get_review_service


router = APIRouter()


def get_review_svc() -> ReviewService:
    """获取审查服务实例"""
    return get_review_service()


async def get_project_characters(
    project_id: str,
    db: AsyncSession,
) -> list[dict]:
    """获取项目的所有角色设定"""
    result = await db.execute(
        select(Character).where(Character.project_id == project_id)
    )
    characters = result.scalars().all()
    return [char.model_dump() for char in characters]


# ========================
# 审查 API 路由
# ========================

@router.post("/chapter", response_model=ReviewResultSchema)
async def review_chapter(
    project_id: Annotated[str, Path(description="项目ID")],
    request: ChapterReviewRequest,
    db: Annotated[AsyncSession, Depends(get_chapter_db)],
    review_service: Annotated[ReviewService, Depends(get_review_svc)],
) -> ReviewResultSchema:
    """
    综合审查章节

    审查内容：敏感词检测 + OOC检测 + 矛盾检测
    """
    # 获取角色设定列表
    characters = await get_project_characters(project_id, db)
    
    # 世界设定（暂不获取，留空）
    world_settings: list[dict] = []

    result = await review_service.review_chapter(
        project_id=project_id,
        chapter_content=request.chapter_content,
        characters=characters,
        world_settings=world_settings,
    )

    return ReviewResultSchema(**result)


@router.post("/contradictions", response_model=list[ReviewIssueSchema])
async def check_contradictions(
    project_id: Annotated[str, Path(description="项目ID")],
    request: ContradictionCheckRequest,
    review_service: Annotated[ReviewService, Depends(get_review_svc)],
) -> list[ReviewIssueSchema]:
    """
    检测前后矛盾

    检测类型：
    - 人物特征矛盾（年龄/外貌/性别）
    - 关系状态矛盾（敌人→朋友无过渡）
    - 时间线矛盾
    - 物品/能力矛盾
    """
    issues = await review_service.detect_contradictions(
        project_id=project_id,
        new_content=request.new_content,
        existing_content=request.existing_content,
    )

    return [ReviewIssueSchema(**issue) for issue in issues]


@router.post("/ooc", response_model=list[ReviewIssueSchema])
async def check_ooc(
    project_id: Annotated[str, Path(description="项目ID")],
    request: OOCCheckRequest,
    db: Annotated[AsyncSession, Depends(get_chapter_db)],
    review_service: Annotated[ReviewService, Depends(get_review_svc)],
) -> list[ReviewIssueSchema]:
    """
    检测角色 OOC（Out Of Character）

    AI 分析角色言行是否与性格设定不符
    """
    # 根据 character_id 获取角色设定
    result = await db.execute(
        select(Character).where(
            Character.id == request.character_id,
            Character.project_id == project_id,
        )
    )
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {request.character_id} not found",
        )

    issues = await review_service.detect_ooc(
        content=request.content,
        character=character.model_dump(),
    )

    return [ReviewIssueSchema(**issue) for issue in issues]


@router.post("/sensitive", response_model=list[ReviewIssueSchema])
async def check_sensitive_words(
    project_id: Annotated[str, Path(description="项目ID")],
    request: SensitiveWordCheckRequest,
    review_service: Annotated[ReviewService, Depends(get_review_svc)],
) -> list[ReviewIssueSchema]:
    """
    敏感词/合规检测

    检测类型：
    - 涉政词汇
    - 涉黄词汇
    - 涉暴词汇
    - 自定义敏感词
    """
    issues = await review_service.check_sensitive_words(
        content=request.content,
        custom_words=request.custom_words,
    )

    return [ReviewIssueSchema(**issue) for issue in issues]


@router.post("/full", response_model=ReviewResultSchema)
async def full_review(
    project_id: Annotated[str, Path(description="项目ID")],
    request: FullReviewRequest,
    db: Annotated[AsyncSession, Depends(get_chapter_db)],
    review_service: Annotated[ReviewService, Depends(get_review_svc)],
) -> ReviewResultSchema:
    """
    全量审查章节

    根据章节ID获取内容后进行完整审查
    """
    # 获取章节内容
    from src.models.chapter import Chapter
    result = await db.execute(
        select(Chapter).where(
            Chapter.id == request.chapter_id,
            Chapter.project_id == project_id,
        )
    )
    chapter = result.scalar_one_or_none()

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter {request.chapter_id} not found",
        )

    if not chapter.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chapter has no content to review",
        )

    # 获取角色设定
    characters = await get_project_characters(project_id, db)
    world_settings: list[dict] = []

    result = await review_service.review_chapter(
        project_id=project_id,
        chapter_content=chapter.content,
        characters=characters,
        world_settings=world_settings,
    )

    return ReviewResultSchema(**result)
