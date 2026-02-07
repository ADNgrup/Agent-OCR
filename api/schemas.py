from pydantic import BaseModel, Field
from typing import Dict, Any, Literal


class OCRRequest(BaseModel):
    mode: Literal["fast", "thinking"] = Field(
        default="fast", 
        description="Processing mode: 'fast' for quick OCR, 'thinking' for detailed analysis"
    )


class OCRResponse(BaseModel):
    success: bool
    engine: str
    text: str
    confidence: float
    metadata: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    plugins: Dict[str, bool]
    version: str
