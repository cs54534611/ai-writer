"""世界设定 API 路由"""

import json
import uuid
from datetime import datetime
from typing import Annotated, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel, Field
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import get_settings
from src.core.database import get_db_manager
from src.core.vector_db import get_vector_db_manager
from src.models.world_setting import WorldSetting, SettingCategory
from src.schemas.world_setting import (
    WorldSettingCreate,
    WorldSettingRead,
    WorldSettingUpdate,
)
from src.services.llm import get_llm_service
from src.services.map_generator import MapGenerator


router = APIRouter()


async def get_setting_db(
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


async def _embed_text(text: str) -> list[float]:
    """获取文本的向量嵌入"""
    settings = get_settings()
    embedding_url = f"{settings.llm_base_url}/api/embeddings"
    embedding_model = settings.llm_embedding_model

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            embedding_url,
            json={
                "model": embedding_model,
                "prompt": text,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("embedding", [])


async def _store_setting_vector(
    project_id: str,
    setting: WorldSetting,
) -> str:
    """
    将世界设定存储到向量数据库

    Returns:
        向量ID
    """
    vector_db = get_vector_db_manager()
    vector_db.init_project_collections(project_id)

    collection_name = vector_db._get_collection_name(
        project_id, vector_db.WORLD_SETTINGS_PREFIX
    )

    # 组合文本用于嵌入
    content_for_embed = f"{setting.name}\n{setting.content}"

    # 获取嵌入向量
    embedding = await _embed_text(content_for_embed)

    # 生成向量ID
    vector_id = f"setting_{setting.id}_{uuid.uuid4().hex[:8]}"

    # 存储
    vector_db.add_vectors(
        collection_name=collection_name,
        ids=[vector_id],
        embeddings=[embedding],
        documents=[content_for_embed],
        metadatas=[{
            "setting_id": setting.id,
            "project_id": project_id,
            "category": setting.category.value if setting.category else None,
            "name": setting.name,
        }],
    )

    return vector_id


async def _update_setting_vector(
    project_id: str,
    setting: WorldSetting,
) -> str:
    """
    更新世界设定在向量数据库中的记录
    """
    vector_db = get_vector_db_manager()

    collection_name = vector_db._get_collection_name(
        project_id, vector_db.WORLD_SETTINGS_PREFIX
    )

    # 删除旧记录
    try:
        collection = vector_db.get_collection(project_id, "world_settings")
        collection.delete(where={"setting_id": setting.id})
    except Exception:
        pass

    # 存储新记录
    return await _store_setting_vector(project_id, setting)


async def _delete_setting_vector(
    project_id: str,
    setting_id: str,
) -> None:
    """从向量数据库删除世界设定"""
    vector_db = get_vector_db_manager()

    try:
        collection = vector_db.get_collection(project_id, "world_settings")
        collection.delete(where={"setting_id": setting_id})
    except Exception:
        pass


@router.post("/", response_model=WorldSettingRead, status_code=status.HTTP_201_CREATED)
async def create_world_setting(
    project_id: str,
    setting_data: WorldSettingCreate,
    db: Annotated[AsyncSession, Depends(get_setting_db)],
) -> WorldSetting:
    """创建设定"""
    setting = WorldSetting(
        project_id=project_id,
        **setting_data.model_dump(),
    )
    db.add(setting)
    await db.flush()
    await db.refresh(setting)

    # 存储到向量数据库
    try:
        await _store_setting_vector(project_id, setting)
    except Exception:
        # 向量存储失败不影响主流程
        pass

    return WorldSettingRead.from_orm_with_relations(setting)


@router.get("/", response_model=list[WorldSettingRead])
async def list_world_settings(
    project_id: str,
    db: Annotated[AsyncSession, Depends(get_setting_db)],
    category: Optional[SettingCategory] = Query(default=None, description="按类别筛选"),
) -> list[WorldSettingRead]:
    """获取设定列表"""
    query = select(WorldSetting).where(WorldSetting.project_id == project_id)

    if category:
        query = query.where(WorldSetting.category == category)

    query = query.order_by(WorldSetting.updated_at.desc())
    result = await db.execute(query)
    settings = result.scalars().all()

    return [WorldSettingRead.from_orm_with_relations(s) for s in settings]


@router.get("/search", response_model=list[WorldSettingRead])
async def search_world_settings(
    project_id: str,
    db: Annotated[AsyncSession, Depends(get_setting_db)],
    query: str = Query(..., description="搜索查询文本"),
    category: Optional[SettingCategory] = Query(default=None, description="按类别筛选"),
    top_k: int = Query(default=5, description="返回结果数量"),
) -> list[WorldSettingRead]:
    """向量相似搜索世界设定"""
    vector_db = get_vector_db_manager()

    collection_name = vector_db._get_collection_name(
        project_id, vector_db.WORLD_SETTINGS_PREFIX
    )

    try:
        # 获取查询向量
        query_embedding = await _embed_text(query)

        # 执行向量搜索
        where_filter = {}
        if category:
            where_filter["category"] = category.value

        results = vector_db.query_vectors(
            collection_name=collection_name,
            query_embedding=query_embedding,
            n_results=top_k,
            where=where_filter if where_filter else None,
        )

        if not results or not results.get("ids") or not results["ids"][0]:
            return []

        # 获取匹配的设定ID
        setting_ids = [
            meta.get("setting_id")
            for meta in results.get("metadatas", [[]])[0]
            if meta.get("setting_id")
        ]

        if not setting_ids:
            return []

        # 从数据库获取完整设定
        query = select(WorldSetting).where(
            WorldSetting.id.in_(setting_ids),
            WorldSetting.project_id == project_id,
        )
        result = await db.execute(query)
        settings = result.scalars().all()

        # 按搜索结果顺序排序
        id_to_setting = {s.id: s for s in settings}
        ordered_settings = [
            id_to_setting[sid] for sid in setting_ids if sid in id_to_setting
        ]

        return [WorldSettingRead.from_orm_with_relations(s) for s in ordered_settings]

    except Exception:
        # 搜索失败时返回空列表
        return []


@router.put("/{setting_id}", response_model=WorldSettingRead)
async def update_world_setting(
    project_id: str,
    setting_id: str,
    setting_data: WorldSettingUpdate,
    db: Annotated[AsyncSession, Depends(get_setting_db)],
) -> WorldSetting:
    """更新设定"""
    result = await db.execute(
        select(WorldSetting).where(
            WorldSetting.id == setting_id,
            WorldSetting.project_id == project_id,
        )
    )
    setting = result.scalar_one_or_none()

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"WorldSetting {setting_id} not found",
        )

    update_data = setting_data.model_dump(exclude_unset=True)

    # 处理 related_setting_ids
    if "related_setting_ids" in update_data:
        related_ids = update_data.pop("related_setting_ids")
        if related_ids is not None:
            setting.set_related_setting_ids(related_ids)

    for key, value in update_data.items():
        setattr(setting, key, value)

    setting.updated_at = datetime.utcnow()
    await db.flush()
    await db.refresh(setting)

    # 更新向量数据库
    try:
        await _update_setting_vector(project_id, setting)
    except Exception:
        pass

    return WorldSettingRead.from_orm_with_relations(setting)


@router.delete("/{setting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_world_setting(
    project_id: str,
    setting_id: str,
    db: Annotated[AsyncSession, Depends(get_setting_db)],
) -> None:
    """删除设定"""
    result = await db.execute(
        select(WorldSetting).where(
            WorldSetting.id == setting_id,
            WorldSetting.project_id == project_id,
        )
    )
    setting = result.scalar_one_or_none()

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"WorldSetting {setting_id} not found",
        )

    await db.delete(setting)
    await db.flush()

    # 从向量数据库删除
    try:
        await _delete_setting_vector(project_id, setting_id)
    except Exception:
        pass


class MapGenerateRequest(BaseModel):
    """AI 生成世界地图请求"""
    genre: str = Field(
        default="玄幻",
        description="题材类型（修仙/都市/玄幻/穿越/科幻/奇幻）"
    )
    settings: list[dict] = Field(
        default=[],
        description="已有世界设定列表"
    )


@router.post("/maps/generate")
async def generate_world_map(
    project_id: str,
    map_request: MapGenerateRequest,
    db: Annotated[AsyncSession, Depends(get_setting_db)],
) -> dict:
    """
    AI 生成世界地图结构
    
    根据题材类型和已有设定，生成包含三个层级的世界地图：
    - 上层空间（天界/仙界/神域）
    - 中层空间（人间/世俗界）
    - 下层空间（冥界/地狱/深渊）
    """
    llm = get_llm_service()
    generator = MapGenerator(llm)
    
    result = await generator.generate_world_map(
        genre=map_request.genre,
        settings=map_request.settings,
    )
    
    return result
