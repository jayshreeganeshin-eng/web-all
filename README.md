# 🕷️ web-all v3.1 - Universal Website Cloner with AI

**The most advanced open-source tool for cloning websites with AI-powered analysis, hidden content discovery, and auto-organized assets.**

## 🎉 Major Updates in v3.1

### ✨ Enhanced Local Browsing Experience
- **All links work offline** - Internal page links automatically rewritten to work locally
- **Images display properly** - All image sources (src, srcset, data-src) downloaded and linked correctly
- **CSS fully functional** - Stylesheets, @import rules, and background images all work offline
- **JavaScript preserved** - All JS files downloaded with correct relative paths
- **Fonts included** - Web fonts (woff, woff2, ttf, etc.) automatically downloaded
- **Videos supported** - Video/audio files downloaded with working references
- **Forms show helpful messages** - Disabled forms indicate they won't work offline
- **Base tag added** - Ensures all relative URLs resolve correctly in local browsing

### 📁 Improved Organization
```
output/
├── example_com/
│   ├── index.html          # Main page with local links
│   ├── about/index.html    # Nested pages with correct paths
│   ├── images/             # All images organized
│   ├── css/                # All stylesheets
│   ├── js/                 # All JavaScript files
│   ├── fonts/              # All font files (NEW!)
│   ├── videos/             # All video/audio files (NEW!)
│   ├── manifest.json       # Clone metadata
│   └── README.txt          # Summary with viewing instructions
```

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
│   ├── index.html          # Main page with local links
│   ├── about/index.html    # Nested pages with correct paths
│   ├── images/             # All images (jpg, png, gif, svg, webp, ico)
│   ├── css/                # All stylesheets with @import resolved
│   ├── js/                 # All JavaScript files
│   ├── fonts/              # All font files (woff, woff2, ttf, otf, eot)
│   ├── videos/             # All video/audio files (mp4, webm, ogg)
│   ├── manifest.json       # Clone metadata and statistics
│   └── README.txt          # Summary report with viewing instructions
```

**All HTML files have:**
- ✅ Rewritten internal links to work locally
- ✅ Image sources pointing to local copies
- ✅ CSS/JS references using relative paths
- ✅ Base tag for proper URL resolution
- ✅ Forms disabled with helpful offline messages

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

---

**Made with ❤️ for the web archiving community**
