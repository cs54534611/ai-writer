"""同人创作工作流服务"""

from typing import Optional

from src.services.llm import BaseLLMService


class FandomService:
    """同人创作工作流"""

    # 导入设定提示词
    IMPORT_TEMPLATE = """你是一位专业的同人创作分析师。请分析以下原文小说文本，提取可用于同人创作的关键设定。

原文：
{source_text}

请从以下维度进行分析：

1. **主要角色**（列出名字、重要性格特点、外貌特征、在故事中的作用）
2. **角色关系**（角色之间的关系，如朋友、恋人、家人、对手等）
3. **世界观设定**（故事发生的世界、规则、地点等）
4. **叙事风格**（原作的写作风格特点）
5. **创作建议**（适合的同人创作方向）

请按以下 JSON 格式输出（只输出 JSON，不要输出其他内容）：
{{
    "characters": [
        {{
            "name": "角色名",
            "aliases": ["别名1", "别名2"],
            "personality": "性格特点",
            "appearance": "外貌特征",
            "role": "protagonist/antagonist/supporting"
        }}
    ],
    "relationships": [
        {{
            "character1": "角色1",
            "character2": "角色2",
            "relationship_type": "friends/lovers/rivals/family/etc",
            "description": "关系描述"
        }}
    ],
    "world_settings": [
        {{
            "name": "设定名称",
            "description": "设定描述",
            "key_locations": ["关键地点1", "地点2"],
            "rules": ["世界规则1", "规则2"]
        }}
    ],
    "narrative_style": "叙事风格描述",
    "writing_suggestions": ["建议1", "建议2", "建议3"]
}}"""

    # 大纲生成提示词
    OUTLINE_TEMPLATE = """你是一位专业的同人小说作家。请为以下同人创作生成详细的大纲。

同人作品名称：{fandom_name}
使用角色：{character_names}
角色关系概述：{relationship_summary}
题材类型：{genre}
故事基调：{tone}

请生成包含以下内容的大纲：

1. **标题和前提**：作品标题及核心设定
2. **章节大纲**：至少 5-8 章的详细大纲，每章包含：
   - 章节标题
   - 章节摘要
   - 涉及角色
   - 关键事件
3. **建议配对**：如果适合，可以建议角色配对
4. **内容警告**：如果涉及敏感内容，提供警告

请按以下 JSON 格式输出（只输出 JSON）：
{{
    "outline_title": "作品标题",
    "premise": "核心前提/设定",
    "chapters": [
        {{
            "chapter_title": "第一章：标题",
            "summary": "章节摘要",
            "involved_characters": ["角色1", "角色2"],
            "key_events": ["事件1", "事件2"]
        }}
    ],
    "suggested_pairings": ["配对1", "配对2"],
    "warnings": ["警告内容"]
}}"""

    def __init__(self, llm: BaseLLMService):
        self.llm = llm

    async def import_fandom_settings(
        self,
        project_id: str,
        source_text: str,
        source_title: str = "",
        fandom_domain: Optional[str] = None,
    ) -> dict:
        """导入已有 IP 设定（AI 分析原著文本提取）

        Args:
            project_id: 项目 ID
            source_text: 原文小说文本
            source_title: 原作标题
            fandom_domain: 同人领域标签

        Returns:
            dict: 提取的角色/世界观/风格等信息
        """
        import json

        # 如果有领域标签，在提示词中强调
        domain_hint = f"\n\n注意：这是 {fandom_domain} 同人创作，请考虑该领域的特色。" if fandom_domain else ""

        prompt = self.IMPORT_TEMPLATE.format(source_text=source_text) + domain_hint

        raw = await self.llm.generate(prompt)

        try:
            # 尝试解析 JSON
            try:
                result = json.loads(raw)
            except json.JSONDecodeError:
                # 尝试从代码块中提取
                import re
                match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
                if match:
                    result = json.loads(match.group(1))
                else:
                    # 尝试找 JSON 对象
                    match = re.search(r"(\{.*\})", raw, re.DOTALL)
                    if match:
                        result = json.loads(match.group(1))
                    else:
                        raise ValueError("无法解析 LLM 输出")

            # 验证必需字段
            required_fields = ["characters", "relationships", "world_settings", "narrative_style"]
            for field in required_fields:
                if field not in result:
                    result[field] = [] if field in ["characters", "relationships", "world_settings"] else ""

            return result

        except Exception as e:
            # 返回错误信息，不中断流程
            return {
                "characters": [],
                "relationships": [],
                "world_settings": [],
                "narrative_style": "",
                "writing_suggestions": [],
                "_error": f"解析失败: {str(e)}",
                "_raw": raw[:1000]
            }

    async def generate_fandom_outline(
        self,
        project_id: str,
        fandom_name: str,
        character_ids: list[str],
        relationship_summary: str = "",
        genre: Optional[str] = None,
        tone: Optional[str] = None,
    ) -> dict:
        """为同人创作生成大纲建议

        Args:
            project_id: 项目 ID
            fandom_name: 同人作品名称
            character_ids: 使用的角色 ID 列表
            relationship_summary: 角色关系概述
            genre: 题材类型
            tone: 故事基调

        Returns:
            dict: 大纲建议
        """
        import json

        # 如果传入了角色 ID，可以获取角色信息来增强提示词
        # 这里暂时使用 ID 列表，实际使用时可以查询数据库获取角色名
        character_names = ", ".join(character_ids) if character_ids else "待定"
        genre = genre or "待定"
        tone = tone or "待定"

        prompt = self.OUTLINE_TEMPLATE.format(
            fandom_name=fandom_name,
            character_names=character_names,
            relationship_summary=relationship_summary or "待定",
            genre=genre,
            tone=tone,
        )

        raw = await self.llm.generate(prompt)

        try:
            try:
                result = json.loads(raw)
            except json.JSONDecodeError:
                import re
                match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
                if match:
                    result = json.loads(match.group(1))
                else:
                    match = re.search(r"(\{.*\})", raw, re.DOTALL)
                    if match:
                        result = json.loads(match.group(1))
                    else:
                        raise ValueError("无法解析 LLM 输出")

            # 确保字段存在
            if "chapters" not in result:
                result["chapters"] = []
            if "suggested_pairings" not in result:
                result["suggested_pairings"] = []
            if "warnings" not in result:
                result["warnings"] = []

            return result

        except Exception as e:
            return {
                "outline_title": fandom_name,
                "premise": "",
                "chapters": [],
                "suggested_pairings": [],
                "warnings": [],
                "_error": f"解析失败: {str(e)}",
                "_raw": raw[:1000]
            }
