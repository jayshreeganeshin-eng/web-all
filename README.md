# 🕷️ web-all v4.0 - Universal Website Cloner with AI

**The most advanced open-source tool for cloning websites with AI-powered analysis, hidden content discovery, and complete offline functionality.**

## 🎉 MAJOR UPGRADE in v4.0 - Complete Offline Browsing Experience!

### ✨ Revolutionary Enhancements

#### 🔁 UNLIMITED CRAWL DEPTH (depth=0)
- **Set depth=0 for unlimited crawling** - Crawls ALL pages including 3rd party & invisible content
- **Follow external links by default** - Complete website ecosystem capture
- **Discover hidden/invisible content** - AJAX-loaded content, lazy-loaded elements
- **Massive scale support** - Up to 10,000 pages per crawl session
- **Smart queue management** - Efficient processing of large websites

#### 🔗 Perfect Link Rewriting
- **All internal links work offline** - Automatic conversion to relative paths
- **Smart navigation** - Browse cloned sites like the real thing
- **Cross-page linking** - Navigate between all downloaded pages seamlessly
- **External link handling** - Links to crawled external sites also work

#### 🖼️ Comprehensive Image Support
- **All image formats** - jpg, png, gif, svg, webp, ico, bmp, tiff, avif
- **Lazy loading handled** - data-src, data-lazy-src, data-original attributes
- **Srcset support** - Responsive images work perfectly
- **Picture elements** - Full support for modern HTML5 picture tags
- **Inline styles** - Background images in style attributes rewritten

#### 🎨 Complete CSS Functionality  
- **All stylesheets downloaded** - With correct relative paths
- **@import resolution** - Chained CSS imports followed and downloaded
- **Background URLs** - CSS url() references rewritten to local paths
- **Font-face rules** - Custom fonts work offline
- **Colors preserved** - All styling maintained exactly as original

#### ⚙️ JavaScript Preservation
- **All JS files downloaded** - With correct relative paths
- **Module support** - .mjs and .cjs files handled
- **Inline scripts preserved** - No modification to script content
- **Event handlers intact** - All interactive features that don't require server work

#### 🔤 Font System
- **All web fonts** - woff, woff2, ttf, otf, eot formats
- **Automatic detection** - From link tags and CSS @font-face rules
- **Organized storage** - All fonts in /fonts folder
- **Correct paths** - Font references in CSS rewritten

#### 🎬 Video & Audio
- **Video files** - mp4, webm, ogg, ogv, avi, mov, wmv, flv
- **Audio files** - mp3, wav, ogg, oga, flac, aac, m4a
- **HTML5 elements** - <video> and <audio> tags fully supported
- **Source tags** - Multiple sources in picture/video elements
- **Streaming ready** - Videos play directly from local files

#### 📝 Smart Form Handling
- **Visual indicators** - Forms show "disabled in offline mode" message
- **User-friendly** - Clear explanation why forms don't work
- **Non-intrusive** - Forms visible but clearly marked as offline

#### 🏗️ Base Tag Injection
- **Proper URL resolution** - All relative paths resolve correctly
- **Browser compatibility** - Works in all modern browsers
- **No configuration needed** - Automatic on every cloned page

### 📁 Enhanced Organization Structure
```
output/
├── example_com/
│   ├── index.html              # Main page with base tag & local links
│   ├── about/index.html        # Nested pages with relative paths
│   ├── contact/index.html      # All pages navigable offline
│   ├── images/                 # All images (10+ formats supported)
│   │   ├── logo.png
│   │   ├── banner.jpg
│   │   └── icons/
│   ├── css/                    # All stylesheets with resolved imports
│   │   ├── main.css
│   │   ├── theme.css
│   │   └── vendor/
│   ├── js/                     # All JavaScript files
│   │   ├── app.js
│   │   ├── utils.mjs
│   │   └── libs/
│   ├── fonts/                  # All web fonts (NEW!)
│   │   ├── roboto.woff2
│   │   └── opensans.ttf
│   ├── videos/                 # All video files (NEW!)
│   │   └── intro.mp4
│   ├── audio/                  # All audio files (NEW!)
│   │   └── background.mp3
│   ├── manifest.json           # Detailed clone information
│   └── README.txt              # Viewing instructions
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
