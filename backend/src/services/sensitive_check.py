"""敏感词检测服务"""

import re
from typing import Optional
from dataclasses import dataclass

from src.models.sensitive_word import (
    DEFAULT_SENSITIVE_WORDS,
    SensitiveLevel,
    SensitiveCategory,
)


@dataclass
class SensitiveMatch:
    """敏感词匹配结果"""
    word: str           # 匹配到的敏感词
    level: str          # 级别: hint/warning/high
    category: str       # 类别: political/adult/violence/custom
    position: int       # 匹配位置（字符索引）
    length: int         # 匹配长度


class SensitiveCheckService:
    """敏感词检测服务"""

    def __init__(self, custom_words: Optional[list[dict]] = None):
        """
        初始化检测服务
        
        Args:
            custom_words: 自定义敏感词列表，每项包含 word, level, category
        """
        # 构建敏感词库（内置 + 自定义）
        self.words: list[dict] = list(DEFAULT_SENSITIVE_WORDS)
        if custom_words:
            self.words.extend(custom_words)
        
        # 构建用于高效匹配的字典（按类别和级别组织）
        self._build_index()

    def _build_index(self):
        """构建敏感词索引以提高匹配效率"""
        # 按长度组织，长词优先匹配
        self._words_by_length: dict[int, list[dict]] = {}
        for item in self.words:
            length = len(item["word"])
            if length not in self._words_by_length:
                self._words_by_length[length] = []
            self._words_by_length[length].append(item)
        
        # 按类别和级别组织的集合，用于快速查找
        self._word_sets: dict[str, set[str]] = {}
        for item in self.words:
            key = f"{item['category']}:{item['level']}"
            if key not in self._word_sets:
                self._word_sets[key] = set()
            self._word_sets[key].add(item["word"])
        
        # 所有敏感词集合（用于快速判断）
        self._all_words = {item["word"] for item in self.words}
        
        # 构建正则表达式模式（处理同义词检测）
        self._patterns: list[tuple[re.Pattern, dict]] = []
        for item in self.words:
            # 转义特殊字符，构造单词边界匹配
            escaped = re.escape(item["word"])
            pattern = re.compile(escaped)
            self._patterns.append((pattern, item))

    def check_content(self, content: str) -> list[dict]:
        """
        检测内容中的敏感词
        
        Args:
            content: 待检测的文本内容
        
        Returns:
            list[dict]: 所有匹配的敏感词及其信息
            [
                {
                    "word": "敏感词",
                    "level": "warning",
                    "category": "political",
                    "position": 10,
                    "length": 3
                },
                ...
            ]
        """
        if not content:
            return []
        
        matches: list[SensitiveMatch] = []
        
        for pattern, item in self._patterns:
            for match in pattern.finditer(content):
                sensitive_word = item["word"]
                matches.append(SensitiveMatch(
                    word=sensitive_word,
                    level=item["level"],
                    category=item["category"],
                    position=match.start(),
                    length=len(sensitive_word),
                ))
        
        # 按位置排序
        matches.sort(key=lambda x: x.position)
        
        # 去重（同一个位置只保留最高级别的）
        deduplicated = self._deduplicate_matches(matches)
        
        return [
            {
                "word": m.word,
                "level": m.level,
                "category": m.category,
                "position": m.position,
                "length": m.length,
            }
            for m in deduplicated
        ]

    def _deduplicate_matches(self, matches: list[SensitiveMatch]) -> list[SensitiveMatch]:
        """去除重叠的匹配，保留最高级别的"""
        if not matches:
            return []
        
        deduplicated: list[SensitiveMatch] = []
        last_end = -1
        
        for match in matches:
            if match.position >= last_end:
                deduplicated.append(match)
                last_end = match.position + match.length
        
        return deduplicated

    def check_and_report(self, content: str) -> dict:
        """
        检测内容并生成报告
        
        Args:
            content: 待检测的文本内容
        
        Returns:
            dict: 检测报告
            {
                "has_sensitive": True/False,
                "total_count": 5,
                "by_level": {"hint": 2, "warning": 2, "high": 1},
                "by_category": {"political": 3, "adult": 1, "violence": 1},
                "matches": [...],
                "risk_level": "high/warning/hint/safe"
            }
        """
        matches = self.check_content(content)
        
        if not matches:
            return {
                "has_sensitive": False,
                "total_count": 0,
                "by_level": {"hint": 0, "warning": 0, "high": 0},
                "by_category": {"political": 0, "adult": 0, "violence": 0, "custom": 0},
                "matches": [],
                "risk_level": "safe",
            }
        
        # 统计各级别数量
        by_level = {"hint": 0, "warning": 0, "high": 0}
        by_category = {"political": 0, "adult": 0, "violence": 0, "custom": 0}
        
        for m in matches:
            by_level[m.level] = by_level.get(m.level, 0) + 1
            by_category[m.category] = by_category.get(m.category, 0) + 1
        
        # 判断整体风险等级
        risk_level = "safe"
        if by_level["high"] > 0:
            risk_level = "high"
        elif by_level["warning"] > 0:
            risk_level = "warning"
        elif by_level["hint"] > 0:
            risk_level = "hint"
        
        return {
            "has_sensitive": True,
            "total_count": len(matches),
            "by_level": by_level,
            "by_category": by_category,
            "matches": matches,
            "risk_level": risk_level,
        }

    def highlight_sensitive(self, content: str) -> str:
        """
        在内容中高亮敏感词
        
        Args:
            content: 待检测的文本内容
        
        Returns:
            str: 高亮后的文本，敏感词用 **word** 包裹
        """
        matches = self.check_content(content)
        if not matches:
            return content
        
        # 从后向前替换，避免位置偏移问题
        result = content
        offset = 0
        
        for match in reversed(matches):
            start = match["position"]
            end = start + match["length"]
            highlighted = f"**{match['word']}**"
            result = result[:start + offset] + highlighted + result[end + offset:]
            offset += len(highlighted) - match["length"]
        
        return result


# 全局服务实例（无自定义词库，使用内置默认词库）
_default_service: Optional[SensitiveCheckService] = None


def get_sensitive_check_service(custom_words: Optional[list[dict]] = None) -> SensitiveCheckService:
    """获取敏感词检测服务实例"""
    global _default_service
    if _default_service is None or custom_words is not None:
        return SensitiveCheckService(custom_words)
    return _default_service


def check_content(content: str) -> list[dict]:
    """快捷函数：检测内容中的敏感词"""
    service = get_sensitive_check_service()
    return service.check_content(content)


def check_and_report(content: str) -> dict:
    """快捷函数：检测内容并生成报告"""
    service = get_sensitive_check_service()
    return service.check_and_report(content)
