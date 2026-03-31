"""插件管理 API 路由"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from src.schemas.plugin import (
    PluginSchema,
    PluginConfigRequest,
    PluginExecuteRequest,
    PluginExecuteResponse,
)
from src.services.plugin import get_plugin_manager, PluginResult

router = APIRouter()


# 插件市场内置推荐插件
MARKET_PLUGINS = [
    {"id": "word-count-goal", "name": "字数目标提醒", "description": "每日/每周字数目标，到期提醒", "author": "AIWriter Team", "downloads": 0, "rating": 5.0, "tags": ["写作", "目标"]},
    {"id": "daily-backup", "name": "每日备份", "description": "每日自动备份项目数据", "author": "AIWriter Team", "downloads": 0, "rating": 5.0, "tags": ["备份", "安全"]},
    {"id": "pinyin-helper", "name": "拼音助手", "description": "自动为角色名添加拼音注音", "author": "Community", "downloads": 0, "rating": 4.5, "tags": ["中文", "工具"]},
    {"id": "writing-stats", "name": "写作统计", "description": "详细写作数据统计和可视化", "author": "Community", "downloads": 0, "rating": 4.8, "tags": ["统计", "仪表盘"]},
]


@router.get("/market")
async def get_plugin_market():
    """获取插件市场列表（内置推荐插件）"""
    return MARKET_PLUGINS


@router.post("/{plugin_id}/install")
async def install_market_plugin(
    plugin_id: Annotated[str, Path(description="插件ID")],
):
    """从市场安装插件"""
    # 检查插件是否在市场中存在
    plugin = next((p for p in MARKET_PLUGINS if p["id"] == plugin_id), None)
    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin {plugin_id} not found in market",
        )
    
    manager = get_plugin_manager()
    # 启用插件（市场插件默认是内置的，只需启用即可）
    success = manager.enable_plugin(plugin_id)
    
    return {
        "success": success,
        "plugin_id": plugin_id,
        "message": f"插件 {plugin['name']} 安装成功" if success else f"插件 {plugin['name']} 安装失败",
    }


@router.get("/", response_model=list[PluginSchema])
async def list_plugins() -> list[PluginSchema]:
    """
    获取所有已发现插件列表（含启用状态）
    """
    manager = get_plugin_manager()
    discovered = manager.discover_plugins()

    plugins = []
    for metadata in discovered:
        plugin_id = metadata["id"]
        plugins.append(PluginSchema(
            id=metadata["id"],
            name=metadata["name"],
            version=metadata["version"],
            description=metadata["description"],
            author=metadata["author"],
            hooks=metadata["hooks"],
            enabled=manager.is_plugin_enabled(plugin_id),
            config=manager.get_plugin_config(plugin_id),
        ))

    return plugins


@router.post("/{plugin_id}/enable", response_model=PluginSchema)
async def enable_plugin(
    plugin_id: Annotated[str, Path(description="插件ID")],
) -> PluginSchema:
    """
    启用指定插件
    """
    manager = get_plugin_manager()
    
    # 确保插件已发现
    discovered = {p["id"]: p for p in manager.discover_plugins()}
    if plugin_id not in discovered:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin {plugin_id} not found",
        )

    success = manager.enable_plugin(plugin_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to enable plugin {plugin_id}",
        )

    metadata = discovered[plugin_id]
    return PluginSchema(
        id=metadata["id"],
        name=metadata["name"],
        version=metadata["version"],
        description=metadata["description"],
        author=metadata["author"],
        hooks=metadata["hooks"],
        enabled=True,
        config=manager.get_plugin_config(plugin_id),
    )


@router.post("/{plugin_id}/disable", response_model=PluginSchema)
async def disable_plugin(
    plugin_id: Annotated[str, Path(description="插件ID")],
) -> PluginSchema:
    """
    禁用指定插件
    """
    manager = get_plugin_manager()
    
    # 确保插件已发现
    discovered = {p["id"]: p for p in manager.discover_plugins()}
    if plugin_id not in discovered:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin {plugin_id} not found",
        )

    success = manager.disable_plugin(plugin_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to disable plugin {plugin_id}",
        )

    metadata = discovered[plugin_id]
    return PluginSchema(
        id=metadata["id"],
        name=metadata["name"],
        version=metadata["version"],
        description=metadata["description"],
        author=metadata["author"],
        hooks=metadata["hooks"],
        enabled=False,
        config=manager.get_plugin_config(plugin_id),
    )


@router.get("/{plugin_id}/config", response_model=dict)
async def get_plugin_config(
    plugin_id: Annotated[str, Path(description="插件ID")],
) -> dict:
    """
    获取插件配置
    """
    manager = get_plugin_manager()
    
    # 确保插件已发现
    discovered = {p["id"]: p for p in manager.discover_plugins()}
    if plugin_id not in discovered:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin {plugin_id} not found",
        )

    return manager.get_plugin_config(plugin_id)


@router.put("/{plugin_id}/config", response_model=dict)
async def update_plugin_config(
    plugin_id: Annotated[str, Path(description="插件ID")],
    config_request: PluginConfigRequest,
) -> dict:
    """
    更新插件配置
    """
    manager = get_plugin_manager()
    
    # 确保插件已发现
    discovered = {p["id"]: p for p in manager.discover_plugins()}
    if plugin_id not in discovered:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin {plugin_id} not found",
        )

    manager.save_plugin_config(plugin_id, config_request.config)
    return config_request.config


@router.post("/{plugin_id}/execute", response_model=PluginExecuteResponse)
async def execute_plugin(
    plugin_id: Annotated[str, Path(description="插件ID")],
    execute_request: PluginExecuteRequest,
) -> PluginExecuteResponse:
    """
    直接执行指定插件
    """
    manager = get_plugin_manager()
    
    # 确保插件已发现
    discovered = {p["id"]: p for p in manager.discover_plugins()}
    if plugin_id not in discovered:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin {plugin_id} not found",
        )

    result: PluginResult = await manager.execute_plugin(
        plugin_id, 
        execute_request.context,
    )

    return PluginExecuteResponse(
        plugin_id=plugin_id,
        success=result["success"],
        data=result.get("data"),
        error=result.get("error"),
    )
