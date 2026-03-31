"""项目 CRUD API 路由"""

import json
from datetime import datetime
from typing import Annotated, AsyncIterator

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
) -> AsyncIterator[AsyncSession]:
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


@router.get("/{project_id}/search")
async def search_in_project(
    project_id: str,
    q: Annotated[str, Query(description="搜索关键词")],
    scope: Annotated[str, Query(description="范围：all/chapters/characters/world_settings")] = "all",
):
    """项目内全文检索"""
    from src.core.vector_db import get_vector_db_manager
    import httpx
    from src.core.config import get_settings
    
    results = []
    settings = get_settings()
    
    # 获取项目的数据库路径
    project_dir = settings.home_dir / ".aiwriter" / "projects" / project_id
    
    if not project_dir.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    # 搜索章节
    if scope in ["all", "chapters"]:
        chapters_file = project_dir / "chapters.json"
        if chapters_file.exists():
            with open(chapters_file, "r", encoding="utf-8") as f:
                chapters_data = json.load(f)
                chapters = chapters_data if isinstance(chapters_data, list) else chapters_data.get("items", [])
                
                for chapter in chapters:
                    title = chapter.get("title", "")
                    content = chapter.get("content", "")
                    
                    # 简单关键词匹配
                    if q.lower() in title.lower() or q.lower() in content.lower():
                        # 提取snippet
                        snippet = ""
                        idx = content.lower().find(q.lower())
                        if idx >= 0:
                            start = max(0, idx - 50)
                            end = min(len(content), idx + len(q) + 50)
                            snippet = ("..." if start > 0 else "") + content[start:end] + ("..." if end < len(content) else "")
                        else:
                            snippet = content[:100] + ("..." if len(content) > 100 else "")
                        
                        results.append({
                            "type": "chapter",
                            "id": chapter.get("id"),
                            "title": title,
                            "snippet": snippet,
                            "score": 1.0 if q.lower() in title.lower() else 0.5,
                        })
    
    # 搜索角色
    if scope in ["all", "characters"]:
        characters_file = project_dir / "characters.json"
        if characters_file.exists():
            with open(characters_file, "r", encoding="utf-8") as f:
                characters_data = json.load(f)
                characters = characters_data if isinstance(characters_data, list) else characters_data.get("items", [])
                
                for char in characters:
                    name = char.get("name", "")
                    bio = char.get("bio", "")
                    personality = char.get("personality", "")
                    
                    searchable = f"{name} {bio} {personality}"
                    if q.lower() in searchable.lower():
                        results.append({
                            "type": "character",
                            "id": char.get("id"),
                            "title": name,
                            "snippet": bio[:100] + ("..." if len(bio) > 100 else ""),
                            "score": 1.0 if q.lower() in name.lower() else 0.5,
                        })
    
    # 搜索世界设定（使用 ChromaDB 向量搜索）
    if scope in ["all", "world_settings"]:
        vector_db = get_vector_db_manager()
        
        try:
            collection_name = vector_db._get_collection_name(
                project_id, vector_db.WORLD_SETTINGS_PREFIX
            )
            
            # 获取查询向量
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{settings.llm_base_url}/api/embeddings",
                    json={
                        "model": settings.llm_embedding_model,
                        "prompt": q,
                    },
                )
                resp.raise_for_status()
                query_embedding = resp.json().get("embedding", [])
            
            if query_embedding:
                search_results = vector_db.query_vectors(
                    collection_name=collection_name,
                    query_embedding=query_embedding,
                    n_results=10,
                )
                
                if search_results and search_results.get("ids"):
                    ids = search_results["ids"][0]
                    distances = search_results.get("distances", [[]])[0]
                    documents = search_results.get("documents", [[]])[0]
                    metadatas = search_results.get("metadatas", [[]])[0]
                    
                    for i, ws_id in enumerate(ids):
                        metadata = metadatas[i] if i < len(metadatas) else {}
                        results.append({
                            "type": "world_setting",
                            "id": ws_id,
                            "title": metadata.get("name", "未知设定"),
                            "snippet": documents[i][:100] + ("..." if len(documents[i]) > 100 else ""),
                            "score": 1.0 - distances[i] if i < len(distances) else 0.0,
                        })
        except Exception:
            pass  # 向量搜索失败不影响其他搜索结果
    
    # 按分数排序
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "project_id": project_id,
        "query": q,
        "scope": scope,
        "total": len(results),
        "results": results[:50],  # 最多返回50条
    }
