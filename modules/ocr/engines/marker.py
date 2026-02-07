from modules.ocr.interface import IOCREngine, OCRResult
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class MarkerEngine(IOCREngine):
    
    def __init__(self):
        self._marker = None
        self.config = {}
    
    @property
    def name(self) -> str:
        return "marker"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self, config: Dict[str, Any]) -> None:
        try:
            from marker.converters.pdf import PdfConverter
            from marker.models import create_model_dict
            from marker.config.parser import ConfigParser
            
            self.config = config
            self.use_llm = config.get('use_llm', False)
            self.force_ocr = config.get('force_ocr', False)
            self.batch_size = config.get('batch_size', 1)
            
            marker_config = {
                "output_format": "json"
            }
            
            config_parser = ConfigParser(marker_config)
            
            self.converter = PdfConverter(
                config=config_parser.generate_config_dict(),
                artifact_dict=create_model_dict(),
                processor_list=config_parser.get_processors(),
                renderer=config_parser.get_renderer()
            )
            
            logger.info("Marker engine initialized successfully")
        except ImportError as e:
            logger.error(f"Failed to import Marker: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Marker: {str(e)}")
            raise
    
    def cleanup(self) -> None:
        if hasattr(self, 'converter'):
            del self.converter
    
    def health_check(self) -> bool:
        return hasattr(self, 'converter') and self.converter is not None
    
    def _extract_blocks_from_json(self, pages: List[Dict]) -> List[Dict[str, Any]]:
        blocks = []
        block_id = 0
        
        for page_idx, page in enumerate(pages):
            if 'children' in page and page['children']:
                for child in page['children']:
                    block_type = child.get('block_type', 'text')
                    polygon = child.get('polygon', [])
                    html = child.get('html', '')
                    
                    if polygon and len(polygon) >= 4:
                        x_coords = [p[0] for p in polygon]
                        y_coords = [p[1] for p in polygon]
                        bbox = [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]
                        
                        import re
                        text = re.sub(r'<[^>]+>', '', html)
                        
                        if text.strip():
                            blocks.append({
                                'bbox': bbox,
                                'text': text,
                                'type': block_type,
                                'confidence': 0.95,
                                'page': page_idx,
                                'polygon': polygon
                            })
                            block_id += 1
        
        return blocks
    
    def process(self, input_path: str, **kwargs) -> OCRResult:
        try:
            rendered = self.converter(input_path)
            
            blocks = []
            markdown_text = ""
            
            if isinstance(rendered, list):
                blocks = self._extract_blocks_from_json(rendered)
                
                from marker.output import json_to_markdown
                markdown_text = json_to_markdown(rendered)
            elif hasattr(rendered, 'markdown'):
                markdown_text = rendered.markdown
            
            return OCRResult(
                text=markdown_text,
                boxes=blocks,
                confidence=1.0,
                metadata={
                    'engine': 'marker',
                    'format': 'json',
                    'pages': len(rendered) if isinstance(rendered, list) else 0,
                    'blocks_count': len(blocks)
                }
            )
        except Exception as e:
            logger.error(f"Marker processing failed: {str(e)}")
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
