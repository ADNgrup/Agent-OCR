# OCR Agent

A plugin-based OCR agent with visual detection and parallel processing capabilities.

## Features

- **Dual Processing Modes**
  - Fast Mode: Parallel visual detection + OCR extraction (5-10s)
  - Thinking Mode: Deep multi-pass analysis with layout detection (10-15s)

- **Multi-Engine Architecture**
  - GLM-OCR: High-accuracy text extraction
  - Qwen3-VL: Vision-language model for visual element detection
  - Marker PDF: Document layout analysis

- **Visual Element Detection**
  - Switches, buttons, and controls
  - Status indicators and gauges
  - Charts and graphics
  - Layout and structure analysis

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your Ollama base URL
```

3. Pull required models:
```bash
ollama pull glm-ocr:latest
ollama pull qwen3-vl:8b
```

## Usage

### Start API Server

```bash
python main.py --mode api
```

Server runs on `http://localhost:8080`

### API Endpoints

**POST /api/v1/ocr**

Process image with OCR:

```bash
curl -X POST http://localhost:8080/api/v1/ocr?mode=fast \
  -F "file=@image.jpg"
```

Parameters:
- `mode`: Processing mode (`fast` or `thinking`)

Response:
```json
{
  "success": true,
  "engine": "qwen3vl+glm-ocr",
  "text": "Extracted and formatted content...",
  "confidence": 0.9,
  "metadata": {
    "mode": "fast-parallel",
    "pipeline": ["qwen3-vl-visual", "glm-ocr", "qwen3-vl-integration"]
  }
}
```

## Processing Modes

### Fast Mode (Recommended)
- Parallel execution: Visual detection + OCR
- 3-step pipeline: Detect → Extract → Integrate
- Output: Complete extraction with visual elements
- Use case: General documents, forms, dashboards

### Thinking Mode
- Sequential deep analysis
- Layout-aware processing for PDFs
- Multi-pass analysis with structured insights
- Use case: Complex documents requiring detailed analysis

## Configuration

Edit `config/config.yaml`:

```yaml
plugins:
  ocr:
    engines:
      glm-ocr:
        base_url: "${OLLAMA_BASE_URL}"
        model: "glm-ocr:latest"
  
  llm:
    providers:
      qwen3-vl:
        base_url: "${OLLAMA_BASE_URL}"
        model: "qwen3-vl:8b"
```

## Project Structure

```
Agent/
├── api/                  # FastAPI server
├── config/              # Configuration files
├── modules/
│   ├── ocr/            # OCR engines
│   │   ├── engines/    # GLM-OCR, Marker
│   │   └── processor.py
│   └── llm/            # LLM providers
│       └── providers/  # Qwen3-VL
├── logs/ocr/           # Processing logs
└── main.py
```

## Supported Document Types

- Forms and applications
- Invoices and receipts
- Reports and documents
- Control panels and dashboards
- Screenshots and UIs
- Charts and graphs
- Tables and spreadsheets
- Plain text documents

## Performance

| Mode | Speed | Quality | Use Case |
|------|-------|---------|----------|
| Fast | 5-10s | 9/10 | General documents |
| Thinking | 10-15s | 8.5/10 | Complex analysis |

## Logging

All OCR runs are logged to `logs/ocr/`:
- Filename: `{mode}_{timestamp}.json`
- Contains: Input path, output, execution time, metadata

## Requirements

- Python 3.8+
- Ollama with GLM-OCR and Qwen3-VL models
- 8GB+ RAM recommended
- GPU optional (faster processing)

## License

MIT License
