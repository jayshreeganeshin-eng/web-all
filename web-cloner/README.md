# Web Cloner Pro

Advanced website cloning and archiving tool with AI-powered auto-fix, stealth modes, comprehensive asset downloading, and full validation.

## ⚠️ Legal Notice

**Only use this tool on websites you own or have explicit written permission to archive.** Unauthorized cloning may violate copyright laws and terms of service.

## Features

### Core Crawling
- Depth-first recursive crawler
- Multiple modes: standard, stealth, discover_invisible
- Handles AJAX-loaded content, SPAs, password-protected pages
- Auto-scroll for lazy-loaded content
- Form interaction and navigation clicking
- Sitemap.xml, RSS, Atom feed parsing
- Invisible page discovery (brute-force common paths)

### Asset Downloading
- Images (including srcset, lazy-loaded)
- CSS & JavaScript (with beautifier)
- Fonts (woff, woff2, ttf, etc.)
- Videos (embedded + YouTube/Vimeo via yt-dlp)
- PDFs and documents
- JSON data files

### Stealth & Bypass
- Puppeteer-extra-plugin-stealth integration
- Rotating user-agents and fingerprints
- Human emulation (mouse movements, typing delays)
- Cookie consent auto-accept
- Proxy rotation support
- CAPTCHA solving integration (2Captcha, Anti-Captcha)

### Screenshots
- Full-page screenshots
- Multiple viewports (desktop, tablet, mobile)
- Custom device simulation

### AI Auto-Fix
- Broken link detection and repair
- Missing asset recovery
- CORS issue fixing
- Tracking script removal
- Service worker generation
- LLM integration for complex fixes

### Testing & Validation
- Link checker
- Asset integrity verification
- JavaScript error detection
- Screenshot comparison
- Auto-healing with re-validation

### API & Web UI
- RESTful API for automation
- Real-time dashboard
- Job management
- Download as ZIP

## Quick Start

### One-Command Installation

```bash
# Clone repository
git clone <your-repo-url>
cd web-cloner

# Run installer
chmod +x install.sh
./install.sh
```

### Usage

#### Web Server Mode (Recommended)

```bash
npm start
```

Then open http://localhost:3000 in your browser.

#### CLI Mode

```bash
# Basic clone
npm start -- https://example.com

# With stealth mode
npm start -- https://example.com --stealth

# With AI auto-fix
npm start -- https://example.com --ai-fix

# Multiple options
npm start -- https://example.com --stealth --ai-fix --no-validate
```

#### Using Custom Config

```bash
npm start --config=config/custom.yaml
```

## Configuration

Edit `config/default.yaml` or create `config/custom.yaml`:

```yaml
target:
  url: "https://example.com"
  depth: 10
  maxPages: 1000
  timeout: 30000

crawl:
  mode: "standard"  # standard, stealth, discover_invisible
  respectRobotsTxt: true
  concurrency: 5
  scrollPage: true
  clickElements: true

stealth:
  enabled: false
  rotateUserAgent: true
  humanEmulation: true
  cookieConsentAutoAccept: true

aiAutofix:
  enabled: false
  llmEndpoint: ""  # OpenAI or local LLM
  llmApiKey: ""
  fixBrokenLinks: true
  fixMissingAssets: true

screenshots:
  enabled: true
  fullPage: true
  viewport: ["desktop", "tablet", "mobile"]

assets:
  downloadImages: true
  downloadVideos: true
  downloadFonts: true
  beautifyCode: true
```

## Environment Variables

```bash
TARGET_URL=https://example.com
STEALTH_ENABLED=true
AI_AUTOFIX_ENABLED=true
AI_LLM_ENDPOINT=https://api.openai.com/v1/chat/completions
AI_LLM_API_KEY=your-api-key
API_PORT=3000
API_AUTH_KEY=your-secret-key
OUTPUT_DIR=./output
LOG_LEVEL=info
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/clone` | Start new clone job |
| GET | `/api/status/:jobId` | Get job status |
| GET | `/api/jobs` | List all jobs |
| GET | `/api/download/:jobId` | Download cloned site (ZIP) |
| POST | `/api/validate/:jobId` | Run validation |
| DELETE | `/api/job/:jobId` | Cancel job |
| GET | `/health` | Health check |

### Example API Usage

```bash
# Start a clone job
curl -X POST http://localhost:3000/api/clone \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "options": {"stealth": {"enabled": true}}}'

# Check status
curl http://localhost:3000/api/status/:jobId

# Download result
curl -O http://localhost:3000/api/download/:jobId
```

## Project Structure

```
web-cloner/
├── src/
│   ├── index.js           # Main entry point
│   ├── CloneManager.js    # Job management
│   ├── crawler/
│   │   └── Crawler.js     # Web crawler
│   ├── downloader/
│   │   └── AssetDownloader.js
│   ├── ai/
│   │   └── AIAutofix.js   # AI auto-fix module
│   ├── api/
│   │   └── WebServer.js   # REST API server
│   ├── utils/
│   │   ├── ConfigLoader.js
│   │   └── Validator.js   # Validation module
│   └── ui/
│       └── index.html     # Web dashboard
├── config/
│   └── default.yaml
├── output/                # Clone outputs
├── logs/                  # Log files
├── package.json
└── install.sh
```

## Advanced Features

### Invisible Page Discovery

Enable brute-force path discovery:

```yaml
sitemap:
  bruteForcePaths: true
  pathDictionary:
    - /admin
    - /dashboard
    - /private
```

### Form Authentication

Provide credentials for protected areas:

```yaml
auth:
  credentials:
    username: "user"
    password: "pass"
  cookies:
    - name: "session"
      value: "abc123"
      domain: "example.com"
```

### Proxy Rotation

```yaml
stealth:
  rotateProxy: true
  proxyList:
    - "http://proxy1:8080"
    - "http://proxy2:8080"
```

### CAPTCHA Solving

```yaml
bypass:
  solveCaptcha: true
  captchaService: "2captcha"
  captchaApiKey: "your-key"
```

## Limitations

- **Backend code cannot be cloned** - Only frontend assets are downloaded
- **Payment gateways** - Only static UI is saved; actual payment processing cannot be replicated
- **Dynamic server-side content** - Only what's rendered client-side is captured
- **Database content** - Not accessible unless exposed via API

## Troubleshooting

### Chrome/Puppeteer Issues

```bash
# Install Chrome dependencies (Linux)
sudo apt-get install -y chromium-browser

# Or let Puppeteer download Chromium
PUPPETEER_DOWNLOAD_CHROMIUM=true npm install
```

### Memory Issues

```bash
# Increase Node.js memory limit
NODE_OPTIONS="--max-old-space-size=4096" npm start
```

### Timeout Errors

Increase timeout in config:

```yaml
target:
  timeout: 60000  # 60 seconds
```

## Development

```bash
# Install dependencies
npm install

# Run in development mode
npm run dev

# Run tests
npm test
```

## License

MIT License - See LICENSE file for details.

## Disclaimer

This tool is designed for legitimate purposes only:
- Archiving your own websites
- Authorized penetration testing
- Educational purposes with permission
- Compliance and auditing

The developers are not responsible for misuse of this tool.
