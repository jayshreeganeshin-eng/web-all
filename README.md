# 🕷️ web-all v3.0 - Universal Website Cloner with AI

**The most advanced open-source tool for cloning websites with AI-powered analysis, hidden content discovery, and auto-organized assets.**

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
- **CLI** - Fast command-line interface (`web-all` or `wa` shortcut)
- **Web GUI** - Beautiful browser-based dashboard
- **REST API** - Programmatic access with job queue

---

## 🚀 Installation

### Method 1: Local Installation from Source (Recommended for Development)

**Step 1: Clone the repository**
```bash
git clone https://github.com/web-all/web-all.git
cd web-all
```

**Step 2: Install in editable mode**
```bash
pip install -e .
```

**Step 3: Install Playwright browsers**
```bash
python -m playwright install chromium
# Optional: install all browsers
python -m playwright install
```

**Step 4: Verify installation**
```bash
web-all --help
# or use the shortcut
wa --help
```

---

### Method 2: Install from PyPI (Production Use)

**Step 1: Install from PyPI**
```bash
pip install web-all
```

**Step 2: Install Playwright browsers**
```bash
python -m playwright install chromium
```

**Step 3: Verify installation**
```bash
web-all --help
```

---

### Method 3: Docker Deployment

**Option A: Using docker-compose (Recommended)**
```bash
# Clone the repository
git clone https://github.com/web-all/web-all.git
cd web-all

# Start all services (web-all + optional Ollama AI)
docker-compose up -d

# Access GUI at http://localhost:8000
```

**Option B: Using Docker directly**
```bash
# Build and run
docker build -t web-all .
docker run -p 8000:8000 -v $(pwd)/output:/app/output web-all
```

---

### Method 4: Online/Cloud Deployment

#### Deploy to Hugging Face Spaces
```bash
# Create a new Space on huggingface.co/spaces
# Select Docker as the SDK
# Push your code to the space
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/web-all
git push hf main
```

#### Deploy to Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### Deploy to Render
1. Create a new Web Service on render.com
2. Connect your GitHub repository
3. Set build command: `pip install -e . && python -m playwright install chromium`
4. Set start command: `web-all serve --host 0.0.0.0 --port $PORT`

#### Deploy to Google Cloud Run
```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/web-all

# Deploy
gcloud run deploy web-all \
  --image gcr.io/PROJECT_ID/web-all \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000
```

#### Deploy to AWS ECS/Fargate
```bash
# Build and push to ECR
aws ecr get-login-password --region region | docker login --username AWS --password-stdin account.dkr.ecr.region.amazonaws.com
docker build -t web-all .
docker tag web-all:latest account.dkr.ecr.region.amazonaws.com/web-all:latest
docker push account.dkr.ecr.region.amazonaws.com/web-all:latest
```

---

### Post-Installation Setup

#### Configure AI Providers (Optional)

**For Ollama (Local AI - Free):**
```bash
# Install Ollama from https://ollama.ai
ollama pull llama3

# web-all will auto-detect Ollama on localhost:11434
```

**For OpenRouter:**
```bash
# Get API key from https://openrouter.ai
export OPENROUTER_API_KEY="your-api-key"
```

**For Groq:**
```bash
# Get API key from https://groq.com
export GROQ_API_KEY="your-api-key"
```

#### Configure Tor (Optional)
```bash
# Install Tor
# Ubuntu/Debian:
sudo apt install tor

# Start Tor service
sudo systemctl start tor

# web-all will auto-detect Tor proxy on socks5://127.0.0.1:9050
```

---

### Troubleshooting Installation

**Issue: `web-all: command not found`**
```bash
# Ensure pip bin directory is in PATH
export PATH="$HOME/.local/bin:$PATH"
# Or reinstall with:
pip install --user -e .
```

**Issue: Playwright browser installation fails**
```bash
# Install system dependencies first
# Ubuntu/Debian:
sudo apt-get install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2

# Then install browsers:
python -m playwright install chromium
```

**Issue: Port 8000 already in use**
```bash
# Use a different port
web-all serve --port 8080
```

---

## 📖 How to Use - Step by Step

### 🟢 Level 1: Easy (Beginner)

#### Clone a website with one command:
```bash
web-all clone https://example.com -o mysite
# or use shortcut
wa clone https://example.com -o mysite
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

#### Specify custom host and port:
```bash
web-all serve --host 0.0.0.0 --port 8080
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
import asyncio
from web_all import SiteCloner, InvisibleContentEngine

async def main():
    # Clone a site
    cloner = SiteCloner(output_dir="./output", depth=3)
    await cloner.clone_site("https://example.com")
    
    # Discover hidden content
    engine = InvisibleContentEngine()
    expanded_html = await engine.expand_all_content("https://example.com")
    print(expanded_html)

if __name__ == "__main__":
    asyncio.run(main())
```

#### Advanced CLI options combination:
```bash
# Full production clone with all features
web-all clone https://example.com \
  -o production_clone \
  -d 10 \
  -c 20 \
  --delay 0.5 \
  --dynamic \
  --discover-invisible \
  --ai-enabled \
  --max-pages 1000
```

#### Clone with custom user agent:
```bash
# Set via environment variable
export USER_AGENT="Mozilla/5.0 (compatible; MyBot/1.0)"
web-all clone https://example.com -o mysite
```

#### Batch cloning multiple sites:
```bash
# Create a sites.txt file with URLs
cat > sites.txt << EOF
https://example1.com
https://example2.com
https://example3.com
EOF

# Clone all sites
while read url; do
  web-all clone "$url" -o "clone_$(echo $url | sed 's|https\?://||' | sed 's|/.*||')"
done < sites.txt
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
