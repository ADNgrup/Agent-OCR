from modules.ocr.interface import IOCREngine, OCRResult
from typing import Dict, Any, List
import logging
import requests
import base64
import os

logger = logging.getLogger(__name__)


class GLMOCREngine(IOCREngine):
    
    def __init__(self):
        self.base_url = None
        self.model = None
        self.config = {}
    
    @property
    def name(self) -> str:
        return "glm-ocr"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.base_url = os.getenv('OLLAMA_BASE_URL', config.get('base_url'))
        self.model = os.getenv('GLM_OCR_MODEL', config.get('model'))
        logger.info(f"GLM-OCR engine initialized: {self.base_url}")
    
    def cleanup(self) -> None:
        pass
    
    def health_check(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _encode_image(self, image_path: str) -> str:
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def process(self, input_path: str, task: str = "text", **kwargs) -> OCRResult:
        try:
            image_base64 = self._encode_image(input_path)
            
            prompt_map = {
                "text": "Text Recognition:",
                "formula": "Formula Recognition:",
                "table": "Table Recognition:"
            }
            prompt = prompt_map.get(task, "Text Recognition:")
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [image_base64],
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            text = result.get('response', '')
            
            return OCRResult(
                text=text,
                boxes=[],
                confidence=0.9,
                metadata={
                    'engine': 'glm-ocr',
                    'task': task,
                    'model': self.model
                }
            )
        except Exception as e:
            logger.error(f"GLM-OCR processing failed: {str(e)}")
            raise
    
    def process_with_schema(self, input_path: str, schema: Dict[str, Any]) -> OCRResult:
        try:
            image_base64 = self._encode_image(input_path)
            
            import json
            prompt = f"Please output the information in the image according to the following JSON format:\n{json.dumps(schema, ensure_ascii=False, indent=2)}"
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [image_base64],
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            text = result.get('response', '')
            
            try:
                structured_data = json.loads(text)
            except:
                structured_data = None
            
            return OCRResult(
                text=text,
                boxes=[],
                confidence=0.9,
                metadata={
                    'engine': 'glm-ocr',
                    'task': 'structured_extraction',
                    'model': self.model,
                    'structured_data': structured_data
                }
            )
        except Exception as e:
            logger.error(f"GLM-OCR structured extraction failed: {str(e)}")
            raise
    
    def batch_process(self, input_paths: List[str], **kwargs) -> List[OCRResult]:
        results = []
        for path in input_paths:
            try:
                result = self.process(path, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {path}: {str(e)}")
                results.append(OCRResult(
                    text="",
                    confidence=0.0,
                    metadata={'error': str(e)}
                ))
        return results
