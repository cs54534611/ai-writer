"""每日自动备份插件"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.services.plugin import BasePlugin, PluginResult, PluginMetadata


class DailyBackupPlugin(BasePlugin):
    """每日自动备份插件 - 每日自动备份项目数据"""

    metadata: PluginMetadata = {
        "id": "daily_backup",
        "name": "每日备份",
        "version": "1.0.0",
        "description": "每日自动备份项目数据，防止数据丢失",
        "author": "AI Writer",
        "hooks": ["scheduled"],
    }

    def __init__(self):
        self._last_backup_date: Optional[str] = None
        self._last_backup_path: Optional[str] = None

    def execute(self, context: dict, backup_dir: str = "backups") -> PluginResult:
        """
        执行每日备份
        
        Args:
            context: 上下文，包含 project_id 等信息
            backup_dir: 备份目录
        
        Returns:
            PluginResult: 包含备份信息的执行结果
        """
        try:
            project_id = context.get("project_id")
            if not project_id:
                return PluginResult(
                    success=False,
                    data=None,
                    error="缺少 project_id",
                )

            # 获取项目目录
            from src.core.config import get_settings
            settings = get_settings()
            project_dir = settings.home_dir / ".aiwriter" / "projects" / project_id
            
            if not project_dir.exists():
                return PluginResult(
                    success=False,
                    data=None,
                    error=f"项目目录不存在: {project_dir}",
                )

            # 创建备份目录
            if not Path(backup_dir).is_absolute():
                backup_base = settings.home_dir / ".aiwriter" / backup_dir
            else:
                backup_base = Path(backup_dir)
            
            backup_base.mkdir(parents=True, exist_ok=True)

            # 生成备份文件名
            today = datetime.now().strftime("%Y%m%d")
            backup_name = f"{project_id}_{today}"
            backup_path = backup_base / backup_name

            # 如果今天的备份已存在，返回成功但不重复备份
            if self._last_backup_date == today and self._last_backup_path:
                return PluginResult(
                    success=True,
                    data={
                        "project_id": project_id,
                        "backup_date": today,
                        "backup_path": str(self._last_backup_path),
                        "skipped": True,
                        "message": "今日备份已存在",
                    },
                    error=None,
                )

            # 创建备份
            backup_path.mkdir(parents=True, exist_ok=True)

            # 备份数据库
            db_path = project_dir / "project.db"
            if db_path.exists():
                shutil.copy2(db_path, backup_path / "project.db")

            # 备份项目数据（JSON 格式）
            data_files = ["project.json", "chapters.json", "characters.json", "relationships.json"]
            for data_file in data_files:
                src = project_dir / data_file
                if src.exists():
                    shutil.copy2(src, backup_path / data_file)

            # 保存备份元数据
            backup_meta = {
                "project_id": project_id,
                "backup_date": today,
                "backup_time": datetime.now().isoformat(),
                "files": list(backup_path.iterdir()),
            }
            with open(backup_path / "backup_meta.json", "w", encoding="utf-8") as f:
                json.dump(backup_meta, f, ensure_ascii=False, indent=2)

            # 清理旧备份（保留最近 7 天）
            self._cleanup_old_backups(backup_base, project_id, keep_days=7)

            self._last_backup_date = today
            self._last_backup_path = str(backup_path)

            return PluginResult(
                success=True,
                data={
                    "project_id": project_id,
                    "backup_date": today,
                    "backup_path": str(backup_path),
                    "files_backed_up": len(list(backup_path.iterdir())),
                },
                error=None,
            )

        except Exception as e:
            return PluginResult(
                success=False,
                data=None,
                error=f"备份失败: {str(e)}",
            )

    def _cleanup_old_backups(self, backup_base: Path, project_id: str, keep_days: int = 7) -> None:
        """清理旧备份"""
        try:
            today = datetime.now()
            for backup_folder in backup_base.iterdir():
                if not backup_folder.is_dir() or not backup_folder.name.startswith(project_id):
                    continue

                # 尝试从文件夹名提取日期
                date_str = backup_folder.name.replace(f"{project_id}_", "")
                try:
                    backup_date = datetime.strptime(date_str, "%Y%m%d")
                    age_days = (today - backup_date).days
                    if age_days > keep_days:
                        shutil.rmtree(backup_folder)
                except ValueError:
                    # 日期格式不对，跳过
                    continue
        except Exception as e:
            # 清理失败不阻塞主流程
            pass
