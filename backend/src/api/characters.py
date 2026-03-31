"""Character CRUD API 路由"""

import json
import uuid
from datetime import datetime
from typing import Annotated, AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Query, status, Path, Body
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import get_db_manager
from src.core.vector_db import get_vector_db_manager
from src.models.character import Character
from src.schemas.character import (
    CharacterCreate,
    CharacterUpdate,
    CharacterRead,
    CharacterListResponse,
)

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


async def _extract_character_profile_embedding(character_data: dict) -> list[float]:
    """调用 LLM 提取角色特征 embedding"""
    from src.services.llm import get_llm_service
    
    # 构建角色描述文本
    profile_text = f"""
角色名称: {character_data.get('name', '')}
性别: {character_data.get('gender', '未知')}
年龄: {character_data.get('age', '未知')}
职业: {character_data.get('occupation', '未知')}
性格: {character_data.get('personality', '未知')}
外貌: {character_data.get('appearance', '未知')}
背景: {character_data.get('background', '未知')}
目标: {character_data.get('goals', '未知')}
关系: {character_data.get('relationships', '未知')}
简介: {character_data.get('bio', '')}
"""
    
    llm = get_llm_service()
    # 使用 embedding API 获取向量
    # 假设 LLM 服务有 generate 方法，我们用它来提取特征描述，再用描述获取 embedding
    # 这里简化处理，实际可以调用专门的 embedding 服务
    description = await llm.generate(
        f"请用一段话描述以下角色的核心特征，用于相似度匹配。只输出特征描述：\n{profile_text}"
    )
    
    # 获取 embedding（通过 httpx 直接调用 embedding API）
    import httpx
    from src.core.config import get_settings
    settings = get_settings()
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{settings.llm_base_url}/api/embeddings",
            json={
                "model": settings.llm_embedding_model,
                "prompt": description,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("embedding", [])


async def _store_character_profile(project_id: str, character_id: str, character_data: dict) -> None:
    """存储角色特征向量到 ChromaDB"""
    vector_db = get_vector_db_manager()
    vector_db.init_project_collections(project_id)
    
    collection_name = vector_db._get_collection_name(
        project_id, vector_db.CHARACTER_PROFILES_PREFIX
    )
    
    # 提取特征向量
    embedding = await _extract_character_profile_embedding(character_data)
    
    # 构建文档内容
    profile_doc = json.dumps({
        "name": character_data.get("name", ""),
        "gender": character_data.get("gender", ""),
        "age": character_data.get("age", ""),
        "occupation": character_data.get("occupation", ""),
        "personality": character_data.get("personality", ""),
        "appearance": character_data.get("appearance", ""),
        "background": character_data.get("background", ""),
        "goals": character_data.get("goals", ""),
        "bio": character_data.get("bio", ""),
    }, ensure_ascii=False)
    
    # 存储向量
    vector_db.add_vectors(
        collection_name=collection_name,
        ids=[character_id],
        embeddings=[embedding],
        documents=[profile_doc],
        metadatas=[{"character_id": character_id, "project_id": project_id}],
    )


@router.post("/", response_model=CharacterRead, status_code=status.HTTP_201_CREATED)
async def create_character(
    project_id: Annotated[str, Path(description="项目ID")],
    character_data: CharacterCreate,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> Character:
    """创建新角色"""
    character = Character(
        project_id=project_id,
        **character_data.model_dump()
    )
    db.add(character)
    await db.flush()
    await db.refresh(character)
    
    # 存储角色特征向量
    try:
        await _store_character_profile(project_id, character.id, character_data.model_dump())
    except Exception:
        # 向量存储失败不影响角色创建
        pass
    
    return character


@router.get("/", response_model=CharacterListResponse)
async def list_characters(
    project_id: Annotated[str, Path(description="项目ID")],
    db: Annotated[AsyncSession, Depends(get_project_db)],
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
) -> CharacterListResponse:
    """获取角色列表（分页）"""
    # 获取总数（使用 COUNT 而非全量查询）
    from sqlmodel import func
    count_query = select(func.count()).select_from(Character).where(Character.project_id == project_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    # 分页查询
    offset = (page - 1) * page_size
    query = (
        select(Character)
        .where(Character.project_id == project_id)
        .order_by(Character.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    characters = result.scalars().all()
    
    return CharacterListResponse(
        items=list(characters),
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{character_id}", response_model=CharacterRead)
async def get_character(
    project_id: Annotated[str, Path(description="项目ID")],
    character_id: Annotated[str, Path(description="角色ID")],
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> Character:
    """获取单个角色"""
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
            detail=f"Character {character_id} not found",
        )
    
    return character


@router.put("/{character_id}", response_model=CharacterRead)
async def update_character(
    project_id: Annotated[str, Path(description="项目ID")],
    character_id: Annotated[str, Path(description="角色ID")],
    character_data: CharacterUpdate,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> Character:
    """更新角色"""
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
            detail=f"Character {character_id} not found",
        )
    
    update_data = character_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(character, key, value)
    
    character.updated_at = datetime.utcnow()
    await db.flush()
    await db.refresh(character)
    
    # 更新角色特征向量
    try:
        await _store_character_profile(project_id, character_id, character_data.model_dump(exclude_unset=True))
    except Exception:
        # 向量存储失败不影响角色更新
        pass
    
    return character


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(
    project_id: Annotated[str, Path(description="项目ID")],
    character_id: Annotated[str, Path(description="角色ID")],
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> None:
    """删除角色"""
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
            detail=f"Character {character_id} not found",
        )
    
    await db.delete(character)
    await db.flush()


@router.get("/{character_id}/profile")
async def get_character_profile(
    project_id: Annotated[str, Path(description="项目ID")],
    character_id: Annotated[str, Path(description="角色ID")],
    db: Annotated[AsyncSession, Depends(get_project_db)],
):
    """获取角色特征向量摘要"""
    # 先获取角色基本信息
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
            detail=f"Character {character_id} not found",
        )
    
    # 从 ChromaDB 获取向量摘要
    vector_db = get_vector_db_manager()
    collection_name = vector_db._get_collection_name(
        project_id, vector_db.CHARACTER_PROFILES_PREFIX
    )
    
    try:
        collection = vector_db.get_collection(project_id, "character_profiles")
        results = collection.get(
            where={"character_id": character_id},
            limit=1,
        )
        
        if results and results.get("documents"):
            return {
                "character_id": character_id,
                "profile_summary": json.loads(results["documents"][0]),
                "has_vector": True,
            }
    except Exception:
        pass
    
    # 如果没有向量数据，返回基本信息
    return {
        "character_id": character_id,
        "profile_summary": {
            "name": character.name,
            "gender": character.gender,
            "age": character.age,
            "occupation": character.occupation,
            "personality": character.personality,
            "bio": character.bio,
        },
        "has_vector": False,
    }


@router.post("/similar")
async def find_similar_characters(
    project_id: Annotated[str, Path(description="项目ID")],
    character_id: Annotated[str, Path(description="目标角色ID")],
    db: Annotated[AsyncSession, Depends(get_project_db)],
    top_k: int = Query(default=5, ge=1, le=20, description="返回相似角色数量"),
):
    """查找与指定角色相似的其他角色"""
    import httpx
    from src.core.config import get_settings
    
    # 获取目标角色
    result = await db.execute(
        select(Character).where(
            Character.id == character_id,
            Character.project_id == project_id
        )
    )
    target_character = result.scalar_one_or_none()
    
    if not target_character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {character_id} not found",
        )
    
    vector_db = get_vector_db_manager()
    collection_name = vector_db._get_collection_name(
        project_id, vector_db.CHARACTER_PROFILES_PREFIX
    )
    
    settings = get_settings()
    
    try:
        # 获取目标角色的向量
        collection = vector_db.get_collection(project_id, "character_profiles")
        results = collection.get(
            where={"character_id": character_id},
            limit=1,
        )
        
        if not results or not results.get("embeddings"):
            # 如果没有向量，尝试重新提取
            embedding = await _extract_character_profile_embedding(target_character.__dict__)
            if not embedding:
                return {
                    "success": False,
                    "error": "角色特征向量不存在",
                    "similar_characters": [],
                }
        else:
            embedding = results["embeddings"][0]
        
        # 搜索相似角色
        search_results = collection.query(
            query_embeddings=[embedding],
            n_results=top_k + 1,  # 多取一个，因为可能包含自身
            where_document=None,
        )
        
        similar_characters = []
        if search_results and search_results.get("ids"):
            ids = search_results["ids"][0]
            distances = search_results.get("distances", [[]])[0]
            documents = search_results.get("documents", [[]])[0]
            
            for i, cid in enumerate(ids):
                if cid == character_id:
                    continue  # 跳过自身
                if len(similar_characters) >= top_k:
                    break
                    
                # 获取角色详情
                char_result = await db.execute(
                    select(Character).where(Character.id == cid)
                )
                char = char_result.scalar_one_or_none()
                if char:
                    similar_characters.append({
                        "character_id": cid,
                        "name": char.name,
                        "similarity_score": 1.0 - distances[i] if i < len(distances) else 0.0,
                        "profile": json.loads(documents[i]) if i < len(documents) else None,
                    })
        
        return {
            "success": True,
            "target_character": {
                "id": character_id,
                "name": target_character.name,
            },
            "similar_characters": similar_characters,
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "similar_characters": [],
        }
