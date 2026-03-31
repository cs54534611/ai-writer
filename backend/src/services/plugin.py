"""插件系统服务"""

import json
import logging
from abc import ABC, abstractmethod
from typing import TypedDict, Optional, Any
from pathlib import Path
import importlib
import os

from src.core.config import get_settings

logger = logging.getLogger(__name__)


class PluginMetadata(TypedDict):
    """插件元数据"""
    id: str
    name: str
    version: str
    description: str
    author: str
    hooks: list[str]


class PluginResult(TypedDict):
    """插件执行结果"""
    success: bool
    data: Optional[dict]
    error: Optional[str]


class BasePlugin(ABC):
    """插件基类"""

    metadata: PluginMetadata

    @abstractmethod
    def execute(self, context: dict, **kwargs) -> PluginResult:
        """执行插件逻辑"""
        pass


class PluginManager:
    """插件管理器"""

    def __init__(self, plugin_dir: str | None = None):
        settings = get_settings()
        self.plugin_dir = plugin_dir or settings.PLUGIN_DIR
        self._plugins: dict[str, BasePlugin] = {}
        self._enabled_plugins: dict[str, bool] = {}
        self._hooks: dict[str, list[str]] = {}
        self._configs: dict[str, dict] = {}

    def discover_plugins(self) -> list[PluginMetadata]:
        """扫描并发现插件"""
        discovered = []
        plugin_base_path = Path(self.plugin_dir)

        # 支持相对路径和绝对路径
        if not plugin_base_path.is_absolute():
            # 相对于项目根目录
            project_root = Path(__file__).parent.parent.parent
            plugin_base_path = project_root / plugin_base_path

        plugin_base_path.mkdir(parents=True, exist_ok=True)

        for plugin_folder in plugin_base_path.iterdir():
            if not plugin_folder.is_dir():
                continue

            # 检查是否是插件目录（有 plugin.json 或有 Python 文件）
            plugin_json = plugin_folder / "plugin.json"
            plugin_py = plugin_folder / "plugin.py"

            if plugin_json.exists():
                # 从 plugin.json 加载元数据
                try:
                    with open(plugin_json, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                    discovered.append(PluginMetadata(**metadata))

                    # 动态加载插件类
                    self._load_plugin_from_json(plugin_folder, metadata)
                except Exception as e:
                    logger.warning(f"Failed to load plugin from {plugin_json}: {e}")

            elif plugin_py.exists():
                # 从 plugin.py 加载
                try:
                    module_name = f"plugins.{plugin_folder.name}.plugin"
                    module = importlib.import_module(module_name)

                    # 查找 BasePlugin 子类
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and
                            issubclass(attr, BasePlugin) and
                            attr != BasePlugin):
                            plugin_instance = attr()
                            self._plugins[plugin_instance.metadata["id"]] = plugin_instance
                            discovered.append(plugin_instance.metadata)

                            # 注册 hooks
                            for hook in plugin_instance.metadata.get("hooks", []):
                                if hook not in self._hooks:
                                    self._hooks[hook] = []
                                self._hooks[hook].append(plugin_instance.metadata["id"])
                except Exception as e:
                    logger.warning(f"Failed to load plugin from {plugin_py}: {e}")

        # 更新已发现插件的启用状态
        for metadata in discovered:
            plugin_id = metadata["id"]
            if plugin_id not in self._enabled_plugins:
                self._enabled_plugins[plugin_id] = plugin_id in settings.ENABLED_PLUGINS

        return discovered

    def _load_plugin_from_json(self, plugin_folder: Path, metadata: dict) -> None:
        """从 plugin.json 加载插件"""
        plugin_id = metadata.get("id")
        if not plugin_id:
            return

        # 加载配置文件
        config_path = plugin_folder / "config.json"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    self._configs[plugin_id] = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load plugin config from {config_path}: {e}")
                self._configs[plugin_id] = {}

        # 尝试加载 plugin.py
        plugin_py = plugin_folder / "plugin.py"
        if plugin_py.exists():
            try:
                module_name = f"plugins.{plugin_folder.name}.plugin"
                module = importlib.import_module(module_name)

                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and
                        issubclass(attr, BasePlugin) and
                        attr != BasePlugin):
                        plugin_instance = attr()
                        self._plugins[plugin_id] = plugin_instance

                        # 注册 hooks
                        for hook in plugin_instance.metadata.get("hooks", []):
                            if hook not in self._hooks:
                                self._hooks[hook] = []
                            self._hooks[hook].append(plugin_id)
            except Exception as e:
                logger.warning(f"Failed to load plugin class from {plugin_py}: {e}")

    def register_plugin(self, plugin: BasePlugin) -> None:
        """注册插件"""
        plugin_id = plugin.metadata["id"]
        self._plugins[plugin_id] = plugin

        # 注册 hooks
        for hook in plugin.metadata.get("hooks", []):
            if hook not in self._hooks:
                self._hooks[hook] = []
            if plugin_id not in self._hooks[hook]:
                self._hooks[hook].append(plugin_id)

    def enable_plugin(self, plugin_id: str) -> bool:
        """启用插件"""
        if plugin_id not in self._plugins:
            return False

        self._enabled_plugins[plugin_id] = True
        self._save_plugin_state(plugin_id, enabled=True)
        return True

    def disable_plugin(self, plugin_id: str) -> bool:
        """禁用插件"""
        if plugin_id not in self._plugins:
            return False

        self._enabled_plugins[plugin_id] = False
        self._save_plugin_state(plugin_id, enabled=False)
        return True

    def _save_plugin_state(self, plugin_id: str, enabled: bool) -> None:
        """保存插件启用状态"""
        plugin_base_path = Path(self.plugin_dir)
        if not plugin_base_path.is_absolute():
            project_root = Path(__file__).parent.parent.parent
            plugin_base_path = project_root / plugin_base_path

        state_file = plugin_base_path / plugin_id / ".state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump({"enabled": enabled}, f)
        except Exception as e:
            logger.warning(f"Failed to save plugin state for {plugin_id}: {e}")

    def execute_hook(self, hook_name: str, context: dict) -> list[PluginResult]:
        """执行所有挂载在某个 hook 上的插件"""
        results = []
        plugin_ids = self._hooks.get(hook_name, [])

        for plugin_id in plugin_ids:
            if not self._enabled_plugins.get(plugin_id, False):
                continue

            plugin = self._plugins.get(plugin_id)
            if not plugin:
                continue

            try:
                config = self._configs.get(plugin_id, {})
                result = plugin.execute(context, **config)
                results.append(result)
            except Exception as e:
                logger.error(f"Error executing plugin {plugin_id} on hook {hook_name}: {e}")
                results.append(PluginResult(
                    success=False,
                    data=None,
                    error=str(e)
                ))

        return results

    async def execute_plugin(self, plugin_id: str, context: dict) -> PluginResult:
        """直接执行某个插件"""
        plugin = self._plugins.get(plugin_id)
        if not plugin:
            return PluginResult(
                success=False,
                data=None,
                error=f"Plugin {plugin_id} not found"
            )

        if not self._enabled_plugins.get(plugin_id, False):
            return PluginResult(
                success=False,
                data=None,
                error=f"Plugin {plugin_id} is disabled"
            )

        try:
            config = self._configs.get(plugin_id, {})
            result = plugin.execute(context, **config)
            return result
        except Exception as e:
            logger.error(f"Error executing plugin {plugin_id}: {e}")
            return PluginResult(
                success=False,
                data=None,
                error=str(e)
            )

    def get_plugin_config(self, plugin_id: str) -> dict:
        """获取插件配置"""
        return self._configs.get(plugin_id, {})

    def save_plugin_config(self, plugin_id: str, config: dict) -> None:
        """保存插件配置"""
        self._configs[plugin_id] = config

        # 保存到文件
        plugin_base_path = Path(self.plugin_dir)
        if not plugin_base_path.is_absolute():
            project_root = Path(__file__).parent.parent.parent
            plugin_base_path = project_root / plugin_base_path

        config_path = plugin_base_path / plugin_id / "config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save plugin config for {plugin_id}: {e}")
            raise

    def is_plugin_enabled(self, plugin_id: str) -> bool:
        """检查插件是否启用"""
        return self._enabled_plugins.get(plugin_id, False)


# 全局插件管理器实例
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """获取全局插件管理器实例"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
        _plugin_manager.discover_plugins()
    return _plugin_manager
