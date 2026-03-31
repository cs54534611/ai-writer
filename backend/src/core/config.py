"""应用配置管理 - 从环境变量读取配置"""

import os
from pathlib import Path
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="AIWRITER_",
        case_sensitive=False,
    )

    # 应用基础配置
    app_name: str = "AI Writer"
    app_version: str = "0.1.0"
    debug: bool = False

    # 数据库配置
    db_path_pattern: str = "{home}/.aiwriter/projects/{project_id}/project.db"
    
    # LLM 配置
    llm_provider: Literal["ollama", "openai", "deepseek", "minimax"] = "ollama"
    llm_base_url: str = "http://localhost:11434"
    llm_api_key: str = ""
    llm_model: str = "qwen3:8b"
    llm_embedding_model: str = "nomic-embed-text"

    # ChromaDB 配置
    chroma_persist_directory: str = "{home}/.aiwriter/chroma"

    # 插件系统配置
    plugin_dir: str = "plugins"
    enabled_plugins: list[str] = []

    # AI 插图生成配置
    image_gen_provider: Literal["stable_diffusion", "dall_e", "qwen_vl"] = "stable_diffusion"
    image_gen_base_url: str = "http://localhost:7860"
    image_gen_api_key: str = ""

    # API 配置
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @property
    def home_dir(self) -> Path:
        """获取用户主目录"""
        return Path(os.path.expanduser("~"))

    def get_db_path(self, project_id: str) -> Path:
        """获取指定项目的数据库路径"""
        db_path = self.db_path_pattern.format(
            home=str(self.home_dir),
            project_id=project_id
        )
        return Path(db_path)

    def get_chroma_path(self) -> Path:
        """获取 ChromaDB 持久化目录"""
        path = self.chroma_persist_directory.format(
            home=str(self.home_dir)
        )
        return Path(path)

    def ensure_directories(self, project_id: str | None = None) -> None:
        """确保必要的目录存在"""
        # 主数据目录
        self.home_dir.joinpath(".aiwriter", "projects").mkdir(parents=True, exist_ok=True)
        self.home_dir.joinpath(".aiwriter", "chroma").mkdir(parents=True, exist_ok=True)
        
        # 如果指定了项目，也创建项目目录
        if project_id:
            project_dir = self.home_dir / ".aiwriter" / "projects" / project_id
            project_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """获取缓存的设置实例"""
    return Settings()
