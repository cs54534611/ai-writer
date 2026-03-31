"""API 路由初始化"""

from fastapi import APIRouter

from src.api.projects import router as projects_router
from src.api.characters import router as characters_router
from src.api.relationships import router as relationships_router
from src.api.inspirations import router as inspirations_router
from src.api.outlines import router as outlines_router
from src.api.world_settings import router as world_settings_router
from src.api.locations import router as locations_router
from src.api.chapters import router as chapters_router
from src.api.writing import router as writing_router
from src.api.reviews import router as reviews_router
from src.api.image_gen import router as image_gen_router
from src.api.fandom import router as fandom_router
from src.api.plugins import router as plugins_router
from src.api.export_import import router as export_import_router
from src.api.sensitive_words import router as sensitive_words_router
from src.api.foreshadowings import router as foreshadowings_router

api_router = APIRouter()

# 插件管理
api_router.include_router(plugins_router, prefix="/plugins", tags=["plugins"])

# 导入导出
api_router.include_router(export_import_router, tags=["export_import"])

# 书架管理
api_router.include_router(projects_router, prefix="/projects", tags=["projects"])

# 角色管理
api_router.include_router(characters_router, prefix="/projects/{project_id}/characters", tags=["characters"])

# 关系管理
api_router.include_router(relationships_router, prefix="/projects/{project_id}/relationships", tags=["relationships"])

# 灵感速记
api_router.include_router(inspirations_router, prefix="/projects/{project_id}/inspirations", tags=["inspirations"])

# 大纲规划
api_router.include_router(outlines_router, prefix="/projects/{project_id}/outlines", tags=["outlines"])

# 世界设定
api_router.include_router(world_settings_router, prefix="/projects/{project_id}/world-settings", tags=["world_settings"])

# 地点/地图
api_router.include_router(locations_router, prefix="/projects/{project_id}/locations", tags=["locations"])

# 章节管理 + AI 写作
api_router.include_router(chapters_router, prefix="/projects/{project_id}/chapters", tags=["chapters"])

# 独立 AI 写作
api_router.include_router(writing_router, prefix="/projects/{project_id}/writing", tags=["writing"])

# 审查服务
api_router.include_router(reviews_router, prefix="/projects/{project_id}/reviews", tags=["reviews"])

# AI 插图生成
api_router.include_router(image_gen_router, prefix="/projects/{project_id}/images", tags=["images"])

# 同人创作
api_router.include_router(fandom_router, prefix="/projects/{project_id}/fandom", tags=["fandom"])

# 敏感词管理
api_router.include_router(sensitive_words_router, prefix="/projects/{project_id}/sensitive-words", tags=["sensitive_words"])

# 伏笔管理
api_router.include_router(foreshadowings_router, prefix="/projects/{project_id}/foreshadowings", tags=["foreshadowings"])

__all__ = ["api_router"]
