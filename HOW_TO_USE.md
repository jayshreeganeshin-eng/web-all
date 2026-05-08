# 🚀 web-all v3.0 - Complete Installation & Usage Guide

## 📋 Table of Contents
1. [Installation Methods](#-installation-methods)
   - [Local Installation from Source](#1-local-installation-from-source-recommended-for-development)
   - [PyPI Installation](#2-pypi-installation-production-ready)
   - [Docker Installation](#3-docker-installation-containerized-deployment)
   - [Online/Cloud Installation](#4-onlinecloud-installation)
2. [How to Use](#-how-to-use)
   - [Beginner Level](#-level-1-easy---beginner)
   - [Intermediate Level](#-level-2-normal---intermediate)
   - [Advanced Level](#-level-3-hard---expert)
3. [API Reference](#api-reference)
4. [Troubleshooting](#troubleshooting)

---

## 📦 Installation Methods

### 1. Local Installation from Source (Recommended for Development)

#### Step 1: Clone the Repository
```bash
git clone https://github.com/web-all/web-all.git
cd web-all
```

#### Step 2: Install Dependencies
```bash
# Install the package in editable mode
pip install -e .

# Install Playwright browser (required for dynamic sites)
python -m playwright install chromium

# Optional: Install system dependencies for Playwright (Linux)
python -m playwright install-deps chromium
```

#### Step 3: Verify Installation
```bash
# Check if commands work
web-all --help
wa --help  # Shortcut command
```

**✅ Success:** You should see the help menu with available commands.

---

### 2. PyPI Installation (Production Ready)

#### Step 1: Install from PyPI
```bash
pip install web-all
```

#### Step 2: Install Playwright Browser
```bash
python -m playwright install chromium
python -m playwright install-deps chromium  # Linux only
```

#### Step 3: Verify Installation
```bash
web-all --help
wa --help
```

**Note:** The `wa` shortcut is automatically available after installation.

---

### 3. Docker Installation (Containerized Deployment)

#### Option A: Using Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/web-all/web-all.git
cd web-all

# Start all services (web-all + optional Ollama AI)
docker-compose up -d

# Access GUI at http://localhost:8000
```

#### Option B: Direct Docker Command

```bash
# Build image
docker build -t web-all .

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/output:/app/output \
  --name web-all \
  web-all

# Access GUI at http://localhost:8000
```

#### Option C: With Tor Proxy Support

```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/output:/app/output \
  --network tor-network \
  --name web-all-tor \
  web-all
```

**Verify Docker Installation:**
```bash
docker ps  # Should show web-all container running
curl http://localhost:8000  # Should return health check
```

---

### 4. Online/Cloud Installation

#### A. Hugging Face Spaces

Create `requirements.txt`:
```txt
web-all
playwright
```

Create `run.sh`:
```bash
#!/bin/bash
pip install -r requirements.txt
python -m playwright install chromium
web-all serve --host 0.0.0.0 --port 7860
```

**Deploy:** Push to Hugging Face Spaces with Docker runtime.

#### B. Railway.app

1. Connect GitHub repository
2. Add start command: `web-all serve --host 0.0.0.0 --port $PORT`
3. Set environment variables:
   - `PLAYWRIGHT_BROWSERS_PATH=0`
   - `HOME=/tmp`

#### C. Render.com

Create `render.yaml`:
```yaml
services:
  - type: web
    name: web-all
    env: docker
    plan: starter
    envVars:
      - key: PORT
        value: 8000
```

#### D. Google Cloud Run

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

#### E. AWS ECS/Fargate

```bash
# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
docker tag web-all:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/web-all:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/web-all:latest

# Deploy via AWS Console or CLI
```

---

## 🔧 Post-Installation Setup

### Configure AI Providers (Optional)

#### Local AI with Ollama (Free)
```bash
# Install Ollama from https://ollama.ai
ollama pull llama3

# Configure in .env file or via API
export OLLAMA_BASE_URL="http://localhost:11434"
```

#### Cloud AI Providers
```bash
# OpenRouter (Free tier available)
export OPENROUTER_API_KEY="your-key-here"

# Groq Cloud (Free tier)
export GROQ_API_KEY="your-key-here"

# OpenAI
export OPENAI_API_KEY="your-key-here"
```

### Tor Proxy Setup (For .onion Sites)

```bash
# Install Tor
sudo apt-get install tor  # Linux
brew install tor  # macOS

# Start Tor service
sudo systemctl start tor  # Linux
brew services start tor  # macOS

# Verify Tor is running
curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org
```

---

## 🚀 How to Use

### 🟢 Level 1: Easy - Beginner

#### Quick Website Clone
```bash
# Clone any website with one command
web-all clone https://example.com -o my_website

# Or use the shortcut
wa clone https://example.com -o my_website
```

**What this does:**
- Downloads all HTML pages
- Saves all images, CSS, and JavaScript files
- Organizes files in folders: `/images`, `/css`, `/js`
- Creates a `manifest.json` with clone information

#### View Your Cloned Site
```bash
# Navigate to output folder
cd my_website/example_com

# Open in browser
open index.html  # macOS
xdg-open index.html  # Linux
start index.html  # Windows
```

#### Download Only Images
```bash
web-all images https://example.com -o my_images
wa images https://example.com -o my_images
```

#### Extract Text Content
```bash
web-all text https://example.com -o my_text
wa text https://example.com -o my_text
```

#### Start Web GUI
```bash
# Start the web server with beautiful GUI
web-all serve
wa serve

# Open browser to: http://localhost:8000
```

---

### 🟡 Level 2: Normal - Intermediate

#### Clone with Custom Depth
```bash
# Crawl deeper (default is 2 levels)
web-all clone https://example.com -o deep_clone -d 5

# -d 5: Crawl 5 levels deep
# Higher numbers = more pages but slower
```

#### Increase Speed with Concurrency
```bash
# Download multiple pages simultaneously
web-all clone https://example.com -o fast_clone -c 10 --delay 0.2

# -c 10: Use 10 concurrent connections
# --delay 0.2: Wait 0.2 seconds between requests
```

#### Clone JavaScript-Heavy Sites
```bash
# For React, Vue, Angular, etc.
web-all clone https://example.com -o dynamic_site --dynamic
wa clone https://example.com -o dynamic_site --dynamic
```

#### Discover Hidden Content
```bash
# Find content behind buttons, accordions, lazy-loading
web-all clone https://example.com -o hidden_content --discover-invisible
```

#### Full Capture Mode (Everything)
```bash
# Enable all advanced features at once
web-all clone https://example.com -o complete --everything
```

#### Clone .onion Sites (Tor)
```bash
# Ensure Tor is running, then:
web-all clone http://example.onion -o onion_site --tor
```

#### Combined Options Example
```bash
# Full-featured clone
web-all clone https://example.com \
  -o complete_clone \
  -d 4 \
  -c 8 \
  --delay 0.3 \
  --dynamic \
  --discover-invisible
```

#### Custom Server Host and Port
```bash
# Serve on custom host/port
web-all serve --host 0.0.0.0 --port 8080
wa serve --host 127.0.0.1 --port 3000
```

---

### 🔴 Level 3: Hard - Expert

#### Programmatic Usage in Python

**Basic Cloning Script:**
```python
import asyncio
from web_all import SiteCloner

async def clone_website():
    cloner = SiteCloner(
        output_dir="./my_output",
        depth=3,
        concurrency=10,
        delay=0.5,
        use_tor=False
    )
    
    manifest = await cloner.clone_site("https://example.com", mode="static")
    print(f"Cloned {manifest['visited_count']} pages")

if __name__ == "__main__":
    asyncio.run(clone_website())
```

**Dynamic Cloning with Invisible Content:**
```python
import asyncio
from web_all import SiteCloner, InvisibleContentEngine

async def advanced_clone():
    url = "https://example.com"
    
    # Step 1: Discover hidden content
    engine = InvisibleContentEngine()
    expanded_html = await engine.expand_all_content(url)
    
    # Save expanded content
    with open("expanded.html", "w") as f:
        f.write(expanded_html)
    
    # Step 2: Clone the full site
    cloner = SiteCloner(output_dir="./output", depth=2)
    await cloner.clone_site(url, mode="dynamic")

if __name__ == "__main__":
    asyncio.run(advanced_clone())
```

#### AI-Powered Cloning

**Setup AI Configuration:**
```bash
# Start server first
web-all serve &

# Configure Ollama (local, free)
curl -X POST http://localhost:8000/api/v1/ai/config \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "provider": "ollama",
    "model": "llama3",
    "base_url": "http://localhost:11434"
  }'

# Configure OpenRouter (free tier)
curl -X POST http://localhost:8000/api/v1/ai/config \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "provider": "openrouter",
    "api_key": "your-api-key",
    "model": "mistralai/mistral-7b-instruct:free"
  }'
```

**Clone with AI Analysis:**
```bash
curl -X POST http://localhost:8000/api/v1/clone \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "depth": 3,
    "ai_enabled": true,
    "discover_invisible": true
  }'
```

**AI automatically:**
- Summarizes page content
- Extracts structured data (products, articles, contacts)
- Generates relevant tags
- Cleans HTML by removing ads/navigation

#### REST API Usage

**Create Clone Job:**
```bash
curl -X POST http://localhost:8000/api/v1/clone \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "mode": "dynamic",
    "depth": 3,
    "use_tor": false,
    "discover_invisible": true,
    "ai_enabled": true
  }'
```

**Response:**
```json
{
  "job_id": "uuid-here",
  "status": "queued",
  "message": "Job created successfully"
}
```

**Check Job Status:**
```bash
curl http://localhost:8000/api/v1/jobs/{job_id}
```

**Download Result as ZIP:**
```bash
curl -O http://localhost:8000/api/v1/download/{job_id}
```

**List All Jobs:**
```bash
curl http://localhost:8000/api/v1/jobs
```

#### Advanced CLI Examples

**Batch Cloning Multiple Sites:**
```bash
#!/bin/bash
sites=(
  "https://example1.com"
  "https://example2.com"
  "https://example3.com"
)

for site in "${sites[@]}"; do
  echo "Cloning $site..."
  web-all clone "$site" -o "batch_output" -d 2 -c 5 --delay 0.3
done
```

**Custom User Agent:**
```python
from web_all.core.cloner import SiteCloner

cloner = SiteCloner(
    output_dir="./output",
    user_agent="Mozilla/5.0 (compatible; MyBot/1.0)"
)
```

---

## 📖 API Reference

### CLI Commands

```bash
web-all clone <url> [options]     # Full website clone
web-all images <url> [options]    # Download images only
web-all text <url> [options]      # Extract text only
web-all serve [options]           # Start web server
web-all --help                    # Show help
wa <command>                      # Shortcut for all commands
```

### Clone Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output` | `-o` | Output directory | `./output` |
| `--depth` | `-d` | Crawl depth (0 = unlimited) | `2` |
| `--concurrency` | `-c` | Concurrent requests | `5` |
| `--delay` | | Delay between requests (seconds) | `0.5` |
| `--tor` | | Use Tor proxy | `False` |
| `--dynamic` | | Use dynamic rendering | `False` |
| `--discover-invisible` | | Discover hidden content | `False` |
| `--everything` | | Enable all advanced features | `False` |
| `--ai-enabled` | | Enable AI analysis | `False` |
| `--max-pages` | | Maximum pages to crawl | `100` |

### Serve Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--port` | `-p` | Server port | `8000` |
| `--host` | | Server host | `127.0.0.1` |
| `--no-gui` | | API only, no GUI | `False` |

### REST API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/v1/clone` | POST | Create clone job |
| `/api/v1/jobs/{id}` | GET | Get job status |
| `/api/v1/jobs` | GET | List all jobs |
| `/api/v1/download/{id}` | GET | Download ZIP |
| `/api/v1/ai/config` | GET/POST | AI configuration |
| `/api/v1/ai/providers` | GET | List AI providers |
| `/api/v1/ai/test` | POST | Test AI connection |

---

## 🔍 Troubleshooting

### Common Issues

**1. Playwright Error**
```bash
python -m playwright install chromium
python -m playwright install-deps chromium
```

**2. Tor Not Working**
- Ensure Tor service is running: `systemctl start tor` (Linux) or `brew services start tor` (macOS)
- Default proxy: `http://127.0.0.1:9050`

**3. AI Not Responding**
- For Ollama: Ensure `ollama serve` is running
- Check API keys for external providers
- Test connection: `curl -X POST http://localhost:8000/api/v1/ai/test`

**4. Permission Errors**
```bash
chmod -R 755 ./output
```

**5. Memory Issues**
- Reduce concurrency: `-c 3`
- Reduce depth: `-d 1`
- Close other applications

**6. Port Already in Use**
```bash
# Use a different port
web-all serve --port 8080
```

**7. Docker Permission Denied**
```bash
# Run Docker with sudo or add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

---

## 📁 Output Structure

```
output/
└── example_com/
    ├── index.html              # Main page
    ├── about/
    │   └── index.html          # Nested pages
    ├── images/                 # All images
    ├── css/                    # Stylesheets
    ├── js/                     # JavaScript files
    ├── manifest.json           # Clone metadata
    ├── README.txt              # Summary report
    └── ai_analysis.json        # AI results (if enabled)
```

---

## ✅ Best Practices

1. **Respect robots.txt**: Always check website terms of service
2. **Rate limiting**: Use `--delay` to avoid overloading servers (recommended: 0.3-1.0s)
3. **Concurrency**: Start low (`-c 5`) and increase if needed
4. **Depth**: Most sites work well with `-d 2` or `-d 3`
5. **Dynamic mode**: Only use when necessary (slower than static)
6. **Monitor resources**: Large clones can consume significant disk space
7. **Use Tor responsibly**: Only for legitimate .onion site access

---

Made with ❤️ for the web archiving community
