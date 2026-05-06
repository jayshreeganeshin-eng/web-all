# 🕷️ web-all v3.0.0 - Complete Installation & Usage Guide

**Universal Website Cloner & Crawler with Tor Support, AI Enhancement, and InfinityFree Deployment**

---

## 📋 Table of Contents

1. [Features](#features)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
   - [Local Installation (Linux/Mac/WSL)](#local-installation-linuxmacwsl)
   - [Windows Installation](#windows-installation)
   - [Docker Installation](#docker-installation)
4. [Quick Start](#quick-start)
5. [CLI Commands Reference](#cli-commands-reference)
6. [Web GUI Usage](#web-gui-usage)
7. [REST API Documentation](#rest-api-documentation)
8. [Hosting on InfinityFree](#hosting-on-infinityfree)
9. [Troubleshooting](#troubleshooting)
10. [Legal & Ethics](#legal--ethics)

---

## ✨ Features

### Core Capabilities
- **🌐 Full Website Cloning** - Download complete websites with all assets (HTML, CSS, JS, images)
- **🧅 Tor/.onion Support** - Clone hidden services anonymously through Tor network
- **🔍 Invisible Content Discovery** - Click, hover, scroll to reveal hidden elements
- **📸 Image Downloader** - Extract all images including lazy-loaded content
- **📝 Text Extractor** - Clean text extraction from any page
- **⚡ Dynamic JS Support** - Handle JavaScript-heavy sites with headless browser
- **🤖 AI Enhancement** - Auto-summarization, tagging, and structured data extraction
- **📦 ZIP Packaging** - Package cloned sites into downloadable ZIP files

### Interfaces
- **💻 CLI** - Full-featured command-line interface
- **🌍 Web GUI** - Beautiful browser-based interface
- **🔌 REST API** - Programmatic access with job queue system

---

## 💻 System Requirements

### Minimum Requirements
- **Python**: 3.10 or higher
- **RAM**: 2GB minimum (4GB recommended)
- **Disk Space**: 1GB free space
- **OS**: Linux, macOS, Windows 10+, or WSL

### For Tor Support (.onion sites)
- **Tor Browser** OR **Tor Daemon** installed and running

### For AI Features (Optional)
- **Ollama** (local, free) OR
- **API Key** from OpenRouter/Groq/HuggingFace

---

## 🚀 Installation

### Local Installation (Linux/Mac/WSL)

#### Option 1: One-Command Installer (Recommended)

```bash
# Clone or navigate to the project directory
cd /path/to/web_all_final

# Make installer executable
chmod +x install.sh

# Run installer
./install.sh
```

#### Option 2: Manual Installation

```bash
# Step 1: Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
# or on Windows: venv\Scripts\activate

# Step 2: Upgrade pip
pip install --upgrade pip

# Step 3: Install dependencies
pip install requests beautifulsoup4 lxml playwright fastapi uvicorn python-multipart aiohttp yt-dlp

# Step 4: Install Playwright browsers
python -m playwright install chromium

# Step 5: Install web-all
pip install -e .
```

### Windows Installation

```powershell
# Step 1: Install Python 3.10+ from python.org
# Make sure to check "Add Python to PATH" during installation

# Step 2: Open PowerShell as Administrator
python -m venv venv
.\venv\Scripts\Activate.ps1

# Step 3: Install dependencies
pip install --upgrade pip
pip install requests beautifulsoup4 lxml playwright fastapi uvicorn python-multipart aiohttp yt-dlp

# Step 4: Install Playwright browsers
python -m playwright install chromium

# Step 5: Install web-all
pip install -e .
```

### Docker Installation

```bash
# Build Docker image
docker build -t web-all:latest .

# Run container
docker run -d \
  --name web-all \
  -p 8000:8000 \
  -v $(pwd)/output:/app/output \
  web-all:latest

# Access web GUI at http://localhost:8000
```

---

## ⚡ Quick Start

### Test Installation

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Check if web-all is installed
web-all --help

# Start the web GUI
web-all serve
```

Open your browser to **http://localhost:8000**

### Basic Usage Examples

```bash
# Clone a simple website
web-all clone https://example.com -o ./myclone

# Clone with deep crawling (depth 5)
web-all clone https://example.com -o ./deep-clone --depth 5 --dynamic

# Download all images from a gallery
web-all images https://photogallery.com -o ./gallery-images

# Extract text content
web-all text https://docs.example.com -o ./docs-text

# Discover hidden content (clicks, hovers, scrolls)
web-all discover https://site.com -o ./discovered --scrolls 10

# Clone a .onion site (requires Tor)
web-all clone http://example.onion --tor -o ./onion-site
```

---

## 📖 CLI Commands Reference

### `clone` - Full Website Clone

```bash
web-all clone <url> [options]

Options:
  -o, --output DIR        Output directory (default: ./output/clone)
  -d, --depth NUM         Crawl depth 0-10 (default: 2)
  -c, --concurrency NUM   Concurrent requests (default: 3)
  --delay SEC             Delay between requests (default: 1.0)
  --tor                   Use Tor proxy for .onion sites
  --tor-proxy URL         Custom Tor proxy address
  --dynamic               Use headless browser for JS sites
```

**Examples:**
```bash
web-all clone https://example.com -o ./site
web-all clone https://example.com --depth 5 --dynamic
web-all clone http://abc123.onion --tor
```

### `images` - Download Images Only

```bash
web-all images <url> [options]

Options:
  -o, --output DIR    Output directory (default: ./output/images)
  -d, --depth NUM     Crawl depth (default: 0)
  --tor               Use Tor proxy
  --dynamic           Use headless browser
```

### `text` - Extract Text Content

```bash
web-all text <url> [options]

Options:
  -o, --output DIR    Output directory (default: ./output/text)
  --tor               Use Tor proxy
  --dynamic           Use headless browser
```

### `discover` - Discover Invisible Content

```bash
web-all discover <url> [options]

Options:
  -o, --output DIR      Output directory (default: ./output/discovered)
  --tor                 Use Tor proxy
  --scrolls NUM         Number of scroll iterations (default: 5)
```

### `serve` - Start Web GUI Server

```bash
web-all serve [options]

Options:
  --host ADDR           Host to bind (default: 0.0.0.0)
  -p, --port NUM        Port number (default: 8000)
```

---

## 🌐 Web GUI Usage

1. **Start the server:**
   ```bash
   web-all serve
   ```

2. **Open your browser:**
   Navigate to `http://localhost:8000`

3. **Use the interface:**
   - Enter the target URL
   - Select mode (Clone, Images, Text, Discover)
   - Configure options (depth, Tor, dynamic)
   - Click "Start Download"
   - Monitor progress in real-time
   - Download results as ZIP when complete

---

## 🔌 REST API Documentation

### Start a Clone Job

```bash
curl -X POST http://localhost:8000/api/v1/clone \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "mode": "static",
    "depth": 2,
    "use_tor": false,
    "discover_invisible": false
  }'
```

**Response:**
```json
{
  "job_id": "abc123-def456",
  "status": "queued",
  "message": "Job created successfully"
}
```

### Check Job Status

```bash
curl http://localhost:8000/api/v1/jobs/{job_id}
```

**Response:**
```json
{
  "job_id": "abc123-def456",
  "status": "completed",
  "created_at": "2024-01-01T12:00:00",
  "completed_at": "2024-01-01T12:05:00",
  "manifest": { ... },
  "download_url": "/api/v1/download/abc123-def456"
}
```

### Download Result as ZIP

```bash
curl -O http://localhost:8000/api/v1/download/{job_id}
```

### List All Jobs

```bash
curl http://localhost:8000/api/v1/jobs
```

---

## 🌍 Hosting on InfinityFree

InfinityFree hosts **static websites only**. Follow these steps to upload your cloned site:

### Method 1: Manual FTP Upload

1. **Clone the website locally:**
   ```bash
   web-all clone https://yoursite.com -o ./for-upload --depth 3
   ```

2. **Get InfinityFree FTP credentials:**
   - Log in to your InfinityFree account
   - Go to Control Panel → FTP Details
   - Note: Host, Username, Password

3. **Upload via FTP client (FileZilla recommended):**
   - Connect to: `ftpupload.net` (or your assigned host)
   - Upload all files from `./for-upload` to `/htdocs/`
   - Wait for upload to complete

4. **Access your site:**
   - Visit your InfinityFree domain
   - Example: `http://yourdomain.rf.gd`

### Method 2: Command Line (lftp)

```bash
# Install lftp
sudo apt install lftp  # Linux
brew install lftp      # Mac

# Upload using lftp
lftp -u epiz_XXXXXX,YOUR_PASSWORD ftpupload.net << EOF
mirror ./for-upload /htdocs
bye
EOF
```

### Method 3: Using web-all's Built-in Upload (Coming Soon)

```bash
# Future feature - not yet implemented
web-all upload ./for-upload \
  --host ftpupload.net \
  --user epiz_XXXXXX \
  --password YOUR_PASSWORD
```

### ⚠️ Important Notes for InfinityFree

- **Static only**: PHP forms, databases won't work
- **File limits**: Max 400 files per directory
- **Size limits**: Total 5GB storage
- **No server-side scripts**: Only HTML, CSS, JS work
- **Broken features**: Contact forms, search, login systems

---

## 🛠️ Troubleshooting

### Playwright Browser Issues

**Problem**: Browser doesn't launch or crashes

```bash
# Reinstall Playwright browsers
python -m playwright install chromium --force

# On Linux, install dependencies
sudo apt-get install libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 libpango-1.0-0 libcairo2
```

### Tor Connection Failed

**Problem**: Can't connect to .onion sites

```bash
# Check if Tor is running
systemctl status tor  # Linux
brew services list    # Mac

# Start Tor service
sudo systemctl start tor      # Linux
brew services start tor       # Mac

# Or install Tor Browser and keep it running
```

### Permission Errors

**Problem**: Can't write to output directory

```bash
# Fix ownership
sudo chown -R $USER:$USER ./output

# Or use a different directory
web-all clone https://example.com -o ~/Downloads/clones
```

### Module Import Errors

**Problem**: `ModuleNotFoundError: No module named 'web_all'`

```bash
# Ensure you're in the project directory
cd /path/to/web_all_final

# Activate virtual environment
source venv/bin/activate

# Reinstall in development mode
pip install -e .
```

### Memory Issues

**Problem**: Out of memory during large clones

```bash
# Reduce concurrency
web-all clone https://large-site.com -o ./clone --concurrency 2

# Reduce depth
web-all clone https://large-site.com -o ./clone --depth 2
```

---

## ⚖️ Legal & Ethics

### Responsible Use Guidelines

1. **Respect robots.txt**: The tool respects robots.txt by default
2. **Rate limiting**: Use delays to avoid overloading servers
3. **Permission**: Only clone sites you own or have permission to
4. **Copyright**: Comply with copyright laws and terms of service
5. **Privacy**: Don't harvest personal data without consent
6. **Fair use**: Use for archiving, testing, or educational purposes

### Prohibited Uses

- ❌ Scraping protected content without authorization
- ❌ Bypassing paywalls or access controls
- ❌ Harvesting emails for spam
- ❌ Creating mirror sites for phishing
- ❌ Violating website terms of service

---

## 📞 Support

- **Documentation**: This README file
- **Issues**: Report bugs and feature requests
- **Discussions**: Ask questions and share tips

---

## 📄 License

MIT License - Free for personal and commercial use.

---

## 🎉 You're Ready!

Your web-all installation is complete. Start cloning websites now:

```bash
web-all clone https://example.com -o ./first-clone
web-all serve  # Launch web GUI
```

**Happy cloning! 🕷️**
