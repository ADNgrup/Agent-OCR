from abc import ABC, abstractmethod
from typing import Dict, Any


class IPlugin(ABC):
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        pass
