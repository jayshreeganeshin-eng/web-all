# web-all - Complete Technical Specification

## 📋 Project Overview

**web-all** is a universal website cloning and crawling tool designed to download both visible and invisible content from any website. It provides multiple interfaces (CLI, REST API, Web GUI) and supports various download modes.

---

## 🎯 Core Features Implemented

### 1. Download Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `clone` | Full recursive site mirror with asset downloading and link rewriting | Complete offline browsing |
| `scroll` | Single page capture after infinite scrolling | Social media feeds, lazy-loaded galleries |
| `images-only` | Extract and download all images | Asset archival, design inspiration |
| `text-only` | Clean text extraction from pages | Content analysis, research |
| `deep-crawl` | Comprehensive discovery using sitemaps and path guessing | Finding orphan/hidden pages |

### 2. Invisible Content Discovery

The tool discovers "invisible" content through:

- **Interaction Engine**: Clicks toggles, hovers menus, expands accordions
- **Sitemap Parsing**: Reads `/sitemap.xml` for hidden URLs
- **Path Guessing**: Tests common paths (`/admin`, `/api`, etc.)
- **Lazy Load Handling**: Scrolls pages to trigger dynamic content

### 3. Multi-Interface Support

- **CLI**: Full-featured command-line interface
- **REST API**: FastAPI backend with job queue
- **Web GUI**: Modern browser-based interface with real-time progress

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   User Interfaces                    │
├──────────────┬──────────────────┬───────────────────┤
│     CLI      │    REST API      │    Web GUI        │
│  (argparse)  │   (FastAPI)      │   (HTML/JS)       │
└──────┬───────┴────────┬─────────┴─────────┬─────────┘
       │                │                   │
       └────────────────┼───────────────────┘
                        │
              ┌─────────▼─────────┐
              │   Core Engine     │
              ├───────────────────┤
              │ • cloner.py       │
              │ • invisible.py    │
              │ • scraper.py      │
              └─────────┬─────────┘
                        │
              ┌─────────▼─────────┐
              │   Dependencies    │
              ├───────────────────┤
              │ • aiohttp         │
              │ • playwright      │
              │ • beautifulsoup4  │
              │ • fastapi         │
              └───────────────────┘
```

---

## 📁 File Structure

```
web-all/
├── README.md                 # User documentation
├── SPECIFICATION.md          # This file
├── pyproject.toml            # Python package configuration
├── Dockerfile                # Container build instructions
├── install.sh                # One-command installer
└── web_all/
    ├── __init__.py           # Package initialization
    ├── cli.py                # Command-line interface
    ├── api.py                # FastAPI REST backend
    ├── cloner.py             # Core cloning engine
    ├── invisible.py          # Hidden content handler
    └── gui/
        └── index.html        # Web interface
```

---

## 🔧 Technical Implementation Details

### Cloner Engine (`cloner.py`)

**Key Components:**

1. **URL Normalization**: Deduplicates URLs by removing fragments, normalizing slashes
2. **Link Extraction**: Uses BeautifulSoup to find all `<a>`, `<link>`, `<script>` tags
3. **Link Rewriting**: Converts absolute URLs to relative paths for offline browsing
4. **Async Concurrency**: Uses `aiohttp` with semaphore-based concurrency control
5. **Politeness**: Configurable delays between requests

**Algorithm:**
```python
1. Initialize queue with starting URL
2. Worker threads fetch URLs concurrently
3. For each page:
   a. Fetch HTML
   b. Rewrite links to relative paths
   c. Save to local directory structure
   d. Extract new links and add to queue
4. Continue until queue empty or depth limit reached
```

### Invisible Handler (`invisible.py`)

**Discovery Methods:**

1. **Browser Automation** (Playwright):
   - Launches headless Chromium
   - Executes JavaScript
   - Waits for network idle
   
2. **Interaction Strategies**:
   ```python
   selectors = [
       'button[aria-expanded="false"]',
       '.accordion-toggle',
       '.load-more',
       'details > summary',
   ]
   ```
   
3. **Sitemap Parser**:
   - Fetches `/sitemap.xml`
   - Parses XML with namespace handling
   - Extracts all `<loc>` URLs
   
4. **Path Guesser**:
   - Tests 20+ common paths
   - Records successful responses

### API Backend (`api.py`)

**Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/jobs` | POST | Create new download job |
| `/api/v1/jobs/{id}` | GET | Get job status |
| `/api/v1/download/{id}` | GET | Download result ZIP |

**Job States:**
- `pending`: Queued, waiting to start
- `running`: Currently processing
- `completed`: Finished successfully
- `failed`: Error occurred

### Web GUI (`gui/index.html`)

**Features:**
- Modern gradient UI
- Real-time progress bar
- Live log output
- Mode selection dropdown
- Depth configuration
- Invisible content toggle

---

## 🚀 Installation Methods

### Method 1: Single Command (Recommended)

```bash
curl -sSL https://get.web-all.sh | bash
```

Or manually:
```bash
pip install web-all && python -m playwright install chromium
```

### Method 2: From Source

```bash
git clone https://github.com/web-all/web-all.git
cd web-all
pip install -e .
python -m playwright install chromium
```

### Method 3: Docker

```bash
docker build -t web-all .
docker run -d -p 8000:8000 -v $(pwd)/output:/app/output web-all
```

---

## 📖 Usage Examples

### CLI Commands

**Basic Clone:**
```bash
web-all clone https://example.com --output ./mirror
```

**Deep Crawl with Hidden Content:**
```bash
web-all deep-crawl https://example.com \
  --sitemap \
  --path-guess \
  --output ./deep-mirror
```

**Infinite Scroll Capture:**
```bash
web-all scroll https://twitter.com/explore \
  --output ./twitter-capture
```

**Start Web Server:**
```bash
web-all serve --port 8000
# Open http://localhost:8000
```

### API Usage

**Create Job:**
```bash
curl -X POST http://localhost:8000/api/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "mode": "clone",
    "depth": 5,
    "discover_invisible": true
  }'
```

**Poll Status:**
```bash
curl http://localhost:8000/api/v1/jobs/{job_id}
```

---

## 🌐 Hosting on InfinityFree

### Important Limitation

InfinityFree is a **static hosting provider**. It cannot run Python applications. The workflow is:

1. **Clone locally** using web-all
2. **Upload static files** to InfinityFree

### Step-by-Step Guide

#### Step 1: Clone Target Website

```bash
web-all clone https://target-site.com \
  --output ./for-infinityfree \
  --depth 5 \
  --discover-invisible
```

#### Step 2: Prepare Files

```bash
cd for-infinityfree
# Optionally create ZIP
zip -r ../upload.zip .
cd ..
```

#### Step 3: Upload via FTP

**FTP Credentials** (from InfinityFree panel):
- Host: `ftpupload.net` (or your assigned host)
- Username: `epiz_XXXXXX`
- Password: Your InfinityFree password
- Directory: `/htdocs/`

**Using FileZilla:**
1. Connect with FTP credentials
2. Navigate to `/htdocs/`
3. Upload all files from `./for-infinityfree/`

**Using Command Line:**
```bash
lftp -u epiz_XXXXXX,YOUR_PASSWORD ftpupload.net << EOF
mirror -R ./for-infinityfree /htdocs
bye
EOF
```

#### Step 4: Access Your Site

Visit: `http://your-domain.infinityfreeapp.com`

---

## ⚙️ Configuration Options

### CLI Parameters

| Parameter | Short | Type | Default | Description |
|-----------|-------|------|---------|-------------|
| `--output` | `-o` | string | `./output` | Output directory |
| `--depth` | `-d` | int | `5` | Max crawl depth |
| `--concurrency` | `-c` | int | `5` | Parallel requests |
| `--delay` | | float | `1.0` | Delay between requests (s) |
| `--discover-invisible` | | flag | `false` | Enable hidden content |
| `--headless` | | flag | `true` | Run browser headless |
| `--sitemap` | | flag | `false` | Use sitemap.xml |
| `--path-guess` | | flag | `false` | Guess common paths |

### Advanced Settings

**Custom User-Agent:**
```bash
web-all clone https://example.com \
  --user-agent "MyBot/1.0 (+https://mysite.com/bot)"
```

**URL Filtering:**
```bash
web-all clone https://example.com \
  --include ".*blog.*" \
  --exclude ".*admin.*"
```

**Authentication:**
```bash
web-all clone https://private-site.com \
  --cookies cookies.txt
```

---

## 🧪 Testing & Development

### Run Tests

```bash
pip install -e ".[dev]"
pytest tests/
```

### Code Quality

```bash
# Format
black web_all/

# Lint
ruff check web_all/

# Type check (future)
mypy web_all/
```

### Local Development

```bash
# Install in editable mode
pip install -e .

# Run CLI
web-all clone https://test.com

# Run API server
web-all serve --reload
```

---

## 📊 Performance Considerations

### Concurrency Control

- Default: 5 concurrent requests
- Adjust based on target server capacity
- Use `--concurrency 1` for fragile sites

### Rate Limiting

- Default delay: 1 second between requests
- Increase for large crawls
- Respect `robots.txt` crawl-delay

### Memory Management

- Streaming downloads for large assets
- Bounded queue size
- Automatic cleanup of temporary files

---

## 🔒 Ethical & Legal Considerations

### Best Practices

1. **Respect robots.txt**: Enabled by default
2. **Rate limiting**: Don't overload servers
3. **User-Agent identification**: Be transparent
4. **Copyright**: Only archive content you have rights to
5. **Terms of Service**: Check site ToS before crawling

### When NOT to Use

- Password-protected areas without permission
- Sites explicitly forbidding crawlers
- Commercial data scraping without license
- Personal data collection (GDPR concerns)

---

## 🛣️ Roadmap

### Version 1.0 (Current)
- ✅ Basic cloning
- ✅ Infinite scroll
- ✅ Hidden content discovery
- ✅ CLI interface
- ✅ Web GUI
- ✅ REST API

### Version 1.1 (Planned)
- [ ] Video downloading (yt-dlp integration)
- [ ] Mobile viewport emulation
- [ ] Form submission automation
- [ ] Authentication handling
- [ ] FTP auto-upload

### Version 1.2 (Planned)
- [ ] WebSocket real-time updates
- [ ] Redis job queue
- [ ] Scheduled crawls
- [ ] Multiple domain support
- [ ] Export formats (PDF, EPUB)

---

## 🤝 Contributing

### How to Contribute

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit PR

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Keep functions small

---

## 📄 License

MIT License - See LICENSE file for full terms.

---

## 📞 Support

- **Documentation**: README.md, this file
- **Issues**: GitHub Issues tab
- **Discussions**: GitHub Discussions tab
- **Email**: team@web-all.dev (future)

---

**Last Updated**: May 2024  
**Version**: 1.0.0
