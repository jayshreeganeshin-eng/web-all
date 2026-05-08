# 🕷️ web-all v3.0 - Universal Website Cloner with AI

**The most advanced open-source tool for cloning websites with AI-powered analysis, hidden content discovery, and auto-organized assets.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests Passing](https://img.shields.io/badge/tests-37%20passed-green.svg)](https://github.com/web-all/web-all)

---

## ✨ Key Features

### Core Capabilities
| Feature | Description |
|---------|-------------|
| 🌐 **Full Website Cloning** | Download complete websites with HTML, CSS, JS, images |
| 🔍 **Hidden Content Discovery** | Uncover content behind clicks, hovers, accordions, lazy-loading |
| 🤖 **AI-Powered Analysis** | Auto-summarize, extract structured data, tag content (Ollama/OpenRouter/Groq/NVIDIA/HuggingFace) |
| 🧅 **Tor/.onion Support** | Clone hidden services through Tor network |
| 📱 **Dynamic Rendering** | Headless browser support for JavaScript-heavy sites (React, Vue, Angular) |
| 🗂️ **Auto-Organization** | Assets organized by type: /images, /css, /js folders |
| 📦 **ZIP Export** | Package cloned sites for easy sharing |
| ⚡ **High Performance** | Async concurrency, connection pooling, caching |
| 🛡️ **Ethical Crawling** | Respects robots.txt, rate limiting, configurable delays |

### Interfaces
- **CLI** - Fast command-line interface with comprehensive options
- **Web GUI** - Beautiful, responsive browser-based dashboard with real-time progress
- **REST API** - Programmatic access with job queue management

### AI Providers Supported
| Provider | Free Tier | Speed | Best For |
|----------|-----------|-------|----------|
| **NVIDIA NIM** | ✅ Yes | ⚡⚡⚡ Fast | Production, enterprise |
| **Groq** | ✅ Yes | ⚡⚡⚡⚡ Fastest | Real-time applications |
| **OpenRouter** | ✅ Yes | ⚡⚡ Medium | Multiple model choices |
| **HuggingFace** | ✅ Yes | ⚡ Medium | Experimentation |
| **Ollama** | ✅ Free (Local) | ⚡⚡ Hardware-dependent | Offline, privacy |

---

## 🚀 Installation

### Method 1: Quick Install (Recommended)
```bash
cd /workspace
pip install -e .
python -m playwright install chromium
```

### Method 2: From PyPI
```bash
pip install web-all
python -m playwright install chromium
```

### Method 3: Docker
```bash
docker build -t web-all .
docker run -p 8000:8000 -v $(pwd)/output:/app/output web-all
```

### Verify Installation
```bash
web-all --help
```

### System Requirements
- Python 3.10 or higher
- 2GB+ RAM recommended for large crawls
- Chromium browser (auto-installed via Playwright)
- Optional: Tor Browser for .onion sites

---

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [CLI Commands](#-cli-commands)
- [Web GUI](#-web-gui)
- [REST API](#-rest-api)
- [AI Features](#-ai-features)
- [Configuration Options](#-configuration-options)
- [Output Structure](#-output-structure)
- [Docker Deployment](#-docker-deployment)
- [Troubleshooting](#-troubleshooting)
- [Documentation Files](#-documentation-files)

---

## 🎯 Quick Start

### Clone a Website (Basic)
```bash
web-all clone https://example.com -o mysite
```

### Start Web GUI
```bash
web-all serve
# Open http://localhost:8000 in your browser
```

### Full Capture with AI
```bash
web-all clone https://example.com -o mysite --everything --ai-enabled --ai-provider nvidia --ai-key "your-key"
```

---

## 💻 CLI Commands

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
- `-d 0`: Crawl all pages in the domain (unlimited depth, bounded by `--max-pages`)

#### Control page crawl size:
```bash
web-all clone https://example.com -o mysite --max-pages 500
```
This limits the number of pages crawled for large sites.

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

## 🌐 Web GUI

The web-based GUI provides a beautiful, user-friendly interface for all web-all features.

### Starting the Server
```bash
web-all serve              # Default port 8000
web-all serve -p 8080      # Custom port
web-all serve --no-gui     # API only mode
```

### Accessing the GUI
1. Start the server with `web-all serve`
2. Open your browser to `http://localhost:8000`
3. Use the intuitive interface to:
   - Enter target URLs
   - Select capture modes
   - Configure depth and concurrency
   - Enable AI analysis
   - Monitor real-time progress
   - Download results as ZIP

### GUI Features
- **🚀 Clone Website Tab**: Full website cloning with options
- **🤖 AI Settings Tab**: Configure AI providers and models
- **📊 Jobs Dashboard**: View and manage all clone jobs
- **⚙️ Settings**: Customize behavior and preferences

---

## 🔌 REST API

web-all provides a comprehensive REST API for programmatic access.

### Base URL
```
http://localhost:8000/api/v1/
```

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/clone` | POST | Create clone job |
| `/jobs/{id}` | GET | Get job status |
| `/jobs` | GET | List all jobs |
| `/download/{id}` | GET | Download ZIP |
| `/ai/config` | POST/GET | Configure AI |
| `/ai/providers` | GET | List AI providers |
| `/ai/test` | POST | Test AI connection |

### Example: Create Clone Job
```bash
curl -X POST http://localhost:8000/api/v1/clone \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "mode": "everything",
    "depth": 5,
    "discover_invisible": true,
    "ai_enabled": true
  }'
```

### Example: Check Job Status
```bash
curl http://localhost:8000/api/v1/jobs/{job_id}
```

### Example: Download Result
```bash
curl -O http://localhost:8000/api/v1/download/{job_id}
```

---

## 🤖 AI Features

When AI is enabled, web-all can:
- **Summarize** webpage content
- **Extract structured data** (products, articles, contacts)
- **Auto-tag** content with relevant keywords
- **Clean HTML** by removing navigation/ads

### Supported Providers

| Provider | Free Tier | API Key Required | Speed | Best For |
|----------|-----------|------------------|-------|----------|
| **NVIDIA NIM** | ✅ Yes | ✅ Yes | ⚡⚡⚡ Fast | Production, enterprise |
| **Groq** | ✅ Yes | ✅ Yes | ⚡⚡⚡⚡ Fastest | Real-time applications |
| **OpenRouter** | ✅ Yes | ✅ Yes | ⚡⚡ Medium | Multiple model choices |
| **HuggingFace** | ✅ Yes | ✅ Yes | ⚡ Medium | Experimentation |
| **Ollama** | ✅ Yes (local) | ❌ No | ⚡⚡ Hardware-dependent | Offline, privacy |

### Configuring AI

#### CLI Configuration
```bash
# Using NVIDIA NIM
web-all clone https://example.com --ai-enabled --ai-provider nvidia --ai-key "your-key"

# Using Groq
web-all clone https://example.com --ai-enabled --ai-provider groq --ai-key "your-key"

# Using Ollama (local, no key needed)
web-all clone https://example.com --ai-enabled --ai-provider ollama
```

#### Environment Variables
```bash
export NVIDIA_API_KEY="your-key"
export GROQ_API_KEY="your-key"
export OPENROUTER_API_KEY="your-key"

# Then use without --ai-key flag
web-all clone https://example.com --ai-enabled --ai-provider nvidia
```

#### GUI Configuration
1. Start server: `web-all serve`
2. Open http://localhost:8000
3. Go to "🤖 AI Settings" tab
4. Select provider and enter API key
5. Click "Save Configuration"

### AI Output Files

When AI analysis is enabled, the following files are generated:
- `ai_analysis.json` - Structured JSON with summary, tags, and extracted data
- `SUMMARY.md` - Human-readable markdown summary

---

## ⚙️ Configuration Options

### CLI Parameters

| Parameter | Short | Type | Default | Description |
|-----------|-------|------|---------|-------------|
| `--output` | `-o` | string | `./output` | Output directory |
| `--depth` | `-d` | int | `2` | Crawl depth (0 = unlimited) |
| `--concurrency` | `-c` | int | `5` | Parallel requests |
| `--delay` | | float | `0.5` | Delay between requests (s) |
| `--tor` | | flag | false | Use Tor proxy |
| `--dynamic` | | flag | false | Use dynamic rendering |
| `--discover-invisible` | | flag | false | Find hidden content |
| `--everything` | | flag | false | Full capture mode |
| `--ai-enabled` | | flag | false | Enable AI analysis |
| `--ai-provider` | | string | `ollama` | AI provider |
| `--ai-key` | | string | - | API key |
| `--ai-model` | | string | - | Specific model |
| `--max-pages` | | int | `1000` | Max pages to crawl |

### Common Usage Patterns

```bash
# Basic clone
web-all clone https://example.com -o mysite

# Deep crawl with concurrency
web-all clone https://example.com -o mysite -d 5 -c 10

# Dynamic site with hidden content
web-all clone https://example.com -o mysite --dynamic --discover-invisible

# Everything mode (recommended for complete capture)
web-all clone https://example.com -o mysite --everything

# With AI analysis
web-all clone https://example.com -o mysite --everything --ai-enabled --ai-provider nvidia --ai-key "key"

# Tor/.onion sites
web-all clone http://example.onion -o onion_site --tor

# Limit pages crawled
web-all clone https://example.com -o mysite --max-pages 500
```

---

## 🐳 Docker Deployment

### Build Image
```bash
docker build -t web-all .
```

### Run Container
```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/output:/app/output \
  --name web-all \
  web-all
```

### Access Services
- **GUI**: http://localhost:8000
- **API**: http://localhost:8000/api/v1/

### Docker Compose (Optional)
Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  web-all:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./output:/app/output
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

---

## 🛡️ Ethics & Legal

- ✅ Respects `robots.txt` (configurable)
- ✅ Configurable rate limiting
- ✅ User-agent identification
- ⚠️ Always respect website terms of service
- ⚠️ Use responsibly for legal purposes only

### Best Practices

1. **Check robots.txt**: Review allowed paths before crawling
2. **Rate limiting**: Use `--delay` to avoid overloading servers
3. **Concurrency**: Start low (`-c 5`) and increase if needed
4. **Depth**: Most sites work well with `-d 2` or `-d 3`
5. **Dynamic mode**: Only use when necessary (slower than static)

---

## 📦 Requirements

### System Requirements
- Python 3.10 or higher
- 2GB+ RAM recommended for large crawls
- 1GB+ free disk space
- Modern browser (for GUI access)

### Software Dependencies
- Playwright (auto-installed)
- Chromium browser (auto-installed via Playwright)
- Optional: Tor Browser (for .onion sites)
- Optional: Ollama/local AI (for offline AI features)

---

## 🔧 Troubleshooting

### Common Issues

**1. Playwright Error**
```bash
python -m playwright install chromium
python -m playwright install-deps chromium
```

**2. Command Not Found**
```bash
pip install -e .
export PATH=$PATH:~/.local/bin
```

**3. Tor Not Working**
- Ensure Tor service is running: `systemctl start tor`
- Default proxy: `http://127.0.0.1:9050`

**4. AI Not Responding**
- For Ollama: Ensure `ollama serve` is running
- Check API keys for external providers
- Test connection: `curl -X POST http://localhost:8000/api/v1/ai/test`

**5. Permission Errors**
```bash
chmod -R 755 ./output
```

**6. Memory Issues**
- Reduce concurrency: `-c 3`
- Reduce depth: `-d 1`
- Close other applications

**7. Port Already in Use**
```bash
web-all serve -p 8080
```

---

## 📚 Documentation Files

| File | Description |
|------|-------------|
| **README.md** | This file - main documentation |
| **HOW_TO_USE.md** | Detailed usage guide with examples |
| **SPECIFICATION.md** | Technical specifications and architecture |
| **SUMMARY.md** | Quick start and feature summary |
| **ENHANCEMENT_SUMMARY.md** | Performance optimizations and enhancements |
| **OPTIMIZATION_REPORT.md** | Code refactoring and test coverage report |
| **NVIDIA_INTEGRATION_GUIDE.md** | NVIDIA NIM AI integration guide |

---

## 🧪 Testing

Run the test suite:
```bash
cd /workspace
python -m pytest tests/ -v
```

All 37 tests should pass ✅

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests
5. Submit a pull request

### Development Setup
```bash
git clone https://github.com/web-all/web-all.git
cd web-all
pip install -e ".[dev]"
python -m playwright install chromium
```

---

## 📞 Support

- **Documentation**: See the documentation files listed above
- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Join discussions on GitHub

---

## 📄 License

MIT License - See LICENSE file for full terms.

---

**Made with ❤️ for the web archiving community**

**Version**: 3.0.0  
**Last Updated**: May 2024
