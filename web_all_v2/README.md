# web-all v5.0.0

## The Internet's Universal Reproduction Engine – Beyond Cloning

Autonomously captures, analyzes, and rebuilds any website or online project into a clean, modern stack. Combines AI vision, passive traffic interception, and design‑token extraction to produce production‑ready codebases with zero manual cleanup.

![Version](https://img.shields.io/badge/version-5.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-green)
![License](https://img.shields.io/badge/license-MIT-blue)

---

## 🌟 Features

### Visibility Modes
- **Surface**: HTML/CSS/images only (fastest)
- **Deep**: SPA, lazy-loaded modules, WebSocket-fed data
- **Invisible**: Hidden endpoints, orphan pages, unlinked API routes
- **Shadow**: JavaScript execution, all rendered variants (dark-mode, responsive breakpoints, A/B tests)

### Core Capabilities
- **Component-Centric Cloning**: Every UI piece (buttons, cards, modals) is identified once and turned into a reusable, responsive component
- **AI Co-Pilot**: Each cloning job is accompanied by an AI assistant that suggests accessibility fixes, SEO meta improvements, performance enhancements, and code refactors in real time
- **Design Token Extraction**: Figma-compatible design tokens (colors, typography, spacing, shadows)
- **Stealth Mode**: Undetected crawling with fingerprint randomization + traffic pattern humanization
- **Session Import**: Browser profile (cookies, localStorage, IndexedDB) injection for authenticated cloning
- **Asset Harvester**: Downloads every video (HLS/DASH), font, SVG with automatic conversion to modern formats (WebP, WOFF2)
- **Anti-Ratelimit**: Distributed IP pool support with automatic backpressure

### Output Options
- Export as ZIP, HAR, WARC
- Figma design token JSON
- Storybook component export
- Direct deployment to Vercel, Netlify, Docker

---

## 🚀 Quick Start

### One-Command Installation

```bash
curl -fsSL https://web-all.sh | bash
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/web-all/web-all.git
cd web-all

# Install dependencies
pip install -e .

# Install Playwright browsers
playwright install chromium
```

### Basic Usage

```bash
# Simple surface clone
web-all clone https://example.com -o ./my-clone

# Deep clone with JavaScript execution
web-all clone https://example.com --mode deep -o ./my-clone

# All visibility modes
web-all clone https://example.com --mode all -o ./my-clone

# With component and design token extraction
web-all clone https://example.com --extract-components --extract-tokens

# Authenticated cloning (with saved cookies)
web-all clone https://example.com --cookies ./cookies.json
```

---

## 📖 Documentation

### Commands

| Command | Description |
|---------|-------------|
| `clone` | Clone a website with specified visibility mode |
| `ai analyze` | Analyze cloned site with AI |
| `ai improve` | Get AI improvement suggestions |
| `generate` | Generate modern codebase from cloned site |
| `export` | Export cloned data in various formats |
| `serve` | Start web GUI server |
| `deploy` | Deploy generated site to hosting platform |
| `config` | Manage configuration |
| `info` | Show system information |

### Visibility Modes

```bash
# Surface mode (default) - Static HTML/CSS/JS
web-all clone https://example.com --mode surface

# Deep mode - Execute JavaScript, capture dynamic content
web-all clone https://example.com --mode deep

# Invisible mode - Discover hidden URLs
web-all clone https://example.com --mode invisible

# Shadow mode - Capture all visual variants
web-all clone https://example.com --mode shadow

# All modes - Run everything
web-all clone https://example.com --mode all
```

### Configuration

Create a `.env` file:

```env
# AI Configuration
WEBALL_AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-api-key-here

# Crawler Configuration
WEBALL_DEPTH=5
WEBALL_CONCURRENCY=10
WEBALL_DELAY=1.0
WEBALL_STEALTH=true

# Backend Configuration
WEBALL_HOST=0.0.0.0
WEBALL_PORT=8000
DATABASE_URL=postgresql://user:pass@localhost:5432/weball
REDIS_URL=redis://localhost:6379
```

---

## 🏗️ Architecture

```
web-all/
├── core/                    # Core cloning engine
│   ├── cloner.py           # Main website cloner
│   ├── crawler.py          # Async Playwright crawler
│   ├── component_extractor.py  # UI component identification
│   ├── design_token_extractor.py  # Design token extraction
│   └── visibility_manager.py    # Multi-mode visibility handling
├── api/                     # REST API & Web GUI
├── cli/                     # Command-line interface
├── ai/                      # AI integration
├── utils/                   # Utility functions
├── gui/                     # Web interface
├── config/                  # Configuration management
└── plugins/                 # Plugin system
```

---

## 🔧 Tech Stack

- **Crawler**: Playwright (Chromium) + Node.js clustering
- **AI**: LangChain agents with Anthropic Claude 3.7 Sonnet + vision
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL + Redis
- **Frontend**: Next.js 16 + TypeScript + Tailwind v4 + shadcn/ui
- **Infra**: Kubernetes (EKS) or single-node Docker Compose

---

## ⚖️ Legal & Ethics

### Allowed Uses
- Cloning your own sites
- Learning and education
- Archival purposes
- Legal pentesting with written permission

### Prohibited Uses
- Theft or impersonation
- Phishing or fraud
- Violating Terms of Service

### Content Replacement
All original text, images, and logos must be replaced before publishing. The AI co-pilot will highlight them for you.

### Transparency
Generated sites include a `<meta generator='web-all'>` tag (removable in admin settings).

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

```bash
# Fork and clone
git clone https://github.com/your-username/web-all.git
cd web-all

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black web_all_v2/
ruff check web_all_v2/
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Inspired by tools like HTTrack, wget, and SiteSucker
- AI capabilities powered by Anthropic Claude
- Component detection inspired by Chromatic and Storybook
- Design token extraction inspired by Figma Variables

---

## 📬 Support

- **Documentation**: https://docs.web-all.dev
- **Issues**: https://github.com/web-all/web-all/issues
- **Discord**: https://discord.gg/web-all
- **Twitter**: @web_all_dev

---

**Made with ❤️ by the web-all Team**
