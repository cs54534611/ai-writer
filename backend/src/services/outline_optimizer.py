"""AI 大纲节奏优化服务 - 智能分配章节字数"""

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import get_db_manager
from src.models.outline import OutlineNode, LineType
from src.services.llm import BaseLLMService


class OutlineOptimizer:
    """AI 大纲节奏优化器 - 智能分配章节字数"""

    # 默认字数分配比例
    RHYTHM_RATIOS = {
        "opening": 0.15,   # 开头（前10%）
        "development": 0.40,  # 中段发展（60%的约2/3）
        "climax": 0.15,    # 高潮（60%的约1/3）
        "ending": 0.30,    # 结尾（30%）
    }

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

    def _calculate_position_ratio(
        self, index: int, total: int
    ) -> str:
        """计算节点在整体中的位置（前/中/后）"""
        if total <= 0:
            return "development"
        
        position = index / total
        
        if position < 0.1:
            return "opening"
        elif position > 0.7:
            return "ending"
        else:
            return "development"

    def _adjust_ratio_by_line_type(
        self, base_ratio: float, line_type: LineType, position: str
    ) -> float:
        """根据线类型调整字数比例"""
        if line_type == LineType.BRANCH:
            # 支线适当减少
            return base_ratio * 0.7
        elif line_type == LineType.SUBPLOT:
            # 副线更少
            return base_ratio * 0.5
        
        # 主线根据位置调整
        if position == "climax":
            return base_ratio * 1.3  # 高潮部分主线增加
        elif position == "ending":
            return base_ratio * 1.1  # 结尾适当增加
        
        return base_ratio

    def _ai_optimize(
        self, nodes: list[OutlineNode], target_words: int
    ) -> str:
        """使用 AI 优化字数分配"""
        # 构建大纲摘要
        outline_summary = []
        for i, node in enumerate(nodes):
            position = self._calculate_position_ratio(i, len(nodes))
            outline_summary.append({
                "index": i + 1,
                "title": node.title,
                "summary": node.summary or "",
                "line_type": node.line_type,
                "position": position,
            })

        prompt = f"""你是一位专业的小说结构分析师。请为以下大纲智能分配字数。

目标总字数：{target_words:,} 字
章节数量：{len(nodes)}

大纲结构：
{chr(10).join([f"{i+1}. [{n['line_type']}] {n['title']} - {n['summary'] or '无描述'}（位置: {n['position']}）" for i, n in enumerate(outline_summary])}

字数分配原则：
- 开头（前10%）：占 15% 字数，用于铺垫和建立
- 中段（10%-70%）：占 55% 字数，用于发展和蓄势
- 结尾（70%-100%）：占 30% 字数，用于高潮和收尾
- 主线章节比支线章节分配更多字数
- 高潮章节适当增加字数

请按以下 JSON 格式输出每个章节的建议字数分配：
{{
    "allocations": [
        {{"index": 1, "title": "章节标题", "suggested_words": 3000, "reason": "分配理由"}},
        ...
    ],
    "summary": {{
        "total": {target_words},
        "opening": "开头部分总字数",
        "development": "中段总字数",
        "ending": "结尾总字数"
    }}
}}

请直接输出 JSON："""
        
        return prompt

    async def optimize_chapter_rhythm(
        self, project_id: str, target_words: int
    ) -> dict:
        """
        智能优化章节字数分配

        Args:
            project_id: 项目ID
            target_words: 目标总字数（10万/50万/100万等）

        Returns:
            dict: 字数分配结果，包含每个大纲节点的建议字数
        """
        # 获取大纲节点
        nodes = await self._get_outline_nodes(project_id)
        
        if not nodes:
            return {
                "allocations": [],
                "summary": {
                    "total": target_words,
                    "opening": 0,
                    "development": 0,
                    "ending": 0,
                },
                "message": "未找到大纲节点",
            }

        # 使用 AI 进行智能分配
        prompt = self._ai_optimize(nodes, target_words)
        raw = await self.llm.generate(prompt)

        # 解析 AI 返回结果
        try:
            import json as _json
            import re
            
            # 尝试从响应中提取 JSON
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                result = _json.loads(match.group())
                
                # 更新数据库中的 word_target
                await self._update_word_targets(project_id, result.get("allocations", []))
                
                return result
        except Exception:
            pass

        # 降级方案：使用默认规则分配
        return await self._fallback_allocation(nodes, target_words)

    async def _fallback_allocation(
        self, nodes: list[OutlineNode], target_words: int
    ) -> dict:
        """降级方案：使用默认规则分配字数"""
        total = len(nodes)
        allocations = []

        for i, node in enumerate(nodes):
            position = self._calculate_position_ratio(i, total)
            base_ratio = self.RHYTHM_RATIOS.get(position, 0.20)
            
            # 根据线类型调整
            line_type = LineType(node.line_type) if isinstance(node.line_type, str) else node.line_type
            adjusted_ratio = self._adjust_ratio_by_line_type(base_ratio, line_type, position)
            
            suggested_words = int(target_words * adjusted_ratio)
            
            allocations.append({
                "index": i + 1,
                "title": node.title,
                "suggested_words": suggested_words,
                "reason": f"{position}阶段{'主线' if line_type == LineType.MAIN else '支线'}章节",
            })

        # 调整确保总数匹配
        total_allocated = sum(a["suggested_words"] for a in allocations)
        if total_allocated != target_words and allocations:
            diff = target_words - total_allocated
            # 将差值加到最长的章节（通常是高潮部分）
            allocations[-1]["suggested_words"] += diff

        return {
            "allocations": allocations,
            "summary": {
                "total": target_words,
                "opening": int(target_words * self.RHYTHM_RATIOS["opening"]),
                "development": int(target_words * (self.RHYTHM_RATIOS["development"] + self.RHYTHM_RATIOS["climax"])),
                "ending": int(target_words * self.RHYTHM_RATIOS["ending"]),
            },
            "message": "使用默认规则分配（AI解析失败）",
        }

    async def _update_word_targets(
        self, project_id: str, allocations: list[dict]
    ) -> None:
        """更新大纲节点的 word_target"""
        if not allocations:
            return

        db_manager = get_db_manager()
        engine = db_manager._engines.get(project_id)
        if not engine:
            return

        async with AsyncSession(engine, expire_on_commit=False) as session:
            for alloc in allocations:
                index = alloc.get("index")
                if not index:
                    continue

                # 根据 index 找到对应的节点（按 sort_order）
                result = await session.execute(
                    select(OutlineNode)
                    .where(OutlineNode.project_id == project_id)
                    .order_by(OutlineNode.sort_order)
                )
                all_nodes = result.scalars().all()
                
                if 0 < index <= len(all_nodes):
                    target_node = all_nodes[index - 1]
                    target_node.word_target = alloc.get("suggested_words", 0)

            await session.commit()
