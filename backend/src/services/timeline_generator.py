"""AI 时间线生成服务 - 从大纲自动生成时间线事件"""

import uuid
from datetime import datetime

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import get_db_manager
from src.models.outline import OutlineNode
from src.models.timeline_event import TimelineEvent
from src.services.llm import BaseLLMService


class TimelineGenerator:
    """AI 时间线生成器 - 从大纲自动提取关键事件"""

    def __init__(self, llm: BaseLLMService):
        self.llm = llm

    async def _get_outline_nodes(
        self, project_id: str
    ) -> list[OutlineNode]:
        """获取项目大纲节点"""
        db_manager = get_db_manager()
        if project_id not in db_manager._engines:
            await db_manager.init_project_db(project_id)

        engine = db_manager._engines[project_id]
        async with AsyncSession(engine, expire_on_commit=False) as session:
            result = await session.execute(
                select(OutlineNode)
                .where(OutlineNode.project_id == project_id)
                .order_by(OutlineNode.sort_order)
            )
            nodes = result.scalars().all()
            return list(nodes)

    async def generate_from_outline(
        self, project_id: str
    ) -> list[dict]:
        """
        从大纲生成时间线事件

        Args:
            project_id: 项目ID

        Returns:
            list[dict]: 时间线事件列表，包含 id, time_point, event_type, sort_order 等
        """
        # 获取大纲节点
        nodes = await self._get_outline_nodes(project_id)
        
        if not nodes:
            return []

        # 构建大纲摘要
        outline_summary = "\n".join([
            f"{i+1}. [{node.line_type}] {node.title}" + 
            (f" - {node.summary}" if node.summary else "")
            for i, node in enumerate(nodes)
        ])

        prompt = f"""你是一位专业的小说时间线分析师。请从以下大纲中提取关键事件，生成时间线。

大纲内容：
{outline_summary}

请分析大纲中的关键事件，按时间顺序排列，并为每个事件分配：
- 合适的时间点（如「第1年3月」「主角10岁时」「纪元前1000年」等）
- 事件类型（主线/支线/暗线）
- 事件重要性标记

请按以下 JSON 格式输出：
{{
    "events": [
        {{
            "title": "事件标题",
            "description": "事件描述（可选）",
            "time_point": "时间点描述",
            "event_type": "主线/支线/暗线",
            "sort_order": 1
        }},
        ...
    ]
}}

请直接输出 JSON，只输出 JSON，不要输出其他内容："""

        raw = await self.llm.generate(prompt)

        # 解析 JSON 响应
        try:
            import json as _json
            import re
            
            # 尝试从响应中提取 JSON
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                result = _json.loads(match.group())
                events = result.get("events", [])
                
                # 保存到数据库
                await self._save_events(project_id, events)
                
                return events
        except Exception:
            pass

        # 降级方案：基于大纲节点简单生成
        return await self._fallback_generate(nodes)

    async def _fallback_generate(
        self, nodes: list[OutlineNode]
    ) -> list[dict]:
        """降级方案：基于大纲节点简单生成时间线"""
        events = []
        
        for i, node in enumerate(nodes):
            events.append({
                "title": node.title,
                "description": node.summary or "",
                "time_point": f"第{i+1}章",
                "event_type": node.line_type.value if hasattr(node.line_type, 'value') else node.line_type,
                "sort_order": i + 1,
            })
        
        return events

    async def _save_events(
        self, project_id: str, events: list[dict]
    ) -> None:
        """保存时间线事件到数据库"""
        db_manager = get_db_manager()
        if project_id not in db_manager._engines:
            await db_manager.init_project_db(project_id)

        engine = db_manager._engines[project_id]
        async with AsyncSession(engine, expire_on_commit=False) as session:
            for event_data in events:
                event = TimelineEvent(
                    id=str(uuid.uuid4()),
                    project_id=project_id,
                    title=event_data.get("title", ""),
                    description=event_data.get("description"),
                    time_point=event_data.get("time_point", ""),
                    event_type=event_data.get("event_type", "主线"),
                    sort_order=event_data.get("sort_order", 0),
                    character_ids=event_data.get("character_ids"),
                    location_id=event_data.get("location_id"),
                )
                session.add(event)

            await session.commit()
