from abc import abstractmethod
from core.plugin import IPlugin
from typing import List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class LLMResponse:
    text: str
    tokens_used: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ILLMProvider(IPlugin):
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        pass
