# 🌐 weball v4.0

**AI-Powered Universal Website Cloner & Crawler - Production Ready**

[![Version](https://img.shields.io/badge/version-4.0.0-blue.svg)](https://github.com/weball/weball)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## ✨ Features

### 🎯 Complete Solution
- **Frontend** - Modern, responsive web interface
- **Backend** - Robust cloning engine with async support
- **Admin Panel** - User management, job monitoring, system settings
- **User System** - Authentication, roles, and permissions
- **AI Services** - Free AI integration for content analysis

### 🚀 Core Capabilities
- ✅ Clone any website (static & dynamic/JavaScript)
- ✅ Tor support for .onion sites
- ✅ Invisible content discovery (clicks, hovers, scrolls)
- ✅ Automatic asset downloading (images, CSS, JS)
- ✅ Organized folder structure
- ✅ AI-powered summarization, tagging, and data extraction
- ✅ RESTful API
- ✅ Real-time job status tracking

### 🤖 AI Features (Free!)
- **Auto-Detection** - Automatically detects and uses available AI
- **Ollama** - Local AI (completely free, no API key needed)
- **Groq** - Free tier with fast Llama models
- **OpenRouter** - Free tier with multiple model choices
- **HuggingFace** - Free inference API

AI automatically:
- Summarizes cloned content
- Extracts structured data
- Generates relevant tags
- Cleans irrelevant content

## 🚀 Quick Start

### Installation

```bash
# Clone or navigate to the weball directory
cd /workspace/weball

# Install dependencies
pip install -e .

# Install playwright browsers
playwright install
```

### Usage

#### Option 1: Web Interface (Recommended for Beginners)

```bash
# Start the web server
python weball_noob.py serve

# Open browser to http://localhost:8000
```

#### Option 2: Command Line

```bash
# Clone a website
python weball_noob.py clone https://example.com

# Clone with options
python weball_noob.py clone https://example.com --depth 3 --dynamic

# Clone .onion site (requires Tor)
python weball_noob.py clone http://example.onion --tor

# Show quick start guide
python weball_noob.py quickstart

# Check system status
python weball_noob.py status
```

## 📁 Project Structure

```
weball/
├── __init__.py           # Package initialization
├── weball_noob.py        # Easy-to-use interface (START HERE!)
├── pyproject.toml        # Project configuration
├── README.md             # This file
│
├── frontend/             # Web interface
│   ├── __init__.py
│   └── app.py            # Frontend HTML generator
│
├── backend/              # Business logic
│   ├── __init__.py
│   └── service.py        # Backend service
│
├── admin/                # Admin panel
│   ├── __init__.py
│   └── panel.py          # Admin dashboard
│
├── users/                # User management
│   ├── __init__.py
│   └── manager.py        # User authentication
│
├── core/                 # Core functionality
│   ├── __init__.py
│   ├── cloner.py         # Website cloning engine
│   └── invisible.py      # Invisible content discovery
│
├── utils/                # Utilities
│   ├── __init__.py
│   ├── ai_engine.py      # AI integration
│   └── zip_utils.py      # ZIP packaging
│
├── api/                  # REST API
│   ├── __init__.py
│   └── server.py         # FastAPI server
│
├── ai_services/          # AI services
│   └── __init__.py
│
├── tests/                # Tests
│   └── __init__.py
│
├── config/               # Configuration files
├── output/               # Cloned websites output
└── docs/                 # Documentation
```

## 🎮 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/clone` | POST | Create cloning job |
| `/api/v1/jobs` | GET | List all jobs |
| `/api/v1/jobs/{id}` | GET | Get job status |
| `/api/v1/download/{id}` | GET | Download result |
| `/api/v1/ai/config` | GET/POST | AI configuration |
| `/api/v1/admin/stats` | GET | Dashboard statistics |
| `/api/v1/users` | GET/POST | User management |

## 🤖 AI Configuration

By default, weball uses **Ollama** (local AI) which is completely free:

```bash
# Ollama is auto-detected if running on localhost:11434
# To install Ollama: https://ollama.ai
```

Alternative free AI providers:
- **Groq**: Get free API key at https://console.groq.com
- **OpenRouter**: Get free API key at https://openrouter.ai
- **HuggingFace**: Get free API key at https://huggingface.co

## 🔐 Default Credentials

```
Username: admin
Password: admin123
```

**⚠️ Change these immediately in production!**

## 📊 Features Comparison

| Feature | weball v4.0 |
|---------|-------------|
| Web Interface | ✅ |
| REST API | ✅ |
| Admin Panel | ✅ |
| User Management | ✅ |
| AI Integration | ✅ Free |
| Tor Support | ✅ |
| Dynamic Sites | ✅ |
| Auto-Organization | ✅ |
| Production Ready | ✅ |

## 🛠️ Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black weball/

# Lint
flake8 weball/
```

## 📝 Examples

### Python API Usage

```python
from weball import SiteCloner, AIEngine

# Clone a website
cloner = SiteCloner(output_dir="./my_clones", depth=2)
manifest = await cloner.clone_site("https://example.com")

# Use AI to analyze content
ai = AIEngine({"enabled": True, "provider": "ollama"})
summary = await ai.summarize_content(html_content, "https://example.com")
```

### Command Line

```bash
# Simple clone
weball-noob clone https://example.com

# Deep crawl with AI
weball-noob clone https://example.com --depth 5 --dynamic

# Start server
weball-noob serve --host 0.0.0.0 --port 8080
```

## 🔄 Auto-Update & Maintenance

weball is designed for production:
- Automatic dependency checks
- Self-healing configurations
- Cleanup old jobs automatically
- Storage management
- Log rotation ready

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Credits

Built with:
- FastAPI - Modern API framework
- Playwright - Browser automation
- BeautifulSoup - HTML parsing
- Ollama/Groq/OpenRouter - AI providers

---

**🎉 Ready to clone websites with AI power?**

```bash
python weball_noob.py quickstart
```
