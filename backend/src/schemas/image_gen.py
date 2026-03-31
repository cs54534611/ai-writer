"""AI 插图生成 Schema"""

from pydantic import BaseModel, Field
from typing import Optional


class ImageGenRequest(BaseModel):
    """插图生成请求"""
    prompt: str = Field(min_length=1, description="生成提示词")
    style: str = Field(default="anime", description="风格: anime/realistic/ink/watercolor/cel_shading")
    size: str = Field(default="512x512", description="尺寸: 512x512/1024x1024")
    character_ids: list[str] = Field(default_factory=list, description="关联角色 ID，用于获取角色设定增强 prompt")
    negative_prompt: Optional[str] = Field(default=None, description="反向提示词")


class ImageGenResponse(BaseModel):
    """插图生成响应"""
    url: str = ""
    b64_json: str = ""  # base64 图片数据
    seed: int = 0
    provider: str = ""  # stable_diffusion / dall_e / qwen_vl


class CharacterImageRequest(BaseModel):
    """角色形象图生成请求"""
    character_id: str = Field(description="角色 ID")
    pose: Optional[str] = Field(default="standing", description="姿态: standing/sitting/action/dynamic")
    expression: Optional[str] = Field(default="neutral", description="表情: neutral/smiling/serious/etc")


class FandomImportRequest(BaseModel):
    """同人创作导入请求"""
    source_text: str = Field(min_length=10, description="原文小说文本")
    source_title: str = Field(default="", description="原作标题")
    fandom_domain: Optional[str] = Field(default=None, description="同人领域标签，如 哈利波特/原神 等")


class FandomCharacter(BaseModel):
    """同人角色"""
    name: str
    aliases: list[str] = Field(default_factory=list)
    personality: str = ""
    appearance: str = ""
    role: str = ""  # protagonist/antagonist/supporting


class FandomRelationship(BaseModel):
    """同人关系"""
    character1: str
    character2: str
    relationship_type: str  # friends/lovers/rivals/family/etc
    description: str = ""


class FandomWorldSetting(BaseModel):
    """同人世界观设定"""
    name: str
    description: str
    key_locations: list[str] = Field(default_factory=list)
    rules: list[str] = Field(default_factory=list)  # 世界规则


class FandomImportResult(BaseModel):
    """同人创作导入结果"""
    characters: list[FandomCharacter]
    relationships: list[FandomRelationship]
    world_settings: list[FandomWorldSetting]
    narrative_style: str  # 叙事风格
    writing_suggestions: list[str] = Field(default_factory=list)  # 创作建议


class FandomOutlineRequest(BaseModel):
    """同人创作大纲生成请求"""
    fandom_name: str = Field(description="同人作品名称")
    character_ids: list[str] = Field(description="使用的角色 ID 列表")
    relationship_summary: str = Field(default="", description="角色关系概述")
    genre: Optional[str] = Field(default=None, description="题材: romance/adventure/mystery/etc")
    tone: Optional[str] = Field(default=None, description="基调: light/dark/comedy/drama")


class FandomOutlineChapter(BaseModel):
    """同人章节大纲"""
    chapter_title: str
    summary: str
    involved_characters: list[str]
    key_events: list[str] = Field(default_factory=list)


class FandomOutlineResult(BaseModel):
    """同人创作大纲结果"""
    outline_title: str
    premise: str  # 前提/设定
    chapters: list[FandomOutlineChapter]
    suggested_pairings: list[str] = Field(default_factory=list)  # 建议的配对
    warnings: list[str] = Field(default_factory=list)  # 内容警告
