# Costco HTML Parser

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg) ![License](https://img.shields.io/badge/License-MIT-yellow.svg)

AI-powered HTML content extraction system for Costco Connection magazine articles with 90%+ accuracy.

## Features

- **7 Content Types**: Recipe, Travel, Tech, Lifestyle, Editorial, Shopping, Member
- **HTML Pattern Recognition**: Identifies content by analyzing HTML structure, tags, and text patterns
- **Dynamic Extraction**: Adapts to different HTML layouts without hardcoded selectors
- **AI Enhancement**: AWS Bedrock integration for improved content understanding and accuracy

## Quick Start

```bash
git clone https://github.com/your-org/costco-html-parser.git
cd costco-html-parser
pip install -r requirements.txt
```

### Requirements
- HTML files (place in `data/input/` directory)
- AWS credentials configured (for AI enhancement)
- Python 3.8+

### Run Processing
```bash
# Process all HTML files in data/input/
python src/main.py

# Results saved to data/results/enhanced_results.json
```

## Architecture

```
costco-html-parser/
├── src/
│   ├── processors/
│   │   └── super_enhanced_costco_processor.py  # Main processing pipeline
│   ├── utils/
│   │   ├── universal_content_extractor.py      # Core extraction engine
│   │   └── enhanced_content_detector.py        # Content classification
│   ├── models/
│   │   └── content_schemas.py                  # Data models & types
│   └── config/
│       └── settings.py                         # AWS & processing config
├── data/
│   ├── input/                                  # Source HTML files
│   └── results/                                # Processed JSON output
└── tests/                                      # Test suite
```

## Content Types & Detection

The system detects content types using pattern matching:

```python
# Example patterns in universal_content_extractor.py
"recipe": {
    "url_keywords": ["recipe"],
    "content_keywords": ["ingredients", "directions", "tablespoon"],
    "required_score": 3
}
```

## Core Architecture

### Processing Pipeline
```
HTML Input → Content Detection → Universal Extraction → AI Enhancement → Structured Output
```

### Key Components
- **`universal_content_extractor.py`** - Core extraction engine with pattern detection
- **`enhanced_content_detector.py`** - Schema-aware content classification 
- **`super_enhanced_costco_processor.py`** - Main processing pipeline with AI integration
- **`content_schemas.py`** - Type-safe data models for all content types

## Testing

```bash
python -m pytest tests/
python -m pytest --cov=src tests/
```

## Configuration

Key files:
- `src/utils/universal_content_extractor.py` - Content detection patterns
- `src/config/settings.py` - AWS and processing settings

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## License

MIT License - see LICENSE file for details.