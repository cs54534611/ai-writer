"""字数目标提醒插件"""

from typing import Optional

from src.services.plugin import BasePlugin, PluginResult, PluginMetadata


class WordCountGoalPlugin(BasePlugin):
    """字数目标提醒插件 - 每写满 N 字提醒一次"""

    metadata: PluginMetadata = {
        "id": "word_count_goal",
        "name": "字数目标提醒",
        "version": "1.0.0",
        "description": "每写满 N 字提醒一次，帮助作者达成写作目标",
        "author": "AI Writer",
        "hooks": ["after_write"],
    }

    def __init__(self):
        self._last_count: int = 0
        self._milestones_reached: set[int] = set()

    def execute(self, context: dict, threshold: int = 1000) -> PluginResult:
        """
        检查是否达到目标字数
        
        Args:
            context: 写作上下文，包含 word_count, chapter_id 等
            threshold: 字数阈值，默认 1000
        
        Returns:
            PluginResult: 包含提醒信息的执行结果
        """
        try:
            word_count = context.get("word_count", 0)
            chapter_id = context.get("chapter_id", "unknown")
            project_id = context.get("project_id", "unknown")

            if word_count <= self._last_count:
                # 字数没有增加，可能被重置了
                self._last_count = word_count
                self._milestones_reached.clear()

            # 计算当前达到了哪个里程碑
            current_milestone = (word_count // threshold) * threshold
            
            results = []
            while current_milestone > self._last_count and current_milestone > 0:
                milestone = current_milestone
                if milestone not in self._milestones_reached and milestone <= word_count:
                    self._milestones_reached.add(milestone)
                    results.append(f"🎉 已完成 {milestone} 字！继续加油！")
                current_milestone -= threshold

            if results:
                self._last_count = word_count
                return PluginResult(
                    success=True,
                    data={
                        "word_count": word_count,
                        "threshold": threshold,
                        "milestones_reached": list(self._milestones_reached),
                        "messages": results,
                        "chapter_id": chapter_id,
                        "project_id": project_id,
                    },
                    error=None,
                )

            self._last_count = word_count
            return PluginResult(
                success=True,
                data={
                    "word_count": word_count,
                    "threshold": threshold,
                    "next_milestone": ((word_count // threshold) + 1) * threshold,
                    "remaining": ((word_count // threshold) + 1) * threshold - word_count,
                },
                error=None,
            )

        except Exception as e:
            return PluginResult(
                success=False,
                data=None,
                error=f"字数目标检查失败: {str(e)}",
            )
