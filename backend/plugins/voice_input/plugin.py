"""voice_input 插件 - 语音输入占位

注意：语音输入功能已由前端实现，此插件为保持插件市场完整性而占位。
"""

from src.services.plugin import BasePlugin, PluginResult


class VoiceInputPlugin(BasePlugin):
    """语音输入占位插件"""

    metadata = {
        "id": "voice_input",
        "name": "语音输入",
        "version": "1.0.0",
        "description": "语音输入功能（由前端实现，此为占位插件）",
        "author": "AI Writer Team",
        "hooks": [],
    }

    def execute(self, context: dict, **kwargs) -> PluginResult:
        """此插件无实际功能"""
        return PluginResult(
            success=True,
            data={
                "note": "语音输入功能已由前端实现",
                "placeholder": True,
            },
            error=None,
        )


plugin = VoiceInputPlugin
