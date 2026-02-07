from typing import Any, Dict, Optional
from .config import ConfigManager
from .registry import ServiceRegistry
from .loader import PluginLoader
import logging

logger = logging.getLogger(__name__)


class Agent:
    
    def __init__(self, config_path: str):
        self.config = ConfigManager(config_path)
        self.registry = ServiceRegistry()
        self.loader = PluginLoader(self.config, self.registry)
        
        self._setup_logging()
        self._load_plugins()
    
    def _setup_logging(self) -> None:
        log_level = self.config.get('logging.level', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _load_plugins(self) -> None:
        logger.info("Loading plugins...")
        self.loader.load_all_plugins()
        logger.info("All plugins loaded successfully")
    
    def execute(self, category: str, task_type: str, **kwargs) -> Any:
        plugin = self.registry.get(category, task_type)
        
        if not plugin:
            raise ValueError(f"Plugin {category}.{task_type} not found")
        
        if not plugin.health_check():
            raise RuntimeError(f"Plugin {category}.{task_type} is not healthy")
        
        if hasattr(plugin, 'process'):
            return plugin.process(**kwargs)
        else:
            raise NotImplementedError(f"Plugin {category}.{task_type} does not implement 'process' method")
    
    def get_active_plugin(self, category: str) -> Optional[Any]:
        active_name = self.config.get(f'plugins.{category}.active')
        if active_name:
            return self.registry.get(category, active_name)
        return None
    
    def list_plugins(self, category: str) -> Dict[str, Any]:
        plugins = self.registry.list_category(category)
        return {
            name: {
                'version': plugin.version,
                'healthy': plugin.health_check()
            }
            for name, plugin in plugins.items()
        }
    
    def health_check(self) -> Dict[str, bool]:
        return self.registry.health_check_all()
