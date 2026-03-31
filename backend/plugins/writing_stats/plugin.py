"""写作统计增强插件"""

from typing import TypedDict
from src.services.plugin import BasePlugin
from .stats_handler import get_stats_handler


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


class WritingStatsPlugin(BasePlugin):
    """写作统计增强插件 - 记录章节完成时的字数统计"""

    metadata: PluginMetadata = {
        "id": "writing_stats",
        "name": "写作统计增强",
        "version": "1.0.0",
        "description": "记录每日写作字数，生成统计报告，帮助作者追踪写作进度",
        "author": "AIWriter Team",
        "hooks": ["on_chapter_complete"],
    }

    def execute(self, context: dict, **kwargs) -> PluginResult:
        """
        执行插件逻辑
        
        当章节完成时，记录字数统计
        """
        action = context.get("action", "")
        
        if action == "on_chapter_complete":
            return self._handle_chapter_complete(context)
        elif action == "get_stats":
            return self._handle_get_stats(context)
        else:
            return PluginResult(
                success=False,
                data=None,
                error=f"Unknown action: {action}",
            )

    def _handle_chapter_complete(self, context: dict) -> PluginResult:
        """处理章节完成事件"""
        try:
            handler = get_stats_handler()
            
            project_id = context.get("project_id", "unknown")
            chapter_id = context.get("chapter_id", "")
            chapter_title = context.get("chapter_title", "无标题")
            word_count = context.get("word_count", 0)
            
            if not word_count:
                # 尝试从 content 计算
                content = context.get("content", "")
                if content:
                    word_count = len(content)
            
            handler.record_chapter_complete(
                project_id=project_id,
                chapter_id=chapter_id,
                chapter_title=chapter_title,
                word_count=word_count,
            )
            
            # 生成简要报告
            report = handler.get_daily_report()
            
            return PluginResult(
                success=True,
                data={
                    "message": f"已记录章节「{chapter_title}」的字数统计",
                    "today_words": report["total_words"],
                    "today_chapters": report["total_chapters"],
                },
                error=None,
            )
            
        except Exception as e:
            return PluginResult(
                success=False,
                data=None,
                error=f"记录统计失败: {str(e)}",
            )

    def _handle_get_stats(self, context: dict) -> PluginResult:
        """获取统计报告"""
        try:
            handler = get_stats_handler()
            report_type = context.get("report_type", "summary")
            
            if report_type == "daily":
                data = handler.get_daily_report()
            elif report_type == "weekly":
                data = handler.get_weekly_report()
            elif report_type == "monthly":
                data = handler.get_monthly_report()
            elif report_type == "overall":
                data = handler.get_overall_stats()
            else:
                data = handler.generate_summary_report()
            
            return PluginResult(
                success=True,
                data=data,
                error=None,
            )
            
        except Exception as e:
            return PluginResult(
                success=False,
                data=None,
                error=f"获取统计失败: {str(e)}",
            )
