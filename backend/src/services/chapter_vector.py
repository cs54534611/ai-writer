"""章节内容向量服务 - 章节分块、向量化存储、相似搜索"""

import re
import uuid
from typing import Optional

import httpx

from src.core.config import get_settings
from src.core.vector_db import get_vector_db_manager


class ChapterVectorService:
    """章节向量服务"""

    # Collection 名称
    CHAPTERS_COLLECTION = "chapters"

    # 中文句子分割标点
    SENTENCE_DELIMITERS = "。！？"

    def __init__(self):
        self._settings = get_settings()
        self._embedding_url = f"{self._settings.llm_base_url}/api/embeddings"
        self._embedding_model = self._settings.llm_embedding_model

    async def _get_embedding(self, text: str) -> list[float]:
        """
        获取文本的向量嵌入

        Args:
            text: 文本内容

        Returns:
            向量列表
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                self._embedding_url,
                json={
                    "model": self._embedding_model,
                    "prompt": text,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("embedding", [])

    def chunk_chapter_content(
        self,
        content: str,
        chunk_size: int = 500,
    ) -> list[dict]:
        """
        将章节内容分块

        使用中文句子分割（按 。！？ 分割），然后合并到指定大小

        Args:
            content: 章节内容
            chunk_size: 每个块的目标大小（字符数）

        Returns:
            分块列表，每个包含 {text, start_pos, end_pos}
        """
        if not content or not content.strip():
            return []

        chunks = []
        current_chunk = ""
        current_start = 0

        # 按句子分割
        pattern = f"[{self.SENTENCE_DELIMITERS}]"
        sentences = re.split(pattern, content)

        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue

            # 句子结束标点
            if i < len(sentences):
                sentence_end = content.find(sentence, current_start)
                if sentence_end >= 0:
                    sentence = sentence + content[sentence_end + len(sentence)]

            # 检查是否需要开始新块
            if current_chunk and (
                len(current_chunk) + len(sentence) > chunk_size
            ):
                # 保存当前块
                chunks.append({
                    "text": current_chunk.strip(),
                    "start_pos": current_start,
                    "end_pos": current_start + len(current_chunk),
                })
                # 开始新块
                current_chunk = sentence
                current_start = content.find(sentence)
            else:
                if current_chunk:
                    current_chunk += sentence
                else:
                    current_chunk = sentence
                    current_start = content.find(sentence)

        # 保存最后一个块
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "start_pos": current_start,
                "end_pos": current_start + len(current_chunk),
            })

        return chunks

    async def embed_and_store(
        self,
        project_id: str,
        chapter_id: str,
        content: str,
    ) -> list[str]:
        """
        将章节内容分块、向量化并存储到 ChromaDB

        Args:
            project_id: 项目ID
            chapter_id: 章节ID
            content: 章节内容

        Returns:
            存储的块ID列表
        """
        vector_db = get_vector_db_manager()

        # 初始化项目的 collection
        vector_db.init_project_collections(project_id)

        # 分块
        chunks = self.chunk_chapter_content(content)

        if not chunks:
            return []

        # 获取 collection 名称
        collection_name = vector_db._get_collection_name(
            project_id, vector_db.CHAPTERS_PREFIX
        )

        # 向量化和存储
        chunk_ids = []
        embeddings = []
        documents = []
        metadatas = []

        for chunk in chunks:
            chunk_id = f"{chapter_id}_{uuid.uuid4().hex[:8]}"
            chunk_ids.append(chunk_id)
            documents.append(chunk["text"])
            metadatas.append({
                "chapter_id": chapter_id,
                "project_id": project_id,
                "start_pos": chunk["start_pos"],
                "end_pos": chunk["end_pos"],
            })

            # 获取 embedding
            embedding = await self._get_embedding(chunk["text"])
            embeddings.append(embedding)

        # 批量存储
        vector_db.add_vectors(
            collection_name=collection_name,
            ids=chunk_ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

        return chunk_ids

    async def search_similar_chapters(
        self,
        project_id: str,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        """
        搜索最相似的章节片段

        Args:
            project_id: 项目ID
            query: 查询文本
            top_k: 返回结果数量

        Returns:
            相似片段列表，每个包含 {chunk_id, chapter_id, text, distance, metadata}
        """
        vector_db = get_vector_db_manager()

        # 获取 collection 名称
        collection_name = vector_db._get_collection_name(
            project_id, vector_db.CHAPTERS_PREFIX
        )

        # 获取查询向量
        query_embedding = await self._get_embedding(query)

        # 查询
        results = vector_db.query_vectors(
            collection_name=collection_name,
            query_embedding=query_embedding,
            n_results=top_k,
        )

        # 格式化结果
        similar_chunks = []
        if results and results.get("ids"):
            ids = results["ids"][0]
            distances = results.get("distances", [[]])[0]
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]

            for i, chunk_id in enumerate(ids):
                similar_chunks.append({
                    "chunk_id": chunk_id,
                    "text": documents[i] if i < len(documents) else "",
                    "distance": distances[i] if i < len(distances) else 0.0,
                    "metadata": metadatas[i] if i < len(metadatas) else {},
                })

        return similar_chunks

    async def delete_chapter_vectors(
        self,
        project_id: str,
        chapter_id: str,
    ) -> None:
        """
        删除章节的所有向量数据

        Args:
            project_id: 项目ID
            chapter_id: 章节ID
        """
        vector_db = get_vector_db_manager()
        collection_name = vector_db._get_collection_name(
            project_id, vector_db.CHAPTERS_PREFIX
        )

        collection = vector_db.get_collection(project_id, "chapters")
        # 使用 where 条件删除
        collection.delete(where={"chapter_id": chapter_id})


# 全局服务实例
_chapter_vector_service: Optional[ChapterVectorService] = None


def get_chapter_vector_service() -> ChapterVectorService:
    """获取章节向量服务实例"""
    global _chapter_vector_service
    if _chapter_vector_service is None:
        _chapter_vector_service = ChapterVectorService()
    return _chapter_vector_service
