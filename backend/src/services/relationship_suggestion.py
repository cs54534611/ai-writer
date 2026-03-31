"""AI 关系建议服务 - 根据两个角色的背景信息建议最合适的关系类型"""

import json
from typing import Optional

from src.services.llm import LLMService


class RelationshipSuggestionService:
    """AI 关系建议服务"""
    
    # 关系类型及其特征描述
    RELATIONSHIP_TYPES = {
        "师徒": "师父-徒弟，传承关系，通常有技艺传授",
        "父子": "父亲-儿子，血缘至亲",
        "母子": "母亲-子女，血缘至亲",
        "兄弟": "兄弟关系，同辈男性血缘",
        "姐妹": "姐妹关系，同辈女性血缘",
        "兄妹": "兄妹或姐弟，同辈血缘",
        "恋人": "恋人/情侣，浪漫情感关系",
        "配偶": "夫妻，正式婚姻关系",
        "暗恋": "单方面暗恋，未表白的关系",
        "仇敌": "仇恨关系，互相敌视",
        "竞争对手": "竞争关系，对立但非仇恨",
        "宿敌": "长期对抗的敌人，命中注定对立",
        "主仆": "主人-仆人，主人-随从的依附关系",
        "主从": "主公-臣子，古代政治从属",
        "结拜": "结拜兄弟/姐妹，非血缘的义气关系",
        "同门": "同门师兄弟，共同师承",
        "知己": "挚友/知己，深刻理解和信任",
        "青梅竹马": "从小一起长大的朋友/恋人",
        "义兄": "义兄，非血缘的兄长关系",
        "义妹": "义妹，非血缘的妹妹关系",
        "义父": "养父，非血缘的父亲关系",
        "义母": "养母，非血缘的母亲关系",
        "恩人": "曾施恩于己的人",
        "救命恩人": "救过自己性命的人",
        "上下级": "工作或组织中的上下级关系",
        "雇佣": "雇主-雇员关系",
        "前任": "曾经的情侣，现已分开",
        "闺蜜": "亲密的女性朋友",
        "铁哥们": "亲密的男性朋友",
        "合伙人": "商业或事业伙伴",
    }
    
    def __init__(self, llm: Optional[LLMService] = None):
        """初始化关系建议服务
        
        Args:
            llm: LLM 服务实例，如果为 None 则使用默认实例
        """
        self._llm = llm
    
    @property
    def llm(self) -> LLMService:
        """获取 LLM 服务实例"""
        if self._llm is None:
            self._llm = LLMService()
        return self._llm
    
    async def suggest_relationship(
        self, 
        char1_profile: dict, 
        char2_profile: dict
    ) -> dict:
        """根据两个角色的背景信息建议最合适的关系类型
        
        Args:
            char1_profile: 角色1的 profile 字典，包含 name, background, personality 等
            char2_profile: 角色2的 profile 字典，包含 name, background, personality 等
        
        Returns:
            dict: {
                "suggested_type": str,  # 建议的关系类型
                "reason": str,          # 建议理由
                "confidence": float,   # 置信度 0-1
                "alternatives": list   # 其他可能的关系类型及置信度
            }
        """
        char1_name = char1_profile.get("name", "角色1")
        char1_background = char1_profile.get("background", char1_profile.get("description", ""))
        char1_personality = char1_profile.get("personality", "")
        
        char2_name = char2_profile.get("name", "角色2")
        char2_background = char2_profile.get("background", char2_profile.get("description", ""))
        char2_personality = char2_profile.get("personality", "")
        
        # 构建提示词
        relationship_types_text = "\n".join(
            f"- {rel_type}: {desc}" 
            for rel_type, desc in self.RELATIONSHIP_TYPES.items()
        )
        
        prompt = f"""你是一个专业的网文关系设定助手。请分析以下两个角色的背景信息，建议最合适的关系类型。

角色1: {char1_name}
背景: {char1_background}
性格: {char1_personality}

角色2: {char2_name}
背景: {char2_background}
性格: {char2_personality}

可选的关系类型:
{relationship_types_text}

请分析两个角色的背景、性格、以及可能的互动场景，推荐最合适的关系类型。

请以 JSON 格式返回结果:
{{
    "suggested_type": "推荐的关系类型",
    "reason": "推荐理由，说明为什么这种关系最合适",
    "confidence": 0.85,
    "alternatives": [
        {{"type": "备选类型1", "confidence": 0.6, "reason": "备选理由"}},
        {{"type": "备选类型2", "confidence": 0.3, "reason": "备选理由"}}
    ]
}}

confidence 表示置信度，0-1 之间，1 表示非常确定。
只返回 JSON，不要有其他内容。"""
        
        try:
            response = await self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                model="auto",
                temperature=0.3,  # 低温度以获得更确定的结果
            )
            
            # 解析 JSON 响应
            content = response.get("content", "{}")
            
            # 尝试提取 JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            result = json.loads(content)
            
            # 验证结果
            if "suggested_type" not in result:
                raise ValueError("Invalid response format")
            
            # 确保推荐的关系类型在枚举中
            suggested = result["suggested_type"]
            if suggested not in self.RELATIONSHIP_TYPES:
                # 尝试模糊匹配
                for rel_type in self.RELATIONSHIP_TYPES:
                    if suggested in rel_type or rel_type in suggested:
                        result["suggested_type"] = rel_type
                        break
                else:
                    # 默认使用"知己"
                    result["suggested_type"] = "知己"
            
            return result
            
        except Exception as e:
            # 如果 AI 分析失败，使用基于规则的简单建议
            return await self._fallback_suggestion(char1_profile, char2_profile)
    
    async def _fallback_suggestion(
        self, 
        char1_profile: dict, 
        char2_profile: dict
    ) -> dict:
        """基于规则的备选建议逻辑
        
        当 LLM 分析失败时使用
        """
        char1_background = char1_profile.get("background", "").lower()
        char2_background = char2_profile.get("background", "").lower()
        
        # 检查关键词来建议关系
        keywords_map = {
            "师徒": ["师父", "徒弟", "传授", "学艺", "门下"],
            "父子": ["父亲", "儿子", "父亲", "亲子"],
            "恋人": ["恋人", "相爱", "情", "爱"],
            "兄弟": ["兄弟", "兄长", "弟弟", "兄长"],
            "知己": ["知己", "挚友", "信任", "了解"],
            "恩人": ["恩人", "救命", "相助", "报答"],
            "青梅竹马": ["长大", "从小", "相识", "童年"],
        }
        
        best_match = None
        best_score = 0
        
        for rel_type, keywords in keywords_map.items():
            score = 0
            for kw in keywords:
                if kw in char1_background:
                    score += 1
                if kw in char2_background:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = rel_type
        
        if best_match and best_score > 0:
            return {
                "suggested_type": best_match,
                "reason": "基于角色背景关键词分析",
                "confidence": 0.5,
                "alternatives": []
            }
        
        # 默认返回知己
        return {
            "suggested_type": "知己",
            "reason": "无法确定具体关系，默认推荐知己",
            "confidence": 0.3,
            "alternatives": []
        }


# 全局服务实例
_relationship_suggestion_service: Optional[RelationshipSuggestionService] = None


def get_relationship_suggestion_service() -> RelationshipSuggestionService:
    """获取关系建议服务实例"""
    global _relationship_suggestion_service
    if _relationship_suggestion_service is None:
        _relationship_suggestion_service = RelationshipSuggestionService()
    return _relationship_suggestion_service
