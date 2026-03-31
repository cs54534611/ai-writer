"""AI 世界地图生成服务 - 根据题材和设定生成世界结构"""

import uuid
from datetime import datetime

from src.services.llm import BaseLLMService


class MapGenerator:
    """AI 世界地图生成器"""

    # 题材对应的层级结构模板
    GENRE_TEMPLATES = {
        "修仙": {
            "upper": ["仙界", "神域", "天庭", "大罗天"],
            "middle": ["人间界", "世俗王朝", "修真界", "各大宗门"],
            "lower": ["冥界", "幽冥地府", "九幽深渊", "轮回之地"],
        },
        "玄幻": {
            "upper": ["神界", "圣域", "天界", "诸神国度"],
            "middle": ["大陆", "帝国", "王国", "各大势力"],
            "lower": ["深渊", "地狱", "魔域", "冥界"],
        },
        "都市": {
            "upper": ["权力巅峰", "金融中心", "上流社会"],
            "middle": ["城市中心", "商业区", "住宅区", "工业区"],
            "lower": ["地下世界", "贫民窟", "暗巷"],
        },
        "穿越": {
            "upper": ["异界神域", "仙灵空间", "上古遗迹"],
            "middle": ["异世界大陆", "王朝帝国", "宗门林立"],
            "lower": ["魔界", "幽冥界", "妖兽森林深处"],
        },
        "科幻": {
            "upper": ["星际联邦", "宇宙议会", "高维空间"],
            "middle": ["母星", "殖民星球", "空间站", "太空城市"],
            "lower": ["暗域", "虫洞深处", "外星巢穴"],
        },
        "奇幻": {
            "upper": ["神国", "精灵仙境", "龙域天空"],
            "middle": ["中土大陆", "矮人王国", "人类帝国", "兽人领地"],
            "lower": ["深渊地狱", "黑暗森林", "远古墓穴"],
        },
    }

    def __init__(self, llm: BaseLLMService):
        self.llm = llm

    async def generate_world_map(
        self,
        genre: str,
        settings: list[dict] = None,
    ) -> dict:
        """
        生成世界地图结构

        Args:
            genre: 题材类型（修仙/都市/玄幻/穿越/科幻/奇幻）
            settings: 世界设定列表

        Returns:
            dict: 世界地图结构，包含层级和地点
        """
        # 获取题材模板
        template = self.GENRE_TEMPLATES.get(genre, self.GENRE_TEMPLATES["玄幻"])

        # 构建设定摘要
        settings_text = ""
        if settings:
            settings_text = "\n\n已有世界设定：\n" + "\n".join([
                f"- {s.get('name', '')}: {s.get('content', '')[:100]}" 
                for s in settings if isinstance(s, dict)
            ])

        prompt = f"""你是一位专业的奇幻世界架构师。请根据以下信息生成一个完整的世界地图结构。

题材类型：{genre}
{settings_text}

请生成包含三个层级的世界结构：
1. 上层空间（如：{', '.join(template['upper'][:3])}）
2. 中层空间（如：{', '.join(template['middle'][:3])}）
3. 下层空间（如：{', '.join(template['lower'][:3])}）

每个层级需要包含：
- 层级名称
- 重要地点列表（每个地点包含：名称、描述、特点）
- 层级之间的通道/联系

请按以下 JSON 格式输出：
{{
    "world_map": {{
        "genre": "{genre}",
        "upper_realm": {{
            "name": "上层空间名称",
            "description": "整体描述",
            "locations": [
                {{
                    "name": "地点名称",
                    "description": "地点描述",
                    "features": ["特点1", "特点2"]
                }}
            ]
        }},
        "middle_realm": {{
            "name": "中层空间名称",
            "description": "整体描述",
            "locations": [
                {{
                    "name": "地点名称",
                    "description": "地点描述",
                    "features": ["特点1", "特点2"]
                }}
            ]
        }},
        "lower_realm": {{
            "name": "下层空间名称",
            "description": "整体描述",
            "locations": [
                {{
                    "name": "地点名称",
                    "description": "地点描述",
                    "features": ["特点1", "特点2"]
                }}
            ]
        }},
        "connections": [
            {{
                "from": "起点",
                "to": "终点",
                "description": "连接描述"
            }}
        ]
    }},
    "notes": "额外说明（如有）"
}}

请直接输出 JSON，只输出 JSON："""

        raw = await self.llm.generate(prompt)

        # 解析 JSON 响应
        try:
            import json as _json
            import re
            
            # 尝试从响应中提取 JSON
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                result = _json.loads(match.group())
                return result
        except Exception:
            pass

        # 降级方案：返回默认结构
        return self._generate_default_map(genre, template)

    def _generate_default_map(
        self, genre: str, template: dict
    ) -> dict:
        """生成默认的世界地图结构"""
        return {
            "world_map": {
                "genre": genre,
                "upper_realm": {
                    "name": "上层空间",
                    "description": f"{genre}世界的上层领域",
                    "locations": [
                        {"name": loc, "description": f"{loc}简介", "features": ["神秘", "高维"]}
                        for loc in template["upper"]
                    ],
                },
                "middle_realm": {
                    "name": "中层空间",
                    "description": f"{genre}世界的主要舞台",
                    "locations": [
                        {"name": loc, "description": f"{loc}简介", "features": ["繁华", "机遇"]}
                        for loc in template["middle"]
                    ],
                },
                "lower_realm": {
                    "name": "下层空间",
                    "description": f"{genre}世界的阴暗面",
                    "locations": [
                        {"name": loc, "description": f"{loc}简介", "features": ["危险", "未知"]}
                        for loc in template["lower"]
                    ],
                },
                "connections": [
                    {"from": "上层空间", "to": "中层空间", "description": "垂直通道"},
                    {"from": "中层空间", "to": "下层空间", "description": "垂直通道"},
                ],
            },
            "notes": "使用默认模板生成",
        }

    async def generate_location_details(
        self,
        location: dict,
        genre: str,
    ) -> dict:
        """
        生成地点的详细信息

        Args:
            location: 地点基本信息（name, description, features）
            genre: 题材类型

        Returns:
            dict: 地点详细信息
        """
        prompt = f"""你是一位专业的奇幻世界架构师。请为以下地点生成详细信息。

地点名称：{location.get('name', '')}
现有描述：{location.get('description', '')}
特点：{', '.join(location.get('features', []))}
题材类型：{genre}

请生成：
1. 详细描述（200-300字）
2. 历史背景
3. 重要NPC或势力
4. 可探索内容
5. 与其他地点的联系

请按以下 JSON 格式输出：
{{
    "detailed_description": "详细描述",
    "history": "历史背景",
    "npcs": ["NPC1", "NPC2"],
    "factions": ["势力1", "势力2"],
    "explorable": ["可探索点1", "可探索点2"],
    "connections": ["联系地点1", "联系地点2"]
}}

请直接输出 JSON："""

        raw = await self.llm.generate(prompt)

        try:
            import json as _json
            import re
            
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                return _json.loads(match.group())
        except Exception:
            pass

        return {"error": "生成失败"}
