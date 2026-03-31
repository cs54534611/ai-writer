"""Relationship 请求/响应 Schema"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RelationType(str, Enum):
    """中文网文关系类型枚举"""
    # 师徒/传承
    MASTER_DISCIPLE = "师徒"           # 师父-徒弟
    
    # 血缘/家庭
    FATHER_SON = "父子"               # 父亲-儿子
    MOTHER_CHILD = "母子"             # 母亲-子女
    BROTHER = "兄弟"                  # 兄弟
    SISTER = "姐妹"                   # 姐妹
    SIBLING = "兄妹"                  # 兄妹/姐弟
    
    # 情感
    LOVER = "恋人"                   # 恋人/情侣
    SPOUSE = "配偶"                   # 夫妻
    CRUSH = "暗恋"                    # 暗恋对象
    
    # 对立
    ENEMY = "仇敌"                   # 仇人/敌人
    RIVAL = "竞争对手"               # 竞争对手
    NEMESIS = "宿敌"                 # 宿敌
    
    # 依附/从属
    MASTER_SERVANT = "主仆"         # 主人-仆人
    LORD_VASSAL = "主从"             # 主公-臣子
    
    # 友情/义气
    SWORN_BROTHER = "结拜"            # 结拜兄弟
    SWORN_SISTER = "结拜姐妹"        # 结拜姐妹
    COHORT = "同门"                  # 同门师兄弟
    BOSOM_FRIEND = "知己"            # 挚友/知己
    CHILDHOOD_FRIEND = "青梅竹马"    # 两小无猜的发小
    
    # 义亲
    ADOPTED_BROTHER = "义兄"         # 义兄
    ADOPTED_SISTER = "义妹"          # 义妹
    FOSTER_FATHER = "义父"           # 养父
    FOSTER_MOTHER = "义母"           # 养母
    
    # 恩情
    BENEFACTOR = "恩人"              # 恩人
    SAVIOR = "救命恩人"              # 救命恩人
    
    # 上下级
    SUPERIOR_INFERIOR = "上下级"     # 上下级关系
    BOSS_EMPLOYEE = "雇佣"          # 雇主-雇员
    
    # 其他
    EX = "前任"                      # 前任恋人
    BESTIE = "闺蜜"                  # 闺蜜/铁哥们
    PARTNER = "合伙人"              # 商业伙伴


class RelationshipDirection(str, Enum):
    """关系方向"""
    BIDIRECTIONAL = "bidirectional"  # 双向关系（对称）
    UNIDIRECTIONAL = "unidirectional"  # 单向关系


class RelationshipCreate(BaseModel):
    """创建关系请求"""
    from_character_id: str = Field(max_length=36, description="源角色ID")
    to_character_id: str = Field(max_length=36, description="目标角色ID")
    relation_type: RelationType = Field(description="关系类型")
    direction: RelationshipDirection = Field(
        default=RelationshipDirection.BIDIRECTIONAL,
        description="关系方向：bidirectional/unidirectional"
    )
    strength: int = Field(default=5, ge=1, le=10, description="关系强度1-10")


class RelationshipUpdate(BaseModel):
    """更新关系请求"""
    from_character_id: Optional[str] = Field(default=None, max_length=36, description="源角色ID")
    to_character_id: Optional[str] = Field(default=None, max_length=36, description="目标角色ID")
    relation_type: Optional[RelationType] = Field(default=None, description="关系类型")
    direction: Optional[RelationshipDirection] = Field(default=None, description="关系方向")
    strength: Optional[int] = Field(default=None, ge=1, le=10, description="关系强度1-10")


class RelationshipRead(BaseModel):
    """关系响应"""
    id: str
    project_id: str
    from_character_id: str
    to_character_id: str
    relation_type: str
    direction: str
    strength: int
    created_at: datetime

    model_config = {"from_attributes": True}


class RelationshipListResponse(BaseModel):
    """关系列表响应"""
    items: list[RelationshipRead]
    total: int
    page: int = 1
    page_size: int = 20


class RelationshipGraphNode(BaseModel):
    """关系图节点"""
    id: str
    name: str


class RelationshipGraphLink(BaseModel):
    """关系图链接"""
    source: str
    target: str
    type: str
    strength: int


class RelationshipGraphResponse(BaseModel):
    """关系图数据响应（用于D3.js力导向图）"""
    nodes: list[RelationshipGraphNode]
    links: list[RelationshipGraphLink]


class SuggestRelationshipRequest(BaseModel):
    """AI 建议关系请求"""
    char1_profile: dict = Field(
        description="角色1的 profile，包含 name, background, personality 等字段"
    )
    char2_profile: dict = Field(
        description="角色2的 profile，包含 name, background, personality 等字段"
    )
