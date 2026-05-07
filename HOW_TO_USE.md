# 🚀 web-all v3.0 - How to Use Guide

## 📋 Table of Contents
1. [Quick Start (Easy)](#-level-1-easy---beginner)
2. [Intermediate Usage (Normal)](#-level-2-normal---intermediate)
3. [Advanced Usage (Hard)](#-level-3-hard---expert)
4. [API Reference](#api-reference)
5. [Troubleshooting](#troubleshooting)

---

## 🟢 Level 1: Easy - Beginner

### Step 1: Installation
```bash
# Clone or navigate to the project directory
cd /workspace

# Install the package
pip install -e .

# Install Playwright browser (required for dynamic sites)
python -m playwright install chromium
```

### Step 2: Basic Website Clone
```bash
# Clone any website with one command
web-all clone https://example.com -o my_website
```

**What this does:**
- Downloads all HTML pages
- Saves all images, CSS, and JavaScript files
- Organizes files in folders: `/images`, `/css`, `/js`
- Creates a `manifest.json` with clone information

### Step 3: View Your Cloned Site
```bash
# Navigate to output folder
cd my_website/example_com

# Open index.html in your browser
open index.html  # macOS
xdg-open index.html  # Linux
start index.html  # Windows
```

### Step 4: Download Only Images
```bash
web-all images https://example.com -o my_images
```

### Step 5: Extract Text Content
```bash
web-all text https://example.com -o my_text
```

### Step 6: Start Web GUI (Optional)
```bash
# Start the web server with beautiful GUI
web-all serve

# Open your browser to: http://localhost:8000
```

---

## 🟡 Level 2: Normal - Intermediate

### Clone with Custom Depth
```bash
# Crawl deeper into the website (default is 2 levels)
web-all clone https://example.com -o deep_clone -d 5
```
- `-d 5`: Crawl 5 levels deep
- Higher numbers = more pages but slower

### Increase Speed with Concurrency
```bash
# Download multiple pages simultaneously
web-all clone https://example.com -o fast_clone -c 10 --delay 0.2
```
- `-c 10`: Use 10 concurrent connections
- `--delay 0.2`: Wait 0.2 seconds between requests

### Clone JavaScript-Heavy Sites
```bash
# For sites that use React, Vue, Angular, etc.
web-all clone https://example.com -o dynamic_site --dynamic
```

### Discover Hidden Content
```bash
# Find content behind buttons, accordions, lazy-loading
web-all clone https://example.com -o hidden_content --discover-invisible
```

### Clone .onion Sites (Tor)
```bash
# First, make sure Tor is running
# Then clone onion sites
web-all clone http://example.onion -o onion_site --tor
```

### Combined Options Example
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

### Export as ZIP
After cloning, the system automatically creates organized folders. To create a ZIP:
```python
from web_all.utils.zip_utils import create_zip_archive

zip_path = create_zip_archive("./output/example_com")
print(f"Created: {zip_path}")
```

---

## 🔴 Level 3: Hard - Expert

### Programmatic Usage in Python

#### Basic Cloning Script
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

asyncio.run(clone_website())
```

#### Dynamic Cloning with Invisible Content
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

asyncio.run(advanced_clone())
```

### Using AI Features

#### Setup Ollama (Local AI - Free)
```bash
# Install Ollama from https://ollama.ai
# Pull a model
ollama pull llama3

# Configure AI via API
curl -X POST http://localhost:8000/api/v1/ai/config \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "provider": "ollama",
    "model": "llama3",
    "base_url": "http://localhost:11434"
  }'
```

#### Setup OpenRouter (Free Tier Available)
```bash
# Get free API key from https://openrouter.ai
curl -X POST http://localhost:8000/api/v1/ai/config \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "provider": "openrouter",
    "api_key": "your-api-key-here",
    "model": "mistralai/mistral-7b-instruct:free"
  }'
```

#### Setup Groq Cloud (Free Tier)
```bash
# Get free API key from https://groq.cloud
curl -X POST http://localhost:8000/api/v1/ai/config \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "provider": "groq",
    "api_key": "your-api-key-here",
    "model": "llama3-8b-8192"
  }'
```

#### Clone with AI Analysis
```bash
# Start server first
web-all serve &

# Clone with AI enabled
curl -X POST http://localhost:8000/api/v1/clone \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "depth": 3,
    "ai_enabled": true,
    "discover_invisible": true
  }'
```

AI will automatically:
- Summarize page content
- Extract structured data (products, articles, contacts)
- Generate relevant tags
- Clean HTML by removing ads/navigation

### REST API Usage

#### Create Clone Job
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

Response:
```json
{
  "job_id": "uuid-here",
  "status": "queued",
  "message": "Job created successfully"
}
```

#### Check Job Status
```bash
curl http://localhost:8000/api/v1/jobs/{job_id}
```

#### Download Result as ZIP
```bash
curl -O http://localhost:8000/api/v1/download/{job_id}
```

#### List All Jobs
```bash
curl http://localhost:8000/api/v1/jobs
```

### Docker Deployment

```bash
# Build Docker image
docker build -t web-all .

# Run container
docker run -p 8000:8000 -v $(pwd)/output:/app/output web-all

# Access GUI at http://localhost:8000
```

---

## API Reference

### Endpoints

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

### CLI Commands

```bash
web-all clone <url> [options]     # Full website clone
web-all images <url> [options]    # Download images only
web-all text <url> [options]      # Extract text only
web-all serve [options]           # Start web server
web-all --help                    # Show help
```

---

## Troubleshooting

### Common Issues

**1. Playwright Error**
```bash
python -m playwright install chromium
python -m playwright install-deps chromium
```

**2. Tor Not Working**
- Ensure Tor service is running: `systemctl start tor`
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

---

## Output Structure

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

## Best Practices

1. **Respect robots.txt**: Always check website terms
2. **Rate limiting**: Use `--delay` to avoid overloading servers
3. **Concurrency**: Start low (`-c 5`) and increase if needed
4. **Depth**: Most sites work well with `-d 2` or `-d 3`
5. **Dynamic mode**: Only use when necessary (slower than static)

---

Made with ❤️ for the web archiving community
