from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from api.deps import get_agent
from api.schemas import OCRResponse
from core.agent import Agent
from typing import Optional
import tempfile
import os
from pathlib import Path

router = APIRouter(tags=["ocr"])

@router.post("/ocr", response_model=OCRResponse)
async def ocr_endpoint(
    file: UploadFile = File(...),
    mode: str = "fast",
    agent: Agent = Depends(get_agent)
):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    if mode not in ['fast', 'thinking']:
        raise HTTPException(status_code=400, detail="Mode must be 'fast' or 'thinking'")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        from modules.ocr.processor import OCRProcessor
        
        ocr_engines = {}
        for name, plugin in agent.registry.list_category('ocr').items():
            if plugin.health_check():
                ocr_engines[name] = plugin
        
        if not ocr_engines:
            raise HTTPException(status_code=503, detail="No OCR engines available")
        
        llm_provider = agent.get_active_plugin('llm')
        
        processor = OCRProcessor(ocr_engines, llm_provider)
        
        if mode == 'fast':
            result = processor.process_fast(tmp_path)
        else:
            result = processor.process_thinking(tmp_path)
        
        return OCRResponse(
            success=True,
            engine=result.metadata.get('engine', 'unknown'),
            text=result.text,
            confidence=result.confidence,
            metadata=result.metadata
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except PermissionError:
                pass
