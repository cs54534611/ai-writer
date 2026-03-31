"""敏感词 CRUD API 路由"""

from datetime import datetime
from typing import Annotated, AsyncGenerator, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Path, Body
from pydantic import BaseModel, Field
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import get_db_manager
from src.models.sensitive_word import (
    SensitiveWord,
    SensitiveLevel,
    SensitiveCategory,
    DEFAULT_SENSITIVE_WORDS,
)
from src.services.sensitive_check import get_sensitive_check_service


router = APIRouter()


async def get_project_db(
    project_id: Annotated[str, Path(description="项目ID")]
) -> AsyncGenerator[AsyncSession, None]:
    """获取项目数据库会话的依赖"""
    db_manager = get_db_manager()
    if project_id not in db_manager._engines:
        await db_manager.init_project_db(project_id)
    
    engine = db_manager._engines[project_id]
    session = AsyncSession(engine, expire_on_commit=False)
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


# Schema 定义
class SensitiveWordCreate(BaseModel):
    """创建敏感词的请求模型"""
    word: str = Field(max_length=100, description="敏感词")
    level: SensitiveLevel = Field(default=SensitiveLevel.WARNING, description="敏感级别")
    category: SensitiveCategory = Field(default=SensitiveCategory.CUSTOM, description="敏感词类别")


class SensitiveWordBatchCreate(BaseModel):
    """批量创建敏感词的请求模型"""
    words: list[SensitiveWordCreate] = Field(description="敏感词列表")
    mode: str = Field(default="skip", description="冲突模式: skip=跳过, overwrite=覆盖")


class SensitiveWordRead(BaseModel):
    """敏感词响应模型"""
    id: str
    project_id: str
    word: str
    level: str
    category: str
    created_at: datetime

    class Config:
        from_attributes = True


class SensitiveWordListResponse(BaseModel):
    """敏感词列表响应模型"""
    items: list[SensitiveWordRead]
    total: int
    page: int
    page_size: int


class SensitiveCheckRequest(BaseModel):
    """敏感词检测请求模型"""
    content: str = Field(description="待检测的文本内容")


class SensitiveMatch(BaseModel):
    """敏感词匹配结果"""
    word: str
    level: str
    category: str
    position: int
    length: int


class SensitiveCheckResponse(BaseModel):
    """敏感词检测响应模型"""
    has_sensitive: bool
    total_count: int
    by_level: dict
    by_category: dict
    matches: list[dict]
    risk_level: str


@router.get("/", response_model=SensitiveWordListResponse)
async def list_sensitive_words(
    project_id: str,
    db: Annotated[AsyncSession, Depends(get_project_db)],
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=50, ge=1, le=200, description="每页数量"),
    category: Optional[str] = Query(default=None, description="按类别过滤"),
    level: Optional[str] = Query(default=None, description="按级别过滤"),
    keyword: Optional[str] = Query(default=None, description="关键词搜索"),
) -> SensitiveWordListResponse:
    """获取敏感词列表（分页）"""
    query = select(SensitiveWord)
    
    if category:
        query = query.where(SensitiveWord.category == category)
    if level:
        query = query.where(SensitiveWord.level == level)
    if keyword:
        query = query.where(SensitiveWord.word.contains(keyword))
    
    # 获取总数
    count_query = select(SensitiveWord)
    if category:
        count_query = count_query.where(SensitiveWord.category == category)
    if level:
        count_query = count_query.where(SensitiveWord.level == level)
    if keyword:
        count_query = count_query.where(SensitiveWord.word.contains(keyword))
    
    result = await db.execute(count_query)
    total = len(result.all())
    
    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    query = query.order_by(SensitiveWord.created_at.desc())
    
    result = await db.execute(query)
    words = result.scalars().all()
    
    return SensitiveWordListResponse(
        items=list(words),
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/", response_model=SensitiveWordRead, status_code=status.HTTP_201_CREATED)
async def create_sensitive_word(
    project_id: str,
    word_data: SensitiveWordCreate,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> SensitiveWord:
    """创建敏感词"""
    # 检查是否已存在
    result = await db.execute(
        select(SensitiveWord).where(
            SensitiveWord.project_id == project_id,
            SensitiveWord.word == word_data.word,
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"敏感词 '{word_data.word}' 已存在",
        )
    
    word = SensitiveWord(
        project_id=project_id,
        word=word_data.word,
        level=word_data.level,
        category=word_data.category,
    )
    db.add(word)
    await db.flush()
    await db.refresh(word)
    
    return word


@router.post("/batch", response_model=SensitiveWordListResponse, status_code=status.HTTP_201_CREATED)
async def batch_create_sensitive_words(
    project_id: str,
    batch_data: SensitiveWordBatchCreate,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> SensitiveWordListResponse:
    """批量创建敏感词（支持批量导入）"""
    created_words: list[SensitiveWord] = []
    skip_count = 0
    
    for word_data in batch_data.words:
        # 检查是否已存在
        result = await db.execute(
            select(SensitiveWord).where(
                SensitiveWord.project_id == project_id,
                SensitiveWord.word == word_data.word,
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            if batch_data.mode == "overwrite":
                # 覆盖模式
                existing.level = word_data.level
                existing.category = word_data.category
                created_words.append(existing)
            else:
                # 跳过模式
                skip_count += 1
                continue
        else:
            word = SensitiveWord(
                project_id=project_id,
                word=word_data.word,
                level=word_data.level,
                category=word_data.category,
            )
            db.add(word)
            created_words.append(word)
    
    await db.flush()
    
    for word in created_words:
        await db.refresh(word)
    
    return SensitiveWordListResponse(
        items=created_words,
        total=len(created_words),
        page=1,
        page_size=len(created_words),
    )


@router.get("/{word_id}", response_model=SensitiveWordRead)
async def get_sensitive_word(
    project_id: str,
    word_id: str,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> SensitiveWord:
    """获取单个敏感词"""
    result = await db.execute(
        select(SensitiveWord).where(
            SensitiveWord.project_id == project_id,
            SensitiveWord.id == word_id,
        )
    )
    word = result.scalar_one_or_none()
    
    if not word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"敏感词 {word_id} 未找到",
        )
    
    return word


@router.put("/{word_id}", response_model=SensitiveWordRead)
async def update_sensitive_word(
    project_id: str,
    word_id: str,
    word_data: SensitiveWordCreate,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> SensitiveWord:
    """更新敏感词"""
    result = await db.execute(
        select(SensitiveWord).where(
            SensitiveWord.project_id == project_id,
            SensitiveWord.id == word_id,
        )
    )
    word = result.scalar_one_or_none()
    
    if not word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"敏感词 {word_id} 未找到",
        )
    
    # 检查是否与其他词冲突
    result2 = await db.execute(
        select(SensitiveWord).where(
            SensitiveWord.project_id == project_id,
            SensitiveWord.word == word_data.word,
            SensitiveWord.id != word_id,
        )
    )
    existing = result2.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"敏感词 '{word_data.word}' 已存在",
        )
    
    word.word = word_data.word
    word.level = word_data.level
    word.category = word_data.category
    
    await db.flush()
    await db.refresh(word)
    
    return word


@router.delete("/{word_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sensitive_word(
    project_id: str,
    word_id: str,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> None:
    """删除敏感词"""
    result = await db.execute(
        select(SensitiveWord).where(
            SensitiveWord.project_id == project_id,
            SensitiveWord.id == word_id,
        )
    )
    word = result.scalar_one_or_none()
    
    if not word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"敏感词 {word_id} 未找到",
        )
    
    await db.delete(word)
    await db.flush()


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_sensitive_words(
    project_id: str,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> None:
    """删除所有自定义敏感词（保留内置词库）"""
    result = await db.execute(
        select(SensitiveWord).where(SensitiveWord.project_id == project_id)
    )
    words = result.scalars().all()
    
    for word in words:
        await db.delete(word)
    
    await db.flush()


@router.post("/check", response_model=SensitiveCheckResponse)
async def check_content_sensitive(
    project_id: str,
    check_request: SensitiveCheckRequest,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> SensitiveCheckResponse:
    """检测文本内容中的敏感词"""
    # 获取项目的自定义敏感词
    result = await db.execute(
        select(SensitiveWord).where(SensitiveWord.project_id == project_id)
    )
    custom_words = result.scalars().all()
    
    # 转换为服务需要的格式
    custom_words_dict = [
        {"word": w.word, "level": w.level, "category": w.category}
        for w in custom_words
    ]
    
    # 执行检测
    service = get_sensitive_check_service(custom_words_dict)
    report = service.check_and_report(check_request.content)
    
    return SensitiveCheckResponse(**report)


@router.post("/init-defaults", response_model=SensitiveWordListResponse, status_code=status.HTTP_201_CREATED)
async def init_default_sensitive_words(
    project_id: str,
    db: Annotated[AsyncSession, Depends(get_project_db)],
) -> SensitiveWordListResponse:
    """初始化项目的默认敏感词库"""
    created_words: list[SensitiveWord] = []
    skip_count = 0
    
    for word_data in DEFAULT_SENSITIVE_WORDS:
        # 检查是否已存在
        result = await db.execute(
            select(SensitiveWord).where(
                SensitiveWord.project_id == project_id,
                SensitiveWord.word == word_data["word"],
                SensitiveWord.category == word_data["category"],
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            skip_count += 1
            continue
        
        word = SensitiveWord(
            project_id=project_id,
            word=word_data["word"],
            level=word_data["level"],
            category=word_data["category"],
        )
        db.add(word)
        created_words.append(word)
    
    await db.flush()
    
    for word in created_words:
        await db.refresh(word)
    
    return SensitiveWordListResponse(
        items=created_words,
        total=len(created_words),
        page=1,
        page_size=len(created_words),
    )
