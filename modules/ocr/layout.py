from typing import List, Dict, Any, Tuple
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class LayoutProcessor:
    
    def __init__(self, marker_engine):
        self.marker = marker_engine
    
    def extract_layout_blocks(self, image_path: str) -> List[Dict[str, Any]]:
        try:
            marker_result = self.marker.process(image_path)
            
            blocks = []
            if marker_result.boxes:
                for idx, box_info in enumerate(marker_result.boxes):
                    bbox = box_info.get('bbox')
                    if bbox:
                        blocks.append({
                            'id': idx,
                            'bbox': bbox,
                            'text': box_info.get('text', ''),
                            'confidence': box_info.get('confidence', 0.0),
                            'type': box_info.get('type', 'text')
                        })
            
            logger.info(f"Extracted {len(blocks)} layout blocks")
            return blocks
        
        except Exception as e:
            logger.error(f"Layout extraction failed: {str(e)}")
            return []
    
    def crop_image_block(self, image_path: str, bbox: List[int]) -> Image.Image:
        try:
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            x1, y1, x2, y2 = bbox
            cropped = image.crop((x1, y1, x2, y2))
            return cropped
        
        except Exception as e:
            logger.error(f"Image cropping failed: {str(e)}")
            raise
    
    def save_cropped_block(self, image_path: str, bbox: List[int]) -> str:
        import tempfile
        import os
        
        cropped = self.crop_image_block(image_path, bbox)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            cropped.save(tmp.name, 'PNG')
            return tmp.name
    
    def merge_block_results(self, blocks: List[Dict[str, Any]]) -> Tuple[str, float]:
        sorted_blocks = sorted(blocks, key=lambda b: (b['bbox'][1], b['bbox'][0]))
        
        texts = []
        confidences = []
        
        for block in sorted_blocks:
            if block.get('text'):
                texts.append(block['text'])
                confidences.append(block.get('confidence', 0.0))
        
        merged_text = '\n\n'.join(texts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return merged_text, avg_confidence
