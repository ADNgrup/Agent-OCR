import yaml
from pathlib import Path
from typing import Any, Dict, Optional
import os
import re


class ConfigManager:
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            content = self._interpolate_env(content)
            self._config = yaml.safe_load(content)
    
    def _interpolate_env(self, content: str) -> str:
        pattern = r'\$\{([^}]+)\}'
        
        def replace(match):
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))
        
        return re.sub(pattern, replace, content)
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value if value is not None else default
    
    def get_section(self, section: str) -> Dict[str, Any]:
        return self.get(section, {})
    
    def reload(self) -> None:
        self.load()
