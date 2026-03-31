"""独立写作 API - 不需要 chapter_id 的写作接口"""

import json
from typing import Annotated, AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from src.schemas.chapter import (
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


def get_writing_service() -> WritingService:
    """获取写作服务实例"""
    llm = get_llm_service()
    return WritingService(llm)


@router.post("/continue")
async def writing_continue(
    project_id: str,
    request: WritingContinueRequest,
    writing_service: Annotated[WritingService, Depends(get_writing_service)],
) -> list[dict]:
    """
    AI 续写（独立接口，不需要 chapter_id）

    直接传入前文上下文进行续写，返回多个版本供选择。
    """
    results = await writing_service.continue_writing(
        context=request.context,
        style=request.style,
        num_versions=request.num_versions,
    )

    return results


@router.post("/continue/stream")
async def writing_continue_stream(
    project_id: str,
    request: WritingContinueRequest,
    writing_service: Annotated[WritingService, Depends(get_writing_service)],
) -> StreamingResponse:
    """
    AI 续写（流式返回 SSE）

    前端可以通过 SSE 逐字显示生成内容。
    """
    async def event_generator() -> AsyncIterator[str]:
        async for token in writing_service.continue_writing_stream(
            context=request.context,
            style=request.style,
        ):
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


@router.post("/expand")
async def writing_expand(
    project_id: str,
    request: WritingExpandRequest,
    writing_service: Annotated[WritingService, Depends(get_writing_service)],
) -> dict:
    """
    AI 扩写（独立接口）

    将段落扩写 N 倍。
    """
    expanded = await writing_service.expand_writing(
        paragraph=request.paragraph,
        expand_ratio=request.expand_ratio,
    )

    return {"original": request.paragraph, "expanded": expanded}


@router.post("/rewrite")
async def writing_rewrite(
    project_id: str,
    request: WritingRewriteRequest,
    writing_service: Annotated[WritingService, Depends(get_writing_service)],
) -> dict:
    """
    AI 改写（独立接口）

    支持三种模式：polish（润色）/ alternative（换角度）/ tone（语调）
    """
    rewritten = await writing_service.rewrite_writing(
        content=request.content,
        mode=request.mode,
        tone=request.tone,
    )

    return {"original": request.content, "rewritten": rewritten}


@router.post("/enhance")
async def writing_enhance(
    project_id: str,
    request: WritingEnhanceRequest,
    writing_service: Annotated[WritingService, Depends(get_writing_service)],
) -> dict:
    """
    AI 描写增强（独立接口）

    增强内容的感官描写。
    """
    enhanced = await writing_service.enhance_description(
        content=request.content,
        senses=request.senses,
    )

    return {"original": request.content, "enhanced": enhanced}


@router.post("/feedback", response_model=WritingFeedbackResponse)
async def writing_feedback(
    project_id: str,
    request: WritingFeedbackRequest,
    writing_service: Annotated[WritingService, Depends(get_writing_service)],
) -> WritingFeedbackResponse:
    """
    AI 即时反馈（独立接口）

    对内容进行评分和反馈。
    """
    feedback = await writing_service.instant_feedback(
        content=request.content,
        focus_areas=request.focus_areas,
    )

    return WritingFeedbackResponse(**feedback)
