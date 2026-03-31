"""角色别名自动合并服务"""

import jieba
import jieba.analyse
import re
from typing import Optional


class AliasMerger:
    """角色别名自动合并服务"""

    def __init__(self):
        # jieba 已经初始化（避免重复加载）
        pass

    def extract_aliases(self, character_name: str, description: str) -> list[str]:
        """
        从角色描述中提取可能的别名
        
        Args:
            character_name: 角色正式名称
            description: 角色描述文本
        
        Returns:
            list[str]: 提取的别名列表，包含正式名和可能的别名
        """
        if not description:
            return [character_name]
        
        # 结果列表
        aliases = [character_name]
        
        # 1. 尝试提取 "XX（又称XX）"、"XX，又名XX"、"XX，尊称XX" 等模式
        alias_patterns = [
            r'又称[为]?([^，,。\n]+)',
            r'又名[为]?([^，,。\n]+)',
            r'尊称[为]?([^，,。\n]+)',
            r'绰号[为]?([^，,。\n]+)',
            r'外号[为]?([^，,。\n]+)',
            r'人称[为]?([^，,。\n]+)',
            r'江湖人称[为]?([^，,。\n]+)',
            r'自号([^，,。\n]+)',
            r'号([^，,。\n]+)',
            r'世称([^，,。\n]+)',
            r'封号([^，,。\n]+)',
            r'谥号([^，,。\n]+)',
        ]
        
        for pattern in alias_patterns:
            matches = re.findall(pattern, description)
            for match in matches:
                alias = match.strip()
                # 过滤太短或太长的别名
                if 1 < len(alias) < 10 and alias not in aliases:
                    aliases.append(alias)
        
        # 2. 用 jieba 词性标注识别人名模式
        words = jieba.posseg.cut(description)
        for word, flag in words:
            # 识别人名模式（nr 标签表示人名）
            if flag == 'nr' and len(word) >= 2:
                # 过滤掉和正式名完全相同的
                if word != character_name and word not in aliases:
                    aliases.append(word)
        
        # 3. 识别昵称/称谓模式
        nickname_patterns = [
            r'["""]([^"""]+)["""]',  # "xxx" 引号内
            r'[‘’]([^‘’]+)['']',  # 'xxx' 单引号内
        ]
        
        for pattern in nickname_patterns:
            matches = re.findall(pattern, description)
            for match in matches:
                nickname = match.strip()
                if 1 < len(nickname) < 10 and nickname != character_name and nickname not in aliases:
                    aliases.append(nickname)
        
        # 去重
        seen = set()
        unique_aliases = []
        for a in aliases:
            if a not in seen:
                seen.add(a)
                unique_aliases.append(a)
        
        return unique_aliases

    def merge_similar_characters(self, characters: list[dict]) -> list[dict]:
        """
        识别可能是同一个人的角色，返回合并建议
        
        Args:
            characters: 角色列表，每个角色包含 name, description 等字段
        
        Returns:
            list[dict]: 合并建议列表，每项包含 original, alias, confidence, reason
        """
        if len(characters) < 2:
            return []
        
        merge_suggestions = []
        
        # 为每个角色提取别名
        character_aliases: dict[int, list[str]] = {}
        for i, char in enumerate(characters):
            name = char.get("name", "")
            desc = char.get("description", "") or ""
            character_aliases[i] = self.extract_aliases(name, desc)
        
        # 比较每对角色
        for i in range(len(characters)):
            for j in range(i + 1, len(characters)):
                char_a = characters[i]
                char_b = characters[j]
                
                name_a = char_a.get("name", "")
                name_b = char_b.get("name", "")
                aliases_a = character_aliases[i]
                aliases_b = character_aliases[j]
                
                # 计算相似度
                common_aliases = set(aliases_a) & set(aliases_b)
                
                # 如果有共同别名
                if len(common_aliases) > 0:
                    confidence = min(0.9, 0.5 + 0.2 * len(common_aliases))
                    merge_suggestions.append({
                        "original": char_a,
                        "alias": char_b,
                        "confidence": confidence,
                        "reason": f"发现共同名称/别名: {', '.join(common_aliases)}",
                        "common_aliases": list(common_aliases),
                    })
                    continue
                
                # 检查描述中的共同关键词
                desc_a = char_a.get("description", "") or ""
                desc_b = char_b.get("description", "") or ""
                
                if desc_a and desc_b:
                    # 用 jieba 提取关键词
                    keywords_a = set(jieba.analyse.extract_tags(desc_a, topK=10, withWeight=False))
                    keywords_b = set(jieba.analyse.extract_tags(desc_b, topK=10, withWeight=False))
                    
                    # 共同关键词（排除人名）
                    common_keywords = keywords_a & keywords_b - {name_a, name_b}
                    
                    # 识别可能的关系词（师父/徒弟/师兄等）
                    relation_words = {"师父", "徒弟", "师兄", "师弟", "师姐", "师妹", "掌门", "帮主", "长老", "弟子", "师傅", "徒儿", "同道", "故人", "旧友"}
                    relationship_indicators = common_keywords & relation_words
                    
                    if relationship_indicators:
                        # 有关系词但不直接相关，可能是同一人
                        confidence = 0.4
                        merge_suggestions.append({
                            "original": char_a,
                            "alias": char_b,
                            "confidence": confidence,
                            "reason": f"描述中存在可能的关联: {', '.join(relationship_indicators)}，可能为同一角色的不同视角描述",
                            "common_keywords": list(relationship_indicators),
                        })
                    elif len(common_keywords) >= 3:
                        # 有较多共同关键词
                        confidence = 0.3
                        merge_suggestions.append({
                            "original": char_a,
                            "alias": char_b,
                            "confidence": confidence,
                            "reason": f"描述中有较多共同特征词: {', '.join(list(common_keywords)[:5])}",
                            "common_keywords": list(common_keywords),
                        })
        
        # 按置信度排序
        merge_suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        
        # 过滤低置信度（<0.3）建议
        return [s for s in merge_suggestions if s["confidence"] >= 0.3]
