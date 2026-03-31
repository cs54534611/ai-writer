"""插件相关 Pydantic Schemas"""

from pydantic import BaseModel
from typing import Optional


class PluginSchema(BaseModel):
    """插件信息 Schema"""
    id: str
    name: str
    version: str
    description: str
    author: str
    hooks: list[str]
    enabled: bool
    config: dict = {}


class PluginConfigRequest(BaseModel):
    """插件配置更新请求"""
    plugin_id: str
    config: dict


class PluginExecuteRequest(BaseModel):
    """插件执行请求"""
    plugin_id: str
    context: dict = {}


class PluginExecuteResponse(BaseModel):
    """插件执行响应"""
    plugin_id: str
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
