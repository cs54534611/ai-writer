"""导入导出 API 路由"""

from typing import Annotated, Union

from fastapi import APIRouter, Depends, HTTPException, Query, Path, UploadFile, File, Body
from fastapi.responses import StreamingResponse, JSONResponse

from src.services.export_import import get_export_import_service

router = APIRouter()


@router.get("/projects/{project_id}/export")
async def export_project(
    project_id: Annotated[str, Path(description="项目ID")],
    format: Annotated[str, Query(description="导出格式: json, markdown, zip")] = "json",
):
    """
    导出项目数据
    
    - format=json: 返回 JSON 数据
    - format=markdown: 返回 Markdown 文件流
    - format=zip: 返回 ZIP 文件流
    """
    service = get_export_import_service()
    
    if format not in ("json", "markdown", "zip"):
        raise HTTPException(
            status_code=400,
            detail="format must be one of: json, markdown, zip",
        )

    result = await service.export_project(project_id, format)
    
    if not result.get("success", False):
        return JSONResponse(
            status_code=400,
            content=result,
        )

    if format == "zip":
        zip_data = result["data"]
        return StreamingResponse(
            iter([zip_data]),
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{result["filename"]}"',
            },
        )
    else:
        return JSONResponse(content=result)


@router.post("/projects/{project_id}/import")
async def import_project(
    project_id: Annotated[str, Path(description="项目ID")],
    file: UploadFile | None = None,
    json_data: dict | None = Body(default=None, description="JSON 格式的导入数据"),
    format: Annotated[str, Query(description="导入格式: json, zip")] = "json",
):
    """
    导入项目数据
    
    支持两种方式:
    1. 上传文件 (multipart/form-data)
    2. 直接提交 JSON 数据 (body)
    """
    service = get_export_import_service()
    
    if format not in ("json", "zip"):
        raise HTTPException(
            status_code=400,
            detail="format must be one of: json, zip",
        )

    file_data = None
    
    # 从上传文件读取
    if file:
        contents = await file.read()
        file_data = contents
    elif json_data:
        import json
        file_data = json.dumps(json_data).encode("utf-8")
    else:
        raise HTTPException(
            status_code=400,
            detail="请提供要导入的文件或 JSON 数据",
        )

    result = await service.import_project(file_data, format)
    
    if not result.get("success", False):
        return JSONResponse(
            status_code=400,
            content=result,
        )

    return result


@router.post("/projects/{project_id}/chapters/import-folder")
async def import_chapters_from_folder(
    project_id: Annotated[str, Path(description="项目ID")],
    folder_path: Annotated[str, Body(description="包含 Markdown 文件的文件夹路径")],
):
    """
    从文件夹批量导入章节
    
    文件夹中的 .md 和 .markdown 文件会被导入为章节
    """
    service = get_export_import_service()
    
    result = await service.import_chapters_from_folder(project_id, folder_path)
    
    if not result.get("success", False):
        return JSONResponse(
            status_code=400,
            content=result,
        )

    return result


@router.get("/chapters/{chapter_id}/export-markdown")
async def export_chapter_markdown(
    chapter_id: Annotated[str, Path(description="章节ID")],
):
    """
    导出单个章节为 Markdown 格式
    """
    service = get_export_import_service()
    
    result = await service.export_chapter_markdown(chapter_id)
    
    if not result.get("success", False):
        return JSONResponse(
            status_code=400,
            content=result,
        )

    return JSONResponse(content=result)


@router.get("/chapters/{chapter_id}/export-text")
async def export_chapter_text(
    chapter_id: Annotated[str, Path(description="章节ID")],
):
    """
    导出单个章节为纯文本 TXT（去除 Markdown 格式）
    """
    service = get_export_import_service()
    
    result = await service.export_chapter_as_text(chapter_id)
    
    if not result.get("success", False):
        return JSONResponse(
            status_code=400,
            content=result,
        )

    return JSONResponse(content=result)


@router.get("/chapters/{chapter_id}/export-json")
async def export_chapter_json(
    chapter_id: Annotated[str, Path(description="章节ID")],
):
    """
    导出单个章节为结构化 JSON 格式
    """
    service = get_export_import_service()
    
    result = await service.export_chapter_as_json(chapter_id)
    
    if not result.get("success", False):
        return JSONResponse(
            status_code=400,
            content=result,
        )

    return JSONResponse(content=result)


@router.get("/projects/{project_id}/world-settings/export")
async def export_world_settings(
    project_id: Annotated[str, Path(description="项目ID")],
    format: Annotated[str, Query(description="导出格式: md, json")] = "md",
):
    """
    导出项目设定集
    
    - format=md: 返回 Markdown 格式（按类别分组）
    - format=json: 返回 JSON 格式
    """
    service = get_export_import_service()
    
    if format not in ("md", "json"):
        raise HTTPException(
            status_code=400,
            detail="format must be one of: md, json",
        )
    
    result = await service.export_world_settings(project_id, format)
    
    if not result.get("success", False):
        return JSONResponse(
            status_code=400,
            content=result,
        )
    
    return JSONResponse(content=result)
