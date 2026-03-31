"""数据库连接管理 - aiosqlite + SQLModel"""

import asyncio
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession as SASyncSession
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import get_settings


class DatabaseManager:
    """数据库管理器"""

    def __init__(self):
        self._engines: dict[str, AsyncEngine] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()

    def _get_engine(self, db_path: Path) -> AsyncEngine:
        """获取或创建数据库引擎"""
        db_url = f"sqlite+aiosqlite:///{db_path}"
        return create_async_engine(
            db_url,
            echo=False,
            connect_args={"check_same_thread": False},
        )

    async def init_project_db(self, project_id: str) -> None:
        """初始化项目数据库，创建表结构"""
        settings = get_settings()
        
        async with self._global_lock:
            if project_id not in self._engines:
                # 确保目录存在
                settings.ensure_directories(project_id)
                db_path = settings.get_db_path(project_id)
                
                engine = self._get_engine(db_path)
                self._engines[project_id] = engine
                self._locks[project_id] = asyncio.Lock()

        # 创建表结构
        engine = self._engines[project_id]
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    def get_session(self, project_id: str) -> AsyncGenerator[AsyncSession, None]:
        """获取项目数据库会话（async generator）"""
        async def _generate():
            if project_id not in self._engines:
                await self.init_project_db(project_id)

            engine = self._engines[project_id]
            session = AsyncSession(engine, expire_on_commit=False)
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
        
        return _generate()

    async def close_project_db(self, project_id: str) -> None:
        """关闭项目数据库连接"""
        if project_id in self._engines:
            await self._engines[project_id].dispose()
            del self._engines[project_id]
            if project_id in self._locks:
                del self._locks[project_id]

    async def close_all(self) -> None:
        """关闭所有数据库连接"""
        for project_id in list(self._engines.keys()):
            await self.close_project_db(project_id)


# 全局数据库管理器实例
_db_manager: DatabaseManager | None = None


def get_db_manager() -> DatabaseManager:
    """获取全局数据库管理器"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


async def get_db(project_id: str) -> AsyncGenerator[AsyncSession, None]:
    """依赖注入：获取项目数据库会话"""
    db_manager = get_db_manager()
    async for session in db_manager.get_session(project_id):
        yield session
