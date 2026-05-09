# web-all v4.5.0 - Project Structure

## Directory Layout

```
/workspace/
├── web_all/                          # Main package
│   ├── __init__.py                   # Package initialization & exports
│   ├── cli.py                        # Command-line interface
│   │
│   ├── api/                          # REST API server
│   │   ├── __init__.py               # API package exports
│   │   └── server.py                 # FastAPI server implementation
│   │
│   ├── core/                         # Core engines
│   │   ├── __init__.py               # Core package exports
│   │   ├── cloner.py                 # SiteCloner - main cloning engine
│   │   └── invisible.py              # InvisibleContentEngine - hidden content discovery
│   │
│   ├── utils/                        # Utilities
│   │   ├── __init__.py               # Utils package exports
│   │   ├── ai_engine.py              # AI integration (5 providers)
│   │   └── zip_utils.py              # ZIP archive utilities
│   │
│   ├── i18n/                         # Internationalization
│   │   └── __init__.py               # i18n system with 11 languages
│   │
│   ├── locales/                      # Translation files
│   │   ├── en.json, es.json, fr.json, ...
│   │
│   └── gui/                          # Web-based GUI
│       └── index.html                # Single-page application
│
├── tests/                            # Test suite
│   └── test_web_all.py               # Comprehensive tests (37 tests)
│
├── output/                           # Default clone output directory
│
├── pyproject.toml                    # Project configuration & dependencies
├── README.md                         # Main documentation
├── QUICK_START.md                    # Quick start guide
├── HOW_TO_USE.md                     # Detailed usage guide
└── ...                               # Additional documentation
```

## Module Exports

### web_all (root package)
- `SiteCloner` - Main website cloning engine
- `InvisibleContentEngine` - Hidden content discovery
- `AIEngine` - AI analysis engine
- `start_api` - Start the REST API server
- `cli_main` - CLI entry point
- `get_available_providers` - List AI providers
- `create_zip_archive` - Create ZIP from directory
- `extract_zip_archive` - Extract ZIP archive

### web_all.core
- `SiteCloner` - Full website cloning with asset organization
- `InvisibleContentEngine` - Click/hover/form interaction capture

### web_all.api
- `app` - FastAPI application instance
- `start_api` - Server startup function

### web_all.utils
- `AIEngine` - Multi-provider AI integration
- `get_available_providers` - ['openrouter', 'groq', 'huggingface', 'nvidia', 'ollama']
- `validate_api_key` - API key validation
- `create_zip_archive` - ZIP creation utility
- `extract_zip_archive` - ZIP extraction utility
- `format_size` - Human-readable size formatting
- `get_directory_size` - Directory size calculation

### web_all.i18n
- `t()` / `_()` - Translation function
- `set_language()` - Set current language
- `get_current_language()` - Get current language code
- `get_available_languages()` - Dict of supported languages
- `t_all()` - Get translation in all languages

## Key Features by Module

### Core Cloning (`core/cloner.py`)
- Static and dynamic page fetching
- Tor/.onion support
- Automatic asset downloading (images, CSS, JS)
- Smart link rewriting for offline browsing
- Organized folder structure (/images, /css, /js)
- Robots.txt respect option
- Performance metrics tracking
- Configurable depth, concurrency, delays

### Invisible Content (`core/invisible.py`)
- Browser automation via Playwright
- Click expandable elements (buttons, accordions)
- Hover interactions (dropdowns, menus)
- Form submission and capture
- Sitemap URL discovery
- Network request logging
- Lazy-loading content trigger

### AI Engine (`utils/ai_engine.py`)
- 5 AI providers: OpenRouter, Groq, HuggingFace, NVIDIA, Ollama
- Content summarization
- Structured data extraction
- Auto-tagging
- Content filtering/cleaning
- Parallel analysis tasks

### API Server (`api/server.py`)
- REST endpoints for all operations
- Job queue with background tasks
- Status tracking
- ZIP download endpoint
- File viewing endpoint
- AI configuration management
- Health check endpoints

### CLI (`cli.py`)
- Commands: clone, images, text, serve
- Interactive mode
- All cloning options exposed
- AI integration flags
- Tor support flags

## Production Ready Features

✅ **Error Handling**: Comprehensive try/except blocks throughout
✅ **Logging**: Structured logging with appropriate levels
✅ **Type Hints**: Full type annotations on all public APIs
✅ **Testing**: 37 passing unit/integration tests
✅ **Documentation**: Inline docstrings + external guides
✅ **Configuration**: Environment variables + config files
✅ **Performance**: Connection pooling, async operations, caching
✅ **Security**: Path traversal protection, input validation
✅ **Scalability**: Concurrent operations, configurable limits
✅ **Internationalization**: 11 languages with RTL support

## Installation & Usage

```bash
# Install
pip install -e .
python -m playwright install chromium

# CLI
web-all clone https://example.com -o mysite
web-all serve --port 8000

# Python SDK
from web_all import SiteCloner, AIEngine
cloner = SiteCloner(output_dir="./output")
await cloner.clone_site("https://example.com")

# API
from web_all.api import start_api
start_api(host="0.0.0.0", port=8000)
```

## Version: 4.5.0
