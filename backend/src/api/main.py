"""FastAPI 应用入口"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import api_router
from src.core.config import get_settings
from src.core.database import get_db_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    settings = get_settings()
    settings.ensure_directories()
    
    yield
    
    # 关闭时
    db_manager = get_db_manager()
    await db_manager.close_all()


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI 小说创作辅助平台后端 API",
        lifespan=lifespan,
    )
    
    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(api_router, prefix=settings.api_prefix)
    
    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {"status": "ok", "version": settings.app_version}
    
    return app


app = create_app()
