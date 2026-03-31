"""敏感词模型 - 合规检测"""

import uuid
from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel


class SensitiveLevel(str, Enum):
    """敏感词级别"""
    HINT = "hint"       # 提示级别
    WARNING = "warning" # 警告级别
    HIGH = "high"       # 高危级别


class SensitiveCategory(str, Enum):
    """敏感词类别"""
    POLITICAL = "political"     # 涉政
    ADULT = "adult"             # 涉黄
    VIOLENCE = "violence"       # 涉暴
    CUSTOM = "custom"           # 自定义


class SensitiveWordBase(SQLModel):
    """敏感词基础字段"""
    word: str = Field(
        max_length=100,
        description="敏感词",
    )
    level: SensitiveLevel = Field(
        default=SensitiveLevel.WARNING,
        description="敏感级别",
    )
    category: SensitiveCategory = Field(
        default=SensitiveCategory.CUSTOM,
        description="敏感词类别",
    )


class SensitiveWord(SensitiveWordBase, table=True):
    """敏感词数据库模型"""
    __tablename__ = "sensitive_words"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        max_length=36,
    )
    project_id: str = Field(
        max_length=36,
        index=True,
        description="项目ID",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="创建时间",
    )

    class Config:
        use_enum_values = True


# 内置默认敏感词库
DEFAULT_SENSITIVE_WORDS = [
    # 涉政敏感词 (30+)
    {"word": "共产党", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.POLITICAL},
    {"word": "国民党", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.POLITICAL},
    {"word": "民主", "level": SensitiveLevel.WARNING, "category": SensitiveCategory.POLITICAL},
    {"word": "人权", "level": SensitiveLevel.WARNING, "category": SensitiveCategory.POLITICAL},
    {"word": "六四", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.POLITICAL},
    {"word": "天安门", "level": SensitiveLevel.WARNING, "category": SensitiveCategory.POLITICAL},
    {"word": "文革", "level": SensitiveLevel.WARNING, "category": SensitiveCategory.POLITICAL},
    {"word": "大跃进", "level": SensitiveLevel.WARNING, "category": SensitiveCategory.POLITICAL},
    {"word": "反革命", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.POLITICAL},
    {"word": "颠覆", "level": SensitiveLevel.WARNING, "category": SensitiveCategory.POLITICAL},
    {"word": "分裂", "level": SensitiveLevel.WARNING, "category": SensitiveCategory.POLITICAL},
    {"word": "台独", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.POLITICAL},
    {"word": "藏独", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.POLITICAL},
    {"word": "疆独", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.POLITICAL},
    {"word": "港独", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.POLITICAL},
    {"word": "钓鱼岛", "level": SensitiveLevel.WARNING, "category": SensitiveCategory.POLITICAL},
    {"word": "南海", "level": SensitiveLevel.HINT, "category": SensitiveCategory.POLITICAL},
    {"word": "主权", "level": SensitiveLevel.HINT, "category": SensitiveCategory.POLITICAL},
    {"word": "领土", "level": SensitiveLevel.HINT, "category": SensitiveCategory.POLITICAL},
    {"word": "国家领导人", "level": SensitiveLevel.WARNING, "category": SensitiveCategory.POLITICAL},
    {"word": "总书记", "level": SensitiveLevel.WARNING, "category": SensitiveCategory.POLITICAL},
    {"word": "国家主席", "level": SensitiveLevel.WARNING, "category": SensitiveCategory.POLITICAL},
    {"word": "总理", "level": SensitiveLevel.HINT, "category": SensitiveCategory.POLITICAL},
    {"word": "主席", "level": SensitiveLevel.HINT, "category": SensitiveCategory.POLITICAL},
    {"word": "总统", "level": SensitiveLevel.HINT, "category": SensitiveCategory.POLITICAL},
    {"word": "政府", "level": SensitiveLevel.HINT, "category": SensitiveCategory.POLITICAL},
    {"word": "法院", "level": SensitiveLevel.HINT, "category": SensitiveCategory.POLITICAL},
    {"word": "检察院", "level": SensitiveLevel.HINT, "category": SensitiveCategory.POLITICAL},
    {"word": "公安局", "level": SensitiveLevel.HINT, "category": SensitiveCategory.POLITICAL},
    {"word": "军队", "level": SensitiveLevel.HINT, "category": SensitiveCategory.POLITICAL},
    {"word": "武警", "level": SensitiveLevel.WARNING, "category": SensitiveCategory.POLITICAL},
    {"word": "坦克", "level": SensitiveLevel.WARNING, "category": SensitiveCategory.POLITICAL},
    
    # 涉黄敏感词 (20+)
    {"word": "色情", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.ADULT},
    {"word": "淫秽", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.ADULT},
    {"word": "黄色", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.ADULT},
    {"word": "性感", "level": SensitiveLevel.WARNING, "category": SensitiveCategory.ADULT},
    {"word": "裸体", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.ADULT},
    {"word": "裸露", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.ADULT},
    {"word": "性行为", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.ADULT},
    {"word": "性交", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.ADULT},
    {"word": "做爱", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.ADULT},
    {"word": "强奸", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.ADULT},
    {"word": "猥亵", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.ADULT},
    {"word": "嫖娼", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.ADULT},
    {"word": "卖淫", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.ADULT},
    {"word": "妓女", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.ADULT},
    {"word": "AV女优", "level": SensitiveLevel.WARNING, "category": SensitiveCategory.ADULT},
    {"word": "成人电影", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.ADULT},
    {"word": "成人网站", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.ADULT},
    {"word": "激情视频", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.ADULT},
    {"word": "露点", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.ADULT},
    {"word": "三点式", "level": SensitiveLevel.WARNING, "category": SensitiveCategory.ADULT},
    {"word": "比基尼", "level": SensitiveLevel.HINT, "category": SensitiveCategory.ADULT},
    {"word": "内衣", "level": SensitiveLevel.HINT, "category": SensitiveCategory.ADULT},
    
    # 涉暴敏感词 (20+)
    {"word": "杀人", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.VIOLENCE},
    {"word": "谋杀", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.VIOLENCE},
    {"word": "死亡", "level": SensitiveLevel.WARNING, "category": SensitiveCategory.VIOLENCE},
    {"word": "尸体", "level": SensitiveLevel.WARNING, "category": SensitiveCategory.VIOLENCE},
    {"word": "血", "level": SensitiveLevel.HINT, "category": SensitiveCategory.VIOLENCE},
    {"word": "血腥", "level": SensitiveLevel.WARNING, "category": SensitiveCategory.VIOLENCE},
    {"word": "暴力", "level": SensitiveLevel.WARNING, "category": SensitiveCategory.VIOLENCE},
    {"word": "虐待", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.VIOLENCE},
    {"word": "酷刑", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.VIOLENCE},
    {"word": "折磨", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.VIOLENCE},
    {"word": "斩首", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.VIOLENCE},
    {"word": "肢解", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.VIOLENCE},
    {"word": "爆炸", "level": SensitiveLevel.WARNING, "category": SensitiveCategory.VIOLENCE},
    {"word": "炸弹", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.VIOLENCE},
    {"word": "恐怖分子", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.VIOLENCE},
    {"word": "袭击", "level": SensitiveLevel.WARNING, "category": SensitiveCategory.VIOLENCE},
    {"word": "枪战", "level": SensitiveLevel.WARNING, "category": SensitiveCategory.VIOLENCE},
    {"word": "武器", "level": SensitiveLevel.HINT, "category": SensitiveCategory.VIOLENCE},
    {"word": "匕首", "level": SensitiveLevel.HINT, "category": SensitiveCategory.VIOLENCE},
    {"word": "菜刀", "level": SensitiveLevel.HINT, "category": SensitiveCategory.VIOLENCE},
    {"word": "砍死", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.VIOLENCE},
    {"word": "捅死", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.VIOLENCE},
    {"word": "勒死", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.VIOLENCE},
    {"word": "毒药", "level": SensitiveLevel.WARNING, "category": SensitiveCategory.VIOLENCE},
    {"word": "下毒", "level": SensitiveLevel.HIGH, "category": SensitiveCategory.VIOLENCE},
]
