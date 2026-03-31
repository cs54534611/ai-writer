"""Review 请求/响应 Schema"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReviewIssueSchema(BaseModel):
    """审查问题"""
    type: str = Field(description="问题类型: 'contradiction' | 'ooc' | 'sensitive'")
    severity: str = Field(description="严重程度: 'low' | 'medium' | 'high'")
    location: str = Field(description="问题位置描述")
    description: str = Field(description="问题描述")
    suggestion: str = Field(description="修改建议")


class ReviewResultSchema(BaseModel):
    """审查结果"""
    score: float = Field(ge=0.0, le=10.0, description="综合评分 0.0-10.0")
    issues: list[ReviewIssueSchema] = Field(default_factory=list, description="问题列表")
    stats: dict = Field(default_factory=dict, description="统计信息：字数/章节数/角色数等")


class SensitiveWordCheckRequest(BaseModel):
    """敏感词检测请求"""
    content: str = Field(min_length=1, description="待检测内容")
    custom_words: Optional[list[str]] = Field(default=None, description="自定义敏感词列表")
    check_political: bool = Field(default=True, description="是否检测涉政词汇")
    check_adult: bool = Field(default=True, description="是否检测涉黄词汇")
    check_violence: bool = Field(default=True, description="是否检测涉暴词汇")


class ChapterReviewRequest(BaseModel):
    """章节审查请求"""
    chapter_content: str = Field(min_length=1, description="章节内容")
    chapter_id: str = Field(description="章节ID")


class ContradictionCheckRequest(BaseModel):
    """矛盾检测请求"""
    new_content: str = Field(min_length=1, description="新内容")
    existing_content: str = Field(default="", description="已有内容（用于对比）")


class OOCCheckRequest(BaseModel):
    """OOC检测请求"""
    content: str = Field(min_length=1, description="待检测内容")
    character_id: str = Field(description="角色ID")


class FullReviewRequest(BaseModel):
    """全量审查请求"""
    chapter_id: str = Field(description="章节ID")
