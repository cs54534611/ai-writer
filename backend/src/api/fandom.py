"""同人创作 API"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import get_db_manager
from src.schemas.image_gen import (
    FandomImportRequest,
    FandomImportResult,
    FandomOutlineRequest,
    FandomOutlineResult,
)
from src.services.fandom import FandomService
from src.services.llm import get_llm_service, BaseLLMService

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


async def get_fandom_service() -> FandomService:
    """获取同人创作服务"""
    llm = get_llm_service()
    return FandomService(llm)


@router.post("/import", response_model=FandomImportResult)
async def import_fandom_settings(
    project_id: Annotated[str, Path(description="项目ID")],
    request: FandomImportRequest,
    service: Annotated[FandomService, Depends(get_fandom_service)],
) -> FandomImportResult:
    """导入同人创作设定

    分析原文小说文本，提取：
    - 主要角色及关系
    - 世界观设定
    - 叙事风格
    - 创作建议

    Args:
        project_id: 项目 ID
        request: 包含 source_text, source_title 等
        service: 同人创作服务

    Returns:
        FandomImportResult: 提取的角色/世界观/风格等信息
    """
    try:
        result = await service.import_fandom_settings(
            project_id=project_id,
            source_text=request.source_text,
            source_title=request.source_title,
            fandom_domain=request.fandom_domain,
        )

        # 如果有解析错误，记录但不中断
        error_info = result.pop("_error", None)
        raw_info = result.pop("_raw", None)

        return FandomImportResult(
            characters=result.get("characters", []),
            relationships=result.get("relationships", []),
            world_settings=result.get("world_settings", []),
            narrative_style=result.get("narrative_style", ""),
            writing_suggestions=result.get("writing_suggestions", []),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"同人设定导入失败: {str(e)}"
        )


@router.post("/outline", response_model=FandomOutlineResult)
async def generate_fandom_outline(
    project_id: Annotated[str, Path(description="项目ID")],
    request: FandomOutlineRequest,
    service: Annotated[FandomService, Depends(get_fandom_service)],
) -> FandomOutlineResult:
    """生成同人创作大纲

    为同人创作生成详细的大纲建议。

    Args:
        project_id: 项目 ID
        request: 包含 fandom_name, character_ids, relationship_summary 等
        service: 同人创作服务

    Returns:
        FandomOutlineResult: 大纲建议
    """
    try:
        result = await service.generate_fandom_outline(
            project_id=project_id,
            fandom_name=request.fandom_name,
            character_ids=request.character_ids,
            relationship_summary=request.relationship_summary,
            genre=request.genre,
            tone=request.tone,
        )

        # 提取并清理错误信息
        error_info = result.pop("_error", None)
        raw_info = result.pop("_raw", None)

        return FandomOutlineResult(
            outline_title=result.get("outline_title", request.fandom_name),
            premise=result.get("premise", ""),
            chapters=result.get("chapters", []),
            suggested_pairings=result.get("suggested_pairings", []),
            warnings=result.get("warnings", []),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"大纲生成失败: {str(e)}"
        )
