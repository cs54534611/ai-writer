"""ChromaDB 向量数据库管理器 - 支持多项目 collection 管理"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import Optional

from src.core.config import get_settings


class ChromaDBManager:
    """ChromaDB 向量数据库管理器"""

    # Collection 名称前缀
    WORLD_SETTINGS_PREFIX = "project_{}_world_settings"
    CHAPTERS_PREFIX = "project_{}_chapters"
    CHARACTER_PROFILES_PREFIX = "project_{}_character_profiles"

    def __init__(self):
        self._client: Optional[chromadb.PersistentClient] = None
        self._initialized = False

    def _ensure_init(self) -> None:
        """确保客户端已初始化"""
        if not self._initialized:
            settings = get_settings()
            chroma_path = str(settings.get_chroma_path())
            self._client = chromadb.PersistentClient(
                path=chroma_path,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                )
            )
            self._initialized = True

    def _get_collection_name(self, project_id: str, collection_type: str) -> str:
        """获取 collection 名称"""
        return collection_type.format(project_id)

    def init_project_collections(self, project_id: str) -> None:
        """
        为项目初始化 3 个 collection

        Args:
            project_id: 项目ID
        """
        self._ensure_init()

        # World Settings collection
        world_name = self._get_collection_name(
            project_id, self.WORLD_SETTINGS_PREFIX
        )
        # Chapters collection
        chapters_name = self._get_collection_name(
            project_id, self.CHAPTERS_PREFIX
        )
        # Character Profiles collection
        characters_name = self._get_collection_name(
            project_id, self.CHARACTER_PROFILES_PREFIX
        )

        # 创建或获取 collection
        for name in [world_name, chapters_name, characters_name]:
            try:
                self._client.get_or_create_collection(
                    name=name,
                    metadata={"project_id": project_id}
                )
            except Exception:
                # Collection 已存在，忽略
                pass

    def get_collection(
        self,
        project_id: str,
        collection_name: str,
    ) -> chromadb.Collection:
        """
        获取项目的 collection

        Args:
            project_id: 项目ID
            collection_name: collection 类型 (world_settings/chapters/character_profiles)

        Returns:
            chromadb.Collection
        """
        self._ensure_init()

        if collection_name == "world_settings":
            full_name = self._get_collection_name(project_id, self.WORLD_SETTINGS_PREFIX)
        elif collection_name == "chapters":
            full_name = self._get_collection_name(project_id, self.CHAPTERS_PREFIX)
        elif collection_name == "character_profiles":
            full_name = self._get_collection_name(
                project_id, self.CHARACTER_PROFILES_PREFIX
            )
        else:
            full_name = collection_name

        return self._client.get_collection(name=full_name)

    def add_vectors(
        self,
        collection_name: str,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: Optional[list[dict]] = None,
    ) -> None:
        """
        添加向量数据

        Args:
            collection_name: collection 名称
            ids: 向量ID列表
            embeddings: 向量列表
            documents: 文档内容列表
            metadatas: 元数据列表（可选）
        """
        self._ensure_init()
        collection = self._client.get_collection(name=collection_name)

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def query_vectors(
        self,
        collection_name: str,
        query_embedding: list[float],
        n_results: int = 5,
        where: Optional[dict] = None,
        where_document: Optional[dict] = None,
    ) -> dict:
        """
        查询相似向量

        Args:
            collection_name: collection 名称
            query_embedding: 查询向量
            n_results: 返回结果数量
            where: 元数据过滤条件
            where_document: 文档内容过滤条件

        Returns:
            查询结果 {ids, distances, documents, metadatas, embeddings}
        """
        self._ensure_init()
        collection = self._client.get_collection(name=collection_name)

        return collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            where_document=where_document,
        )

    def delete_project_vectors(self, project_id: str) -> None:
        """
        删除项目的所有向量数据

        Args:
            project_id: 项目ID
        """
        self._ensure_init()

        # 删除 3 个 collection
        for prefix in [
            self.WORLD_SETTINGS_PREFIX,
            self.CHAPTERS_PREFIX,
            self.CHARACTER_PROFILES_PREFIX,
        ]:
            collection_name = self._get_collection_name(project_id, prefix)
            try:
                self._client.delete_collection(name=collection_name)
            except Exception:
                # Collection 不存在，忽略
                pass

    def close(self) -> None:
        """关闭客户端"""
        if self._client:
            self._client = None
            self._initialized = False


# 全局 ChromaDB 管理器实例
_vector_db_manager: ChromaDBManager | None = None


def get_vector_db_manager() -> ChromaDBManager:
    """获取全局 ChromaDB 管理器"""
    global _vector_db_manager
    if _vector_db_manager is None:
        _vector_db_manager = ChromaDBManager()
    return _vector_db_manager
