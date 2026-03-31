"""AI 插图生成 API"""

from typing import Annotated, AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import get_db_manager
from src.models.character import Character
from src.schemas.image_gen import (
    ImageGenRequest,
    ImageGenResponse,
    CharacterImageRequest,
)
from src.services.image_gen import get_image_gen_service, BaseImageGenService

router = APIRouter()


async def get_project_db(project_id: str) -> AsyncSession:
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


async def get_image_service() -> BaseImageGenService:
    """获取图片生成服务"""
    try:
        return get_image_gen_service()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )


async def get_character_enhanced_prompt(
    project_id: str,
    character_ids: list[str],
    db: AsyncSession
) -> str:
    """获取角色设定增强的 prompt"""
    if not character_ids:
        return ""

    enhanced_parts = []
    for char_id in character_ids:
        result = await db.execute(
            select(Character).where(
                Character.id == char_id,
                Character.project_id == project_id
            )
        )
        character = result.scalar_one_or_none()
        if character:
            parts = [f"角色: {character.name}"]
            if character.personality:
                parts.append(f"性格: {character.personality}")
            if character.background:
                parts.append(f"背景: {character.background}")
            enhanced_parts.append(", ".join(parts))

    return " | ".join(enhanced_parts)


@router.post("/generate", response_model=ImageGenResponse)
async def generate_image(
    project_id: Annotated[str, Path(description="项目ID")],
    request: ImageGenRequest,
    db: Annotated[AsyncSession, Depends(get_project_db)],
    service: Annotated[BaseImageGenService, Depends(get_image_service)],
) -> ImageGenResponse:
    """生成插图

    根据提示词生成插图，支持关联角色设定增强 prompt。

    Args:
        project_id: 项目 ID
        request: 生成请求，包含 prompt, style, size, character_ids 等
        db: 数据库会话
        service: 图片生成服务

    Returns:
        ImageGenResponse: 包含 base64 图片数据或 URL
    """
    try:
        # 如果有关联角色，获取角色设定增强 prompt
        if request.character_ids:
            character_prompt = await get_character_enhanced_prompt(
                project_id, request.character_ids, db
            )
            if character_prompt:
                # 将角色设定加入到主 prompt
                request.prompt = f"{request.prompt}\n\n[角色设定] {character_prompt}"

        # 调用图片生成服务
        result = await service.generate(
            prompt=request.prompt,
            style=request.style,
            size=request.size,
            negative_prompt=request.negative_prompt,
        )

        return ImageGenResponse(
            url=result.get("url", ""),
            b64_json=result.get("b64_json", ""),
            seed=result.get("seed", 0),
            provider=result.get("provider", ""),
        )

    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"图片生成失败: {str(e)}"
        )


@router.post("/characters/{character_id}", response_model=ImageGenResponse)
async def generate_character_image(
    project_id: Annotated[str, Path(description="项目ID")],
    character_id: Annotated[str, Path(description="角色ID")],
    request: CharacterImageRequest,
    db: Annotated[AsyncSession, Depends(get_project_db)],
    service: Annotated[BaseImageGenService, Depends(get_image_service)],
) -> ImageGenResponse:
    """为指定角色生成形象图

    根据角色设定生成角色形象图。

    Args:
        project_id: 项目 ID
        character_id: 角色 ID
        request: 包含 pose, expression 等
        db: 数据库会话
        service: 图片生成服务

    Returns:
        ImageGenResponse: 包含角色形象图
    """
    # 获取角色信息
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
            detail=f"Character {character_id} not found"
        )

    try:
        # 构建角色提示词
        prompt_parts = [f"{character.name}"]

        if character.personality:
            prompt_parts.append(f"personality: {character.personality}")

        # 姿态和表情
        pose_map = {
            "standing": "standing pose",
            "sitting": "sitting pose",
            "action": "action pose, dynamic",
            "dynamic": "dynamic pose, in motion",
        }
        pose_desc = pose_map.get(request.pose, "standing pose")

        expression_map = {
            "neutral": "neutral expression",
            "smiling": "smiling, happy",
            "serious": "serious expression",
            "sad": "sad expression",
            "angry": "angry expression",
            "surprised": "surprised expression",
        }
        expression_desc = expression_map.get(request.expression, "neutral expression")

        prompt_parts.append(pose_desc)
        prompt_parts.append(expression_desc)

        # 如果有外貌描述
        if character.background:
            prompt_parts.append(f"description: {character.background}")

        prompt = ", ".join(filter(None, prompt_parts))

        # 调用图片生成
        result = await service.generate(
            prompt=prompt,
            style="anime",
            size="512x512",
        )

        return ImageGenResponse(
            url=result.get("url", ""),
            b64_json=result.get("b64_json", ""),
            seed=result.get("seed", 0),
            provider=result.get("provider", ""),
        )

    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"角色形象生成失败: {str(e)}"
        )
