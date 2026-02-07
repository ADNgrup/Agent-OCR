from abc import abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass, field
from core.plugin import IPlugin


@dataclass
class OCRResult:
    text: str
    boxes: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class IOCREngine(IPlugin):
    
    @abstractmethod
    def process(self, input_path: str, **kwargs) -> OCRResult:
        pass
    
    @abstractmethod
    def batch_process(self, input_paths: List[str], **kwargs) -> List[OCRResult]:
        pass
