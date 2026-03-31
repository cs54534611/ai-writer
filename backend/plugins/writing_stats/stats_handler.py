"""写作统计数据处理器"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class StatsHandler:
    """写作统计处理器"""

    def __init__(self, stats_dir: Optional[Path] = None):
        if stats_dir is None:
            from src.core.config import get_settings
            settings = get_settings()
            stats_dir = settings.home_dir / ".aiwriter" / "stats"
        
        self.stats_dir = Path(stats_dir)
        self.stats_dir.mkdir(parents=True, exist_ok=True)
        self.stats_file = self.stats_dir / "writing_stats.json"

    def _load_stats(self) -> dict:
        """加载统计数据"""
        if self.stats_file.exists():
            with open(self.stats_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "daily": {},
            "weekly": {},
            "monthly": {},
            "total_words": 0,
            "total_chapters": 0,
            "last_updated": None,
        }

    def _save_stats(self, stats: dict) -> None:
        """保存统计数据"""
        stats["last_updated"] = datetime.now().isoformat()
        with open(self.stats_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

    def record_chapter_complete(self, project_id: str, chapter_id: str, chapter_title: str, word_count: int) -> None:
        """
        记录章节完成
        
        Args:
            project_id: 项目ID
            chapter_id: 章节ID
            chapter_title: 章节标题
            word_count: 本章字数
        """
        stats = self._load_stats()
        
        today = datetime.now().strftime("%Y-%m-%d")
        week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%W")
        month_key = datetime.now().strftime("%Y-%m")
        
        # 更新日统计
        if today not in stats["daily"]:
            stats["daily"][today] = {
                "words": 0,
                "chapters": 0,
                "projects": {},
            }
        stats["daily"][today]["words"] += word_count
        stats["daily"][today]["chapters"] += 1
        
        if project_id not in stats["daily"][today]["projects"]:
            stats["daily"][today]["projects"][project_id] = {
                "words": 0,
                "chapters": 0,
                "chapters_completed": [],
            }
        stats["daily"][today]["projects"][project_id]["words"] += word_count
        stats["daily"][today]["projects"][project_id]["chapters"] += 1
        stats["daily"][today]["projects"][project_id]["chapters_completed"].append({
            "chapter_id": chapter_id,
            "title": chapter_title,
            "words": word_count,
            "completed_at": datetime.now().isoformat(),
        })
        
        # 更新周统计
        if week_start not in stats["weekly"]:
            stats["weekly"][week_start] = {
                "words": 0,
                "chapters": 0,
                "days_active": set(),
            }
        stats["weekly"][week_start]["words"] += word_count
        stats["weekly"][week_start]["chapters"] += 1
        stats["weekly"][week_start]["days_active"].add(today)
        
        # 更新月统计
        if month_key not in stats["monthly"]:
            stats["monthly"][month_key] = {
                "words": 0,
                "chapters": 0,
                "weeks_active": set(),
            }
        stats["monthly"][month_key]["words"] += word_count
        stats["monthly"][month_key]["chapters"] += 1
        stats["monthly"][month_key]["weeks_active"].add(week_start)
        
        # 更新总计
        stats["total_words"] += word_count
        stats["total_chapters"] += 1
        
        # 将 set 转为 list 以便 JSON 序列化
        stats["weekly"][week_start]["days_active"] = list(stats["weekly"][week_start]["days_active"])
        stats["monthly"][month_key]["weeks_active"] = list(stats["monthly"][month_key]["weeks_active"])
        
        self._save_stats(stats)

    def get_daily_report(self, date: Optional[str] = None) -> dict:
        """
        获取每日报告
        
        Args:
            date: 日期字符串，默认为今天
        
        Returns:
            dict: 每日统计报告
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        stats = self._load_stats()
        daily_data = stats["daily"].get(date, {
            "words": 0,
            "chapters": 0,
            "projects": {},
        })
        
        return {
            "date": date,
            "total_words": daily_data["words"],
            "total_chapters": daily_data["chapters"],
            "projects": daily_data.get("projects", {}),
        }

    def get_weekly_report(self, week: Optional[str] = None) -> dict:
        """
        获取每周报告
        
        Args:
            week: 周字符串，格式 YYYY-WW，默认为本周
        
        Returns:
            dict: 每周统计报告
        """
        if week is None:
            week = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%W")
        
        stats = self._load_stats()
        weekly_data = stats["weekly"].get(week, {
            "words": 0,
            "chapters": 0,
            "days_active": [],
        })
        
        return {
            "week": week,
            "total_words": weekly_data["words"],
            "total_chapters": weekly_data["chapters"],
            "days_active": len(weekly_data.get("days_active", [])),
            "average_words_per_day": (
                weekly_data["words"] / len(weekly_data["days_active"])
                if weekly_data["days_active"] else 0
            ),
        }

    def get_monthly_report(self, month: Optional[str] = None) -> dict:
        """
        获取每月报告
        
        Args:
            month: 月字符串，格式 YYYY-MM，默认为本月
        
        Returns:
            dict: 每月统计报告
        """
        if month is None:
            month = datetime.now().strftime("%Y-%m")
        
        stats = self._load_stats()
        monthly_data = stats["monthly"].get(month, {
            "words": 0,
            "chapters": 0,
            "weeks_active": [],
        })
        
        return {
            "month": month,
            "total_words": monthly_data["words"],
            "total_chapters": monthly_data["chapters"],
            "weeks_active": len(monthly_data.get("weeks_active", [])),
            "average_words_per_week": (
                monthly_data["words"] / len(monthly_data["weeks_active"])
                if monthly_data["weeks_active"] else 0
            ),
        }

    def get_overall_stats(self) -> dict:
        """
        获取总体统计
        
        Returns:
            dict: 总体写作统计
        """
        stats = self._load_stats()
        
        return {
            "total_words": stats["total_words"],
            "total_chapters": stats["total_chapters"],
            "last_updated": stats.get("last_updated"),
        }

    def generate_summary_report(self) -> dict:
        """
        生成综合统计报告（JSON 格式）
        
        Returns:
            dict: 包含今日、本周、本月、总体统计的报告
        """
        return {
            "report_time": datetime.now().isoformat(),
            "today": self.get_daily_report(),
            "this_week": self.get_weekly_report(),
            "this_month": self.get_monthly_report(),
            "overall": self.get_overall_stats(),
        }

    def export_stats_json(self) -> str:
        """
        导出统计为 JSON 字符串
        
        Returns:
            str: 完整的统计数据 JSON
        """
        stats = self._load_stats()
        return json.dumps(stats, ensure_ascii=False, indent=2)


# 全局实例
_stats_handler: Optional[StatsHandler] = None


def get_stats_handler() -> StatsHandler:
    """获取统计处理器实例"""
    global _stats_handler
    if _stats_handler is None:
        _stats_handler = StatsHandler()
    return _stats_handler
