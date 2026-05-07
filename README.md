# 🕷️ web-all v3.0 - Universal Website Cloner with AI

**The most advanced open-source tool for cloning websites with AI-powered analysis, hidden content discovery, and auto-organized assets.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/web-all/web-all/actions/workflows/tests.yml/badge.svg)](https://github.com/web-all/web-all/actions)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## ✨ Key Features

### Core Capabilities
| Feature | Description |
|---------|-------------|
| 🌐 **Full Website Cloning** | Download complete websites with HTML, CSS, JS, images |
| 🔍 **Hidden Content Discovery** | Uncover content behind clicks, hovers, accordions, lazy-loading |
| 🤖 **AI-Powered Analysis** | Auto-summarize, extract structured data, tag content (Ollama/OpenRouter/Groq) |
| 🧅 **Tor/.onion Support** | Clone hidden services through Tor network |
| 📱 **Dynamic Rendering** | Headless browser support for JavaScript-heavy sites |
| 🗂️ **Auto-Organization** | Assets organized by type: /images, /css, /js folders |
| 📦 **ZIP Export** | Package cloned sites for easy sharing |
| ✅ **55+ Unit Tests** | Comprehensive test coverage for reliability |

### Interfaces
- **CLI** - Fast command-line interface
- **Web GUI** - Beautiful browser-based dashboard
- **REST API** - Programmatic access with job queue

---

## 🚀 Installation

### Method 1: Quick Install (Recommended)
```bash
pip install -e .
python -m playwright install chromium
```

### Method 2: From PyPI
```bash
pip install web-all
python -m playwright install chromium
```

### Verify Installation
```bash
web-all --help
```

---

## 📖 How to Use - Step by Step

### 🟢 Level 1: Easy (Beginner)

#### Clone a website with one command:
```bash
web-all clone https://example.com -o mysite
```

#### Start the Web GUI:
```bash
web-all serve
# Open http://localhost:8000 in your browser
```

#### Download all images:
```bash
web-all images https://example.com -o images
```

#### Extract text content:
```bash
web-all text https://example.com -o text
```

---

### 🟡 Level 2: Normal (Intermediate)

#### Clone with deeper crawl:
```bash
web-all clone https://example.com -o mysite -d 5 -c 10
```
- `-d 5`: Crawl 5 levels deep
- `-c 10`: Use 10 concurrent connections

#### Discover hidden content:
```bash
web-all clone https://example.com -o mysite --discover-invisible
```

#### Use dynamic rendering (for JavaScript sites):
```bash
web-all clone https://example.com -o mysite --dynamic
```

#### Run the everything capture:
```bash
web-all clone https://example.com -o mysite --everything
```
This enables dynamic rendering, hidden content discovery, a deeper site crawl, entire domain/subdomains capture, and automatically enables AI analysis when AI is configured.

#### Enable AI analysis manually from CLI:
```bash
web-all clone https://example.com -o mysite --ai-enabled
```

#### Clone through Tor (for .onion sites):
```bash
web-all clone http://example.onion -o onion_site --tor
```

#### Start API server only (no GUI):
```bash
web-all serve --no-gui --port 8080
```

---

### 🔴 Level 3: Advanced (Expert)

#### Full clone with AI analysis:
```bash
# 1. Start server with AI enabled
web-all serve

# 2. Configure AI via API or GUI
curl -X POST http://localhost:8000/api/v1/ai/config \
  -H "Content-Type: application/json" \
  -d '{"enabled":true,"provider":"ollama","model":"llama3"}'

# 3. Clone with AI
curl -X POST http://localhost:8000/api/v1/clone \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","depth":3,"ai_enabled":true}'
```

#### Use external AI providers:
```bash
# OpenRouter (free tier)
curl -X POST http://localhost:8000/api/v1/ai/config \
  -H "Content-Type: application/json" \
  -d '{"enabled":true,"provider":"openrouter","api_key":"your-key"}'

# Groq Cloud
curl -X POST http://localhost:8000/api/v1/ai/config \
  -H "Content-Type: application/json" \
  -d '{"enabled":true,"provider":"groq","api_key":"your-key","model":"llama3-8b-8192"}'
```

#### Programmatic usage in Python:
```python
from web_all import SiteCloner, InvisibleContentEngine

# Clone a site
cloner = SiteCloner(output_dir="./output", depth=3)
await cloner.clone_site("https://example.com")

# Discover hidden content
engine = InvisibleContentEngine()
expanded_html = await engine.expand_all_content("https://example.com")
```

---

## 📋 API Reference

### REST Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/clone` | POST | Create clone job |
| `/api/v1/jobs/{id}` | GET | Get job status |
| `/api/v1/jobs` | GET | List all jobs |
| `/api/v1/download/{id}` | GET | Download ZIP |
| `/api/v1/ai/config` | POST/GET | Configure AI |
| `/api/v1/ai/providers` | GET | List AI providers |

### Example: Create Clone Job
```bash
curl -X POST http://localhost:8000/api/v1/clone \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "mode": "everything",
    "depth": 5,
    "discover_invisible": true
  }'
```

### Example: Create Everything Capture Job
```bash
curl -X POST http://localhost:8000/api/v1/clone \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "everything": true,
    "depth": 5
  }'
```

---

## 🗂️ Output Structure

After cloning, your output directory will contain:
```
output/
├── example_com/
│   ├── index.html          # Main page
│   ├── about/index.html    # Nested pages
│   ├── images/             # All images
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   ├── manifest.json       # Clone metadata
│   └── README.txt          # Summary report
└── ...
```

---

## 🤖 AI Features

When AI is enabled, web-all can:
- **Summarize** webpage content
- **Extract structured data** (products, articles, contacts)
- **Auto-tag** content with relevant keywords
- **Clean HTML** by removing navigation/ads

Supported providers:
| Provider | Free Tier | API Key Required |
|----------|-----------|------------------|
| Ollama | ✅ Yes (local) | ❌ No |
| OpenRouter | ✅ Yes | ✅ Yes |
| Groq | ✅ Yes | ✅ Yes |
| HuggingFace | ✅ Yes | ✅ Yes |

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_web_all.py -v
pytest tests/test_api.py -v

# Run with coverage
pytest tests/ --cov=web_all --cov-report=html
```

### Test Coverage
- **Core Cloner**: URL normalization, link extraction, asset management
- **Utilities**: ZIP operations, size formatting
- **AI Engine**: Provider initialization, content analysis
- **API Server**: Job management, AI configuration, security tests

---

## 🛡️ Security & Vulnerabilities

### Implemented Security Measures
- ✅ **Path Traversal Prevention**: Sanitized file path handling
- ✅ **API Key Masking**: Sensitive credentials never exposed in responses
- ✅ **Input Validation**: URL and request validation
- ✅ **Job Isolation**: Unique job IDs prevent cross-access

### Known Limitations
- ⚠️ Always validate cloned content before use
- ⚠️ Rate limiting is client-side; respect server resources
- ⚠️ HTTPS verification recommended for production use

---

## 🛡️ Ethics & Legal

- ✅ Respects `robots.txt` (configurable)
- ✅ Configurable rate limiting
- ✅ User-agent identification
- ⚠️ Always respect website terms of service
- ⚠️ Use responsibly for legal purposes only

---

## 📦 Requirements

- Python 3.10+
- Playwright (auto-installed)
- Optional: Tor Browser (for .onion sites)
- Optional: Ollama/local AI (for AI features)

### Dependencies
```toml
aiohttp>=3.9.0
beautifulsoup4>=4.12.0
lxml>=5.0.0
playwright>=1.40.0
fastapi>=0.109.0
uvicorn>=0.27.0
pydantic>=2.5.0
requests>=2.31.0
```

---

## 🔧 Development

### Setting up Development Environment
```bash
# Clone repository
git clone https://github.com/web-all/web-all.git
cd web-all

# Install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (optional)
pre-commit install
```

### Code Quality
```bash
# Format code
black web_all/ tests/

# Lint code
ruff check web_all/ tests/

# Run tests
pytest tests/ -v
```

---

## 📊 Performance Optimizations

Recent improvements:
- **URL Normalization**: Sorted query parameters for better deduplication
- **Pydantic v2 Migration**: Using `model_dump()` and `model_copy()` for better performance
- **Concurrent Downloads**: Configurable concurrency for asset downloads
- **Memory Management**: Efficient streaming for large files

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 Changelog

### v3.0.0
- ✅ Added comprehensive unit tests (55+ tests)
- ✅ Migrated to Pydantic v2 (`model_dump`, `model_copy`)
- ✅ Improved URL normalization with sorted query params
- ✅ Enhanced security with path traversal prevention
- ✅ API key masking in responses
- ✅ Fixed version consistency across endpoints

### v2.0.0
- Added AI integration with multiple providers
- Web GUI dashboard
- REST API with job queue
- Everything mode for full capture

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Uses [Playwright](https://playwright.dev/) for dynamic rendering
- AI integration via [OpenRouter](https://openrouter.ai/), [Groq](https://groq.com/), [HuggingFace](https://huggingface.co/), and [Ollama](https://ollama.ai/)

---

**Made with ❤️ for the web archiving community**

[![Star this repo](https://img.shields.io/github/stars/web-all/web-all?style=social)](https://github.com/web-all/web-all/stargazers)
[![Fork this repo](https://img.shields.io/github/forks/web-all/web-all?style=social)](https://github.com/web-all/web-all/network/members)
