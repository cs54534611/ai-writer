"""AI 写作服务 - 续写/扩写/改写/描写增强/即时反馈"""

from typing import AsyncIterator

from src.services.llm import BaseLLMService


class WritingService:
    """AI 写作服务"""

    # 默认续写提示词模板
    CONTINUE_TEMPLATE = """你是一位专业的小说作家。请根据以下前文内容，续写一段精彩的故事。

前文内容：
{context}

续写要求：
- 风格：{style}
- 保持与前文的连贯性
- 注重人物性格的一致性
- 适当推进情节发展
- 禁止输出任何非故事内容

请直接输出续写内容："""

    # 多版本续写提示词
    CONTINUE_MULTI_TEMPLATE = """你是一位专业的小说作家。请根据以下前文内容，续写 {num_versions} 个不同版本的故事供选择。

前文内容：
{context}

风格要求：{style}

版本要求：
- 每个版本都要有独特的创意和切入点
- 保持与前文的连贯性
- 注重人物性格的一致性
- 每个版本字数适中（200-500字）
- 禁止输出任何非故事内容

请按以下格式输出（只输出故事内容，不要输出版本标记）：
---
[版本1]
（续写内容1）
---
[版本2]
（续写内容2）
---
（如果有更多版本继续）

请直接输出："""

    # 扩写提示词
    EXPAND_TEMPLATE = """你是一位专业的小说作家。请将以下段落扩写约 {expand_ratio}x 倍，丰富细节和描写。

原文：
{paragraph}

扩写要求：
- 保持原文的核心意思和情感基调
- 增加环境描写、人物心理描写、动作细节等
- 适当添加对话或场景转换
- 扩写后内容要自然流畅
- 禁止输出任何非故事内容

请直接输出扩写后的内容："""

    # 改写提示词
    REWRITE_POLISH_TEMPLATE = """你是一位专业的小说作家。请对以下内容进行润色打磨。

原文：
{content}

润色要求：
- 改善句式结构，使文章更加流畅
- 提升文字的感染力和表现力
- 保持原文的核心意思不变
- 适度增加文采
- 禁止输出任何非故事内容

请直接输出润色后的内容："""

    REWRITE_ALTERNATIVE_TEMPLATE = """你是一位专业的小说作家。请对以下内容提供一个完全不同角度的改写版本。

原文：
{content}

改写要求：
- 提供一个全新角度的改写
- 可以改变叙事视角、时间顺序、场景等
- 保持相同的主题和核心事件
- 保持故事的完整性和逻辑性
- 禁止输出任何非故事内容

请直接输出改写后的内容："""

    REWRITE_TONE_TEMPLATE = """你是一位专业的小说作家。请对以下内容进行语调转换，改写成更加{ tone }的版本。

原文：
{content}

改写要求：
- 调整整体语调为 {tone}
- 保持原文的核心意思不变
- 可以调整用词和句式来匹配新语调
- 禁止输出任何非故事内容

请直接输出改写后的内容："""

    # 描写增强提示词
    ENHANCE_DESCRIPTION_TEMPLATE = """你是一位专业的小说作家。请对以下内容进行感官描写增强。

原文：
{content}

增强要求：
- 着重增强以下感官描写：{senses}
- 增加场景的氛围感和沉浸感
- 通过感官细节让读者身临其境
- 保持原文的核心意思不变
- 禁止输出任何非故事内容

请直接输出增强描写后的内容："""

    # 即时反馈提示词
    FEEDBACK_TEMPLATE = """你是一位专业的小说编辑。请对以下小说内容提供即时反馈。

小说内容：
{content}

反馈重点（可选）：
{focus_areas}

请从以下维度提供反馈：
1. 整体评分（1-10分）
2. 优点分析
3. 需要改进的地方（具体指出）
4. 具体可执行的修改建议

请按以下 JSON 格式输出（只输出JSON，不要输出其他内容）：
{{
    "score": 分数（1-10）,
    "strengths": ["优点1", "优点2", ...],
    "issues": ["问题1", "问题2", ...],
    "suggestions": ["建议1", "建议2", ...]
}}"""

    # 对话式写作提示词
    DIALOGUE_TEMPLATE = """你是一位创意写作助手。请根据以下设定进行对话式故事创作（类似彩云小梦风格）。

角色设定：
{characters}

场景描述：
{scene}

当前对话进度：
{last_dialogue}

创作要求：
- 以对话为主，辅以简洁的动作和心理描写
- 保持各角色的独特性格和说话风格
- 对话要自然、生动、有趣
- 推进情节发展，创造有趣的互动
- 禁止输出任何非故事内容

请直接输出对话内容："""

    def __init__(self, llm: BaseLLMService):
        self.llm = llm

    def _build_continue_prompt(
        self, context: str, style: str = "default"
    ) -> str:
        """构建续写提示词"""
        style_map = {
            "default": "叙事流畅，节奏适中",
            "dialog_heavy": "对话丰富，人物互动频繁",
            "desc_heavy": "描写细腻，环境氛围浓厚",
            "fastpaced": "节奏紧凑，情节推进快",
            "slowpaced": "节奏舒缓，情感细腻",
        }
        style_desc = style_map.get(style, "叙事流畅，节奏适中")
        return self.CONTINUE_TEMPLATE.format(context=context, style=style_desc)

    def _build_continue_multi_prompt(
        self, context: str, style: str = "default", num_versions: int = 2
    ) -> str:
        """构建多版本续写提示词"""
        style_map = {
            "default": "叙事流畅，节奏适中",
            "dialog_heavy": "对话丰富，人物互动频繁",
            "desc_heavy": "描写细腻，环境氛围浓厚",
        }
        style_desc = style_map.get(style, "叙事流畅，节奏适中")
        return self.CONTINUE_MULTI_TEMPLATE.format(
            context=context,
            style=style_desc,
            num_versions=num_versions,
        )

    async def continue_writing(
        self,
        context: str,
        style: str = "default",
        num_versions: int = 1,
    ) -> list[dict]:
        """
        AI 续写 - 生成一个或多个版本供选择

        Args:
            context: 前文内容
            style: 续写风格 (default/dialog_heavy/desc_heavy/fastpaced/slowpaced)
            num_versions: 生成版本数量 (1-3)

        Returns:
            list[dict]: 续写结果列表，每个包含 {version, content}
        """
        num_versions = max(1, min(3, num_versions))

        if num_versions == 1:
            prompt = self._build_continue_prompt(context, style)
            content = await self.llm.generate(prompt)
            return [{"version": 1, "content": content.strip()}]

        # 多版本
        prompt = self._build_continue_multi_prompt(context, style, num_versions)
        raw = await self.llm.generate(prompt)

        results = []
        # 简单解析多版本输出
        parts = raw.split("---")
        version = 1
        for part in parts:
            content = part.strip()
            if "[版本" in content:
                # 提取版本号和内容
                lines = content.split("\n", 1)
                if len(lines) > 1:
                    content = lines[1].strip()
            if content and len(content) > 20:  # 过滤太短的内容
                results.append({"version": version, "content": content})
                version += 1
                if version > num_versions:
                    break

        # 如果解析失败，至少返回一个完整内容
        if not results and raw.strip():
            results.append({"version": 1, "content": raw.strip()})

        return results

    async def continue_writing_stream(
        self,
        context: str,
        style: str = "default",
    ) -> AsyncIterator[str]:
        """
        AI 续写 - 流式版本

        Args:
            context: 前文内容
            style: 续写风格

        Yields:
            str: 续写内容的 token
        """
        prompt = self._build_continue_prompt(context, style)
        async for token in self.llm.stream_generate(prompt):
            yield token

    async def expand_writing(
        self,
        paragraph: str,
        expand_ratio: float = 2.0,
    ) -> str:
        """
        AI 扩写 - 将段落扩写 N 倍

        Args:
            paragraph: 要扩写的段落
            expand_ratio: 扩写倍数 (默认 2.0)

        Returns:
            str: 扩写后的内容
        """
        prompt = self.EXPAND_TEMPLATE.format(
            paragraph=paragraph,
            expand_ratio=expand_ratio,
        )
        return (await self.llm.generate(prompt)).strip()

    async def rewrite_writing(
        self,
        content: str,
        mode: str = "polish",
        **kwargs,
    ) -> str:
        """
        AI 改写

        Args:
            content: 要改写的内容
            mode: 改写模式 (polish/alternative/tone)
            **kwargs: 额外参数，如 tone 用于 tone 模式

        Returns:
            str: 改写后的内容
        """
        if mode == "polish":
            prompt = self.REWRITE_POLISH_TEMPLATE.format(content=content)
        elif mode == "alternative":
            prompt = self.REWRITE_ALTERNATIVE_TEMPLATE.format(content=content)
        elif mode == "tone":
            tone = kwargs.get("tone", "轻松幽默")
            prompt = self.REWRITE_TONE_TEMPLATE.format(
                content=content,
                tone=tone,
            )
        else:
            # 默认润色
            prompt = self.REWRITE_POLISH_TEMPLATE.format(content=content)

        return (await self.llm.generate(prompt)).strip()

    async def enhance_description(
        self,
        content: str,
        senses: list[str] = None,
    ) -> str:
        """
        AI 描写增强 - 增强感官描写

        Args:
            content: 要增强的内容
            senses: 要增强的感官列表 (visual/auditory/olfactory/tactile/smell/taste)
                    默认全部增强

        Returns:
            str: 增强描写后的内容
        """
        sense_map = {
            "visual": "视觉（色彩、光影、形状等）",
            "auditory": "听觉（声音、音效、音乐等）",
            "olfactory": "嗅觉（气味、香味、腐臭等）",
            "tactile": "触觉（质感、温度、触感等）",
            "smell": "嗅觉（气味、香味、腐臭等）",
            "taste": "味觉（味道、口感等）",
        }

        if not senses:
            senses_text = "所有感官（视觉、听觉、嗅觉、触觉、味觉）"
        else:
            senses_text = "、".join(
                sense_map.get(s, s) for s in senses
            )

        prompt = self.ENHANCE_DESCRIPTION_TEMPLATE.format(
            content=content,
            senses=senses_text,
        )
        return (await self.llm.generate(prompt)).strip()

    async def instant_feedback(
        self,
        content: str,
        focus_areas: list[str] = None,
    ) -> dict:
        """
        AI 即时反馈

        Args:
            content: 要反馈的内容
            focus_areas: 反馈重点 (pacing/character/plot/writing)

        Returns:
            dict: 反馈结果 {score, strengths, issues, suggestions}
        """
        if focus_areas:
            focus_text = "重点关注：" + "、".join(focus_areas)
        else:
            focus_text = "全面评估小说质量"

        prompt = self.FEEDBACK_TEMPLATE.format(
            content=content,
            focus_areas=focus_text,
        )

        raw = await self.llm.generate(prompt)

        # 解析 JSON 响应
        try:
            # 尝试提取 JSON
            import json as _json

            # 尝试直接解析
            try:
                return _json.loads(raw)
            except _json.JSONDecodeError:
                pass

            # 尝试从 markdown 代码块中提取
            import re

            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
            if match:
                return _json.loads(match.group(1))

            # 尝试找最外层的 JSON 对象
            match = re.search(r"(\{.*\})", raw, re.DOTALL)
            if match:
                return _json.loads(match.group(1))

        except Exception:
            pass

        # 解析失败时返回原始内容和错误信息
        return {
            "score": 5,
            "strengths": ["内容已接收"],
            "issues": ["反馈解析失败，请查看原始内容"],
            "suggestions": [raw[:500] if len(raw) > 500 else raw],
            "_raw": raw,
        }

    async def dialogue_write(
        self,
        characters: list[dict],
        scene: str,
        last_dialogue: str,
    ) -> str:
        """
        对话式写作（彩云小梦式）

        Args:
            characters: 角色设定列表，每个包含 name, personality, background 等
            scene: 场景描述
            last_dialogue: 最后一句对话（AI 从这里继续）

        Returns:
            str: AI 角色扮演的对话内容
        """
        # 构建角色设定文本
        characters_text = "\n".join(
            f"- {c.get('name', '未知角色')}：{c.get('personality', '')} {c.get('background', '')}".strip()
            for c in characters
        )

        prompt = self.DIALOGUE_TEMPLATE.format(
            characters=characters_text,
            scene=scene,
            last_dialogue=last_dialogue,
        )

        return (await self.llm.generate(prompt)).strip()
