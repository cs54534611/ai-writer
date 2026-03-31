"""Hello World 示例插件"""

from typing import TypedDict
from src.services.plugin import BasePlugin


class PluginMetadata(TypedDict):
    """插件元数据"""
    id: str
    name: str
    version: str
    description: str
    author: str
    hooks: list[str]


class PluginResult(TypedDict):
    """插件执行结果"""
    success: bool
    data: dict | None
    error: str | None


class HelloWorldPlugin(BasePlugin):
    """Hello World 示例插件"""

    metadata: PluginMetadata = {
        "id": "hello_world",
        "name": "Hello World 示例插件",
        "version": "1.0.0",
        "description": "一个简单的示例插件，展示插件系统的基本用法",
        "author": "AI Writer Team",
        "hooks": ["on_chapter_complete", "on_project_create"],
    }

    def execute(self, context: dict, **kwargs) -> PluginResult:
        """执行插件逻辑"""
        action = context.get("action", "greet")
        
        if action == "greet":
            return PluginResult(
                success=True,
                data={"message": f"Hello, {context.get('name', 'World')}!"},
                error=None,
            )
        elif action == "celebrate":
            return PluginResult(
                success=True,
                data={"message": "🎉 恭喜完成章节！"},
                error=None,
            )
        else:
            return PluginResult(
                success=False,
                data=None,
                error=f"Unknown action: {action}",
            )
