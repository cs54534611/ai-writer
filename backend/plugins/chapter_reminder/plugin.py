"""章节完成提醒插件"""

import logging
import random
from typing import TypedDict
from src.services.plugin import BasePlugin


# 配置日志
logger = logging.getLogger("chapter_reminder")


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


# 鼓励语录库
ENCOURAGEMENTS = [
    # 基础鼓励
    "🎉 太棒了！你完成了一章！继续保持这个节奏！",
    "📝 又一章完成！你真是个创作达人！",
    "✨ 章节完成！你的故事又向前迈进了一步！",
    "🌟 写得好！每一章都是你心血的结晶！",
    "💪 完成得漂亮！继续加油！",
    
    # 进度相关
    "📊 进度+1！距离完成大作又近了一步！",
    "🎯 又达成一个小目标！大步向前进！",
    "🚀 里程碑达成！你的故事正在成型！",
    "🏆 章节完成！这就是坚持的力量！",
    "📈 稳定的输出，了不起的进度！",
    
    # 创意鼓励
    "🎨 你的想象力又一次化为文字，精彩！",
    "📖 又一个故事篇章诞生了！",
    "✍️ 笔墨生花，这章写得太妙了！",
    "🌈 你的创意无限，这章充满了惊喜！",
    "🎭 角色的命运在你笔下延续，精彩！",
    
    # 激励语
    "🔥 燃烧吧创作之魂！下一章更精彩！",
    "⚡ 灵感如闪电！继续创作吧！",
    "💫 你的故事值得被世界看见！",
    "🌠 星辰大海在前方，继续航行！",
    "🎇 每一次写作都是一次冒险，你做得很好！",
    
    # 轻松幽默
    "😄 这章写完可以去喝杯茶休息一下了！",
    "🍵 辛苦啦！创作累了记得休息！",
    "🎮 写完这章，娱乐时间到！...还是先写下一章？",
    "😂 什么？你居然写完了？太厉害了！",
    "🤩 我被你惊人的创作速度震惊了！",
    
    # 长篇相关
    "📚 长篇大作又添新章，向目标迈进！",
    "🏰 你世界的版图在不断扩大！",
    "🌐 你的小说宇宙越来越丰富了！",
    "🎭 更多角色登上故事舞台！",
    "📜 史诗篇章继续书写！",
]


# 写作小贴士
WRITING_TIPS = [
    "💡 小贴士：保持每天固定的写作时间，有助于养成习惯",
    "💡 小贴士：写完一章后，稍作休息再继续，效率更高",
    "💡 小贴士：记得定期回顾之前的章节，保持连贯性",
    "💡 小贴士：灵感来临时，随手记录下来",
    "💡 小贴士：不要太纠结于完美，先完成再修改",
    "💡 小贴士：保持良好的坐姿，保护身体很重要",
    "💡 小贴士：适当的运动可以激发创作灵感",
    "💡 小贴士：阅读其他作品可以给你带来新的启发",
]


class ChapterReminderPlugin(BasePlugin):
    """章节完成提醒插件 - 打印鼓励性提示语到日志"""

    metadata: PluginMetadata = {
        "id": "chapter_reminder",
        "name": "章节完成提醒",
        "version": "1.0.0",
        "description": "章节完成时打印鼓励性提示语到日志，激励作者继续创作",
        "author": "AIWriter Team",
        "hooks": ["on_chapter_complete"],
    }

    def execute(self, context: dict, **kwargs) -> PluginResult:
        """
        执行插件逻辑
        
        当章节完成时，打印鼓励性提示语
        """
        action = context.get("action", "")
        
        if action == "on_chapter_complete":
            return self._handle_chapter_complete(context)
        else:
            return PluginResult(
                success=False,
                data=None,
                error=f"Unknown action: {action}",
            )

    def _handle_chapter_complete(self, context: dict) -> PluginResult:
        """处理章节完成事件"""
        try:
            chapter_title = context.get("chapter_title", "未知章节")
            project_id = context.get("project_id", "")
            word_count = context.get("word_count", 0)
            
            # 随机选择鼓励语和写作小贴士
            encouragement = random.choice(ENCOURAGEMENTS)
            writing_tip = random.choice(WRITING_TIPS)
            
            # 构建日志消息
            log_message = f"""
╔══════════════════════════════════════════════════════════════╗
║              📖 章节完成提醒 📖                              ║
╠══════════════════════════════════════════════════════════════╣
║ 项目: {project_id or '未知项目':<50} ║
║ 章节: {chapter_title:<50} ║
║ 字数: {word_count:,} 字{' '*42} ║
╠══════════════════════════════════════════════════════════════╣
║ {encouragement:<56} ║
╠══════════════════════════════════════════════════════════════╣
║ {writing_tip:<56} ║
╚══════════════════════════════════════════════════════════════╝
"""
            
            # 打印到日志
            logger.info(log_message)
            
            return PluginResult(
                success=True,
                data={
                    "message": encouragement,
                    "tip": writing_tip,
                    "chapter_title": chapter_title,
                    "word_count": word_count,
                },
                error=None,
            )
            
        except Exception as e:
            logger.error(f"章节提醒插件执行失败: {str(e)}")
            return PluginResult(
                success=False,
                data=None,
                error=f"提醒失败: {str(e)}",
            )
