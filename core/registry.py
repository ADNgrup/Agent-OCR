from typing import Dict, Type, Any, Optional, List
from .plugin import IPlugin
import logging

logger = logging.getLogger(__name__)


class ServiceRegistry:
    
    def __init__(self):
        self._services: Dict[str, IPlugin] = {}
        self._configs: Dict[str, Dict[str, Any]] = {}
    
    def register(self, category: str, name: str, plugin_class: Type[IPlugin], config: Dict[str, Any]) -> None:
        key = f"{category}.{name}"
        
        try:
            instance = plugin_class()
            instance.initialize(config)
            self._services[key] = instance
            self._configs[key] = config
            logger.info(f"Registered plugin: {key} (v{instance.version})")
        except Exception as e:
            logger.error(f"Failed to register plugin {key}: {str(e)}")
            raise
    
    def get(self, category: str, name: str) -> Optional[IPlugin]:
        key = f"{category}.{name}"
        return self._services.get(key)
    
    def list_category(self, category: str) -> Dict[str, IPlugin]:
        prefix = f"{category}."
        return {k.split('.', 1)[1]: v for k, v in self._services.items() if k.startswith(prefix)}
    
    def unregister(self, category: str, name: str) -> None:
        key = f"{category}.{name}"
        if key in self._services:
            plugin = self._services[key]
            plugin.cleanup()
            del self._services[key]
            del self._configs[key]
            logger.info(f"Unregistered plugin: {key}")
    
    def health_check_all(self) -> Dict[str, bool]:
        return {key: plugin.health_check() for key, plugin in self._services.items()}
