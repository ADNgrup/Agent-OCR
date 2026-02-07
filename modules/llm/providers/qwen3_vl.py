from modules.llm.interface import ILLMProvider, LLMResponse
from typing import Dict, Any, Optional
import logging
import requests
import base64
import os

logger = logging.getLogger(__name__)


class Qwen3VLProvider(ILLMProvider):
    
    def __init__(self):
        self.base_url = None
        self.model = None
        self.config = {}
    
    @property
    def name(self) -> str:
        return "qwen3-vl"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.base_url = os.getenv('OLLAMA_BASE_URL', config.get('base_url'))
        self.model = os.getenv('QWEN3_VL_MODEL', config.get('model', 'qwen3-vl:8b'))
        logger.info(f"Qwen3VL provider initialized: {self.base_url}, model: {self.model}")
    
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
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            if 'temperature' in kwargs:
                payload['options'] = {'temperature': kwargs['temperature']}
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            
            return LLMResponse(
                text=result.get('response', ''),
                tokens_used=result.get('eval_count', 0),
                metadata={
                    'model': self.model,
                    'provider': 'qwen3-vl',
                    'prompt_tokens': result.get('prompt_eval_count', 0),
                    'completion_tokens': result.get('eval_count', 0)
                }
            )
        except Exception as e:
            logger.error(f"Qwen3VL generation failed: {str(e)}")
            raise
    
    def chat(self, messages: list, **kwargs) -> LLMResponse:
        prompt = "\n".join([f"{m.get('role', 'user')}: {m.get('content', '')}" for m in messages])
        return self.generate(prompt, **kwargs)
    
    def generate_with_image(self, prompt: str, image_path: str, **kwargs) -> LLMResponse:
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")
            
            image_base64 = self._encode_image(image_path)
            logger.info(f"Image encoded: {len(image_base64)} chars")
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [image_base64],
                "stream": False
            }
            
            if 'temperature' in kwargs:
                payload['options'] = {'temperature': kwargs['temperature']}
            
            logger.info(f"Calling Ollama: {self.base_url}/api/generate with {self.model}")
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            response_text = result.get('response', '')
            
            logger.info(f"Ollama response length: {len(response_text)} chars")
            
            return LLMResponse(
                text=response_text,
                tokens_used=result.get('eval_count', 0),
                metadata={
                    'model': self.model,
                    'provider': 'qwen3-vl',
                    'with_image': True,
                    'prompt_tokens': result.get('prompt_eval_count', 0),
                    'completion_tokens': result.get('eval_count', 0)
                }
            )
        except Exception as e:
            logger.error(f"Qwen3VL image generation failed: {str(e)}")
            raise
    
    def detect_visual_elements(self, image_path: str, **kwargs) -> LLMResponse:
        prompt = """Describe ALL non-text visual elements in this image. Report ONLY what you see.

## RULES:
- Describe visual elements EXACTLY as they appear
- DO NOT interpret, analyze, or infer meaning
- DO NOT add business logic or reasoning
- Report facts only: positions, colors, shapes, states

## VISUAL ELEMENTS TO DETECT:

**Interactive Controls (if present):**
- Buttons, switches, toggles
- Sliders, knobs, selectors
- Checkboxes, radio buttons
- Exact positions/states visible

**Indicators & Status (if present):**
- Status lights, LEDs (colors, on/off states)
- Progress bars, gauges, meters
- Icons, symbols, badges
- Highlight colors or boxes

**Charts & Graphics (if present):**
- Chart types (bar, line, pie, etc.)
- Axis labels, legends
- Data points visible
- Color coding

**Layout & Structure:**
- Borders, dividers, boxes
- Background colors
- Section groupings
- Visual hierarchy

**Images & Media (if present):**
- Photos, illustrations
- Logos, icons
- Diagrams, flowcharts

**Other Visual Elements:**
- Handwritten marks
- Stamps, seals
- Signatures
- Highlighting or annotations

OUTPUT:
- Use bullet points
- Be specific and factual
- Describe what you see, not what it means
- If no special visual elements exist (plain text document), state: "No special visual elements detected"
"""
        
        return self.generate_with_image(prompt, image_path, **kwargs)
    
    def integrate_results(self, image_path: str, visual_elements: str, ocr_text: str, **kwargs) -> LLMResponse:
        prompt = f"""Combine visual description and OCR text into ONE complete document.

**VISUAL ELEMENTS:**
{visual_elements}

**OCR TEXT:**
{ocr_text}

## STRICT RULES:
1. PRESERVE all information from both sources AS-IS
2. DO NOT modify, correct, or change any values
3. DO NOT add interpretation or analysis
4. DO NOT infer meaning or add logic
5. ONLY organize and format the data

## TASKS:

**1. Merge Information:**
- Include ALL visual elements described
- Include ALL text from OCR
- If visual elements are labeled, match them to corresponding OCR text
- If no visual elements, focus on formatting OCR text

**2. Format Output:**
- Use markdown headers (##, ###) for structure
- Use tables for tabular data
- Use bullet points for lists
- Preserve all numbers, units, and formatting
- Keep original language (don't translate)

**3. Organization:**
Document type determines structure:
- **Forms/Applications**: Group by sections, preserve field-value pairs
- **Invoices/Receipts**: Items, totals, dates, amounts
- **Reports**: Headers, body, data sections
- **Tables/Spreadsheets**: Preserve table structure
- **UI/Dashboards**: Group by functional areas
- **Plain documents**: Logical flow with headers

**4. Completeness:**
- ALL visual details included
- ALL OCR text included
- Nothing omitted, nothing modified
- Well-structured and readable

OUTPUT:
Complete, comprehensive document in clean markdown format. NO analysis, NO modifications."""
        
        return self.generate_with_image(prompt, image_path, **kwargs)
    
    def structure_blocks(self, image_path: str, blocks: list, **kwargs) -> LLMResponse:
        import json
        
        full_text = "\n".join([b.get('text', '') for b in blocks if b.get('text')])
        
        logger.info("Thinking mode: Pass 1 - Full extraction")
        pass1_response = self.analyze_context(image_path, full_text, **kwargs)
        
        logger.info("Thinking mode: Pass 2 - Operational analysis")
        
        pass2_prompt = f"""Provide EXPERT-LEVEL analysis of this extracted data:

{pass1_response.text}

## 1. DATA VALIDATION & QUALITY
- Completeness: missing fields, truncated data, unclear values
- Consistency: mismatched values, logical errors, formatting issues
- Anomalies: unusual patterns, out-of-range values, unexpected data
- OCR errors or ambiguities

## 2. CAUSE-EFFECT ANALYSIS
For each anomaly or unusual pattern:
- **Identify the effect** (what is abnormal)
- **Analyze control responses** (what actions system is taking)
- **Explain the cause** (why this is happening)
- Example: "Valve 100% + Heat Exchanger 51.4°C but Bath only 29°C 
           → System actively heating but insufficient heat delivery 
           → Possible causes: high heat loss, circulation issue, recent water change"

For environmental factors:
- Connect external conditions to system behavior
- Example: "-10.2°C outdoor → Rapid heat loss in open-air baths 
           → System compensating with higher temps (43.9°C vs 42°C target)"

## 3. OPERATIONAL STATE ASSESSMENT
- Evaluate if control actions match targets
- Identify stuck/failed vs correctly operating components
- Example: "0% valve with 43.9°C bath (target 42°C) = CORRECT (no heating needed), 
           NOT a malfunction"
- Assess system efficiency and performance

## 4. CONTEXTUAL INTELLIGENCE
- Domain-specific insights (safety, efficiency, operational norms)
- Time-based patterns and their implications
- Priority assessment (Critical/Important/Monitor)
- Safety threshold implications

## 5. EXPERT RECOMMENDATIONS
**Critical (Immediate Action):**
- Issues requiring urgent attention
- Safety concerns

**Important (Near-term):**
- Performance optimization
- Preventive measures

**Monitoring (Track):**
- Trends to watch
- Normal variation vs developing issues

**Root Cause Hypotheses:**
- Clearly mark as hypotheses
- Suggest verification steps

Use clear markdown: ## headers, **bold** critical items, bullet points. Be specific and actionable."""

        pass2_response = self.generate(pass2_prompt, **kwargs)
        
        total_tokens = pass1_response.tokens_used + pass2_response.tokens_used
        
        return LLMResponse(
            text=pass2_response.text,
            tokens_used=total_tokens,
            metadata={
                'model': self.model,
                'provider': 'qwen3-vl',
                'mode': 'two-pass-thinking',
                'pass1_tokens': pass1_response.tokens_used,
                'pass2_tokens': pass2_response.tokens_used,
                'pass1_extraction': pass1_response.text
            }
        )
