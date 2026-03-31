"""custom_instruction 插件 - 章节完成时自动插入自定义签名"""

from datetime import datetime
from typing import Optional

from src.services.plugin import BasePlugin, PluginResult


class CustomInstructionPlugin(BasePlugin):
    """自定义指令插件
    
    在章节完成时自动在章节末尾插入作者签名/注释
    """

    metadata = {
        "id": "custom_instruction",
        "name": "自定义指令",
        "version": "1.0.0",
        "description": "在章节完成时自动插入自定义注释/签名",
        "author": "AI Writer Team",
        "hooks": ["on_chapter_complete"],
    }

    def __init__(self):
        self._default_config = {
            "signature_text": "",
            "include_timestamp": True,
            "include_word_count": True,
        }

    def execute(self, context: dict, **kwargs) -> PluginResult:
        """
        执行插件逻辑
        
        Args:
            context: 包含 chapter_id, project_id, content, word_count 等
        
        Returns:
            PluginResult: 执行结果
        """
        # 获取配置
        config = {**self._default_config, **kwargs}
        
        # 获取章节内容
        content = context.get("content", "")
        chapter_id = context.get("chapter_id", "")
        project_id = context.get("project_id", "")
        word_count = context.get("word_count", len(content))
        
        # 构建签名
        signature_parts = []
        
        if config.get("signature_text"):
            signature_parts.append(config["signature_text"])
        
        if config.get("include_timestamp"):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            signature_parts.append(f"[完成于 {timestamp}]")
        
        if config.get("include_word_count"):
            signature_parts.append(f"[字数: {word_count}]")
        
        if not signature_parts:
            return PluginResult(
                success=True,
                data={
                    "modified": False,
                    "reason": "未配置签名内容",
                    "chapter_id": chapter_id,
                },
                error=None,
            )
        
        # 拼接签名
        signature = "\n\n" + " ".join(signature_parts)
        
        # 在正文末尾添加签名
        modified_content = content + signature
        
        return PluginResult(
            success=True,
            data={
                "modified": True,
                "original_length": len(content),
                "modified_length": len(modified_content),
                "signature": signature,
                "chapter_id": chapter_id,
                "project_id": project_id,
            },
            error=None,
        )


# 导出插件实例
plugin = CustomInstructionPlugin
