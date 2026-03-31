#!/usr/bin/env python3
"""
数据库初始化脚本
创建默认表结构和初始数据
"""

import os
import sys
from pathlib import Path

# 添加 backend/src 到路径
backend_src = Path(__file__).parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))


def get_database_url() -> str:
    """获取数据库 URL"""
    # 从环境变量读取
    db_path = os.getenv("DATABASE_PATH", "")
    
    if db_path:
        return f"sqlite:///{db_path}"
    
    # 默认路径: backend/data/ai_writer.db
    default_db = Path(__file__).parent.parent / "backend" / "data" / "ai_writer.db"
    return f"sqlite:///{default_db}"


def init_database():
    """初始化数据库"""
    from sqlalchemy import create_engine, text
    
    database_url = get_database_url()
    print(f"数据库 URL: {database_url}")
    
    # 创建引擎
    engine = create_engine(database_url, echo=True)
    
    # 创建所有表
    print("创建数据表...")
    
    # 文档表
    engine.execute(text("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP,
            metadata TEXT
        )
    """))
    
    # 草稿表
    engine.execute(text("""
        CREATE TABLE IF NOT EXISTS drafts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents (id)
        )
    """))
    
    # 写作模板表
    engine.execute(text("""
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            content TEXT NOT NULL,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    # 用户设置表
    engine.execute(text("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    # 插入默认模板
    print("插入默认模板...")
    
    default_templates = [
        {
            "name": "article",
            "description": "通用文章模板",
            "content": "# {{title}}\n\n## 摘要\n\n## 正文\n\n## 结论",
            "category": "article"
        },
        {
            "name": "blog",
            "description": "博客文章模板",
            "content": "# {{title}}\n\n> {{subtitle}}\n\n## 引言\n\n## 主要内容\n\n### 重点一\n\n### 重点二\n\n## 总结",
            "category": "blog"
        },
        {
            "name": "doc",
            "description": "技术文档模板",
            "content": "# {{title}}\n\n## 概述\n\n## 安装\n\n## 使用\n\n## API 参考\n\n## 示例\n\n## 常见问题",
            "category": "documentation"
        }
    ]
    
    for template in default_templates:
        engine.execute(
            text("""
                INSERT OR IGNORE INTO templates (name, description, content, category)
                VALUES (:name, :description, :content, :category)
            """),
            template
        )
    
    # 插入默认设置
    print("插入默认设置...")
    
    default_settings = [
        {"key": "llm_provider", "value": "openai"},
        {"key": "llm_model", "value": "gpt-4"},
        {"key": "theme", "value": "light"},
        {"key": "language", "value": "zh-CN"},
    ]
    
    for setting in default_settings:
        engine.execute(
            text("""
                INSERT OR IGNORE INTO settings (key, value)
                VALUES (:key, :value)
            """),
            setting
        )
    
    print("数据库初始化完成！")
    
    # 显示统计信息
    result = engine.execute(text("SELECT COUNT(*) FROM documents"))
    doc_count = result.scalar()
    result = engine.execute(text("SELECT COUNT(*) FROM templates"))
    template_count = result.scalar()
    result = engine.execute(text("SELECT COUNT(*) FROM settings"))
    setting_count = result.scalar()
    
    print(f"\n统计信息:")
    print(f"  - 文档数: {doc_count}")
    print(f"  - 模板数: {template_count}")
    print(f"  - 设置数: {setting_count}")


if __name__ == "__main__":
    init_database()
