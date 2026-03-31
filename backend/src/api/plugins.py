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
