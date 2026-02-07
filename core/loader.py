from typing import Type, Dict, Any
from .config import ConfigManager
from .registry import ServiceRegistry
from .plugin import IPlugin
import importlib
import logging

logger = logging.getLogger(__name__)


class PluginLoader:
    
    def __init__(self, config: ConfigManager, registry: ServiceRegistry):
        self.config = config
        self.registry = registry
    
    def load_all_plugins(self) -> None:
        plugins_config = self.config.get('plugins', {})
        
        for category, category_config in plugins_config.items():
            if not isinstance(category_config, dict):
                continue
            
            engines = category_config.get('engines', category_config.get('providers', {}))
            
            for name, engine_config in engines.items():
                if not isinstance(engine_config, dict):
                    continue
                
                self._load_plugin(category, name, engine_config)
    
    def _load_plugin(self, category: str, name: str, engine_config: Dict[str, Any]) -> None:
        class_path = engine_config.get('class')
        if not class_path:
            logger.warning(f"No class path specified for {category}.{name}")
            return
        
        try:
            plugin_class = self._import_class(class_path)
            config = engine_config.get('config', {})
            self.registry.register(category, name, plugin_class, config)
        except Exception as e:
            logger.error(f"Failed to load plugin {category}.{name}: {str(e)}")
    
    def _import_class(self, class_path: str) -> Type[IPlugin]:
        module_path, class_name = class_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
