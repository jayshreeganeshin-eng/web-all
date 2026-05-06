# 🌐 web-all v3.0.0

**AI-Powered Universal Website Cloner & Crawler with Tor Support**

Clone any website including .onion sites, discover hidden content, download images/text, analyze with AI, and host on InfinityFree!

## ✨ Features

- 🔗 **Full Site Cloning** - Download complete websites with all assets
- 🧅 **Tor/.onion Support** - Clone hidden services anonymously
- 🔍 **Invisible Content Discovery** - Click, hover, scroll to reveal hidden elements
- 📸 **Image Downloader** - Extract all images including lazy-loaded
- 📝 **Text Extractor** - Clean text extraction from any page
- ⚡ **Dynamic JS Support** - Handle JavaScript-heavy sites with headless browser
- 🤖 **AI Integration** - Auto-summarization, tagging, and data extraction (Ollama, Groq, OpenRouter, HuggingFace)
- 🌍 **Web GUI** - Beautiful browser-based interface
- 🔌 **REST API** - Programmatic access with job queue
- 📦 **One-Command Install** - Easy setup for beginners

## 🚀 Quick Start

### Installation (Single Command)

```bash
cd web_all_project
chmod +x install.sh
./install.sh
```

Or manually:

```bash
pip install requests beautifulsoup4 lxml playwright fastapi uvicorn python-multipart aiohttp
python -m playwright install chromium
pip install -e .
```

### For .onion Sites

1. Install Tor: `sudo apt install tor` (Linux) or `brew install tor` (macOS)
2. Start Tor service
3. Use `--tor` flag in commands

## 💻 Usage

### CLI Commands

```bash
# Clone a website
web-all clone https://example.com -o ./mysite

# Clone with deep crawling
web-all clone https://example.com -o ./mysite --depth 5 --dynamic

# Clone .onion site
web-all clone http://example.onion --tor -o ./onion-site

# Download all images
web-all images https://gallery.com -o ./images

# Extract text
web-all text https://docs.example.com -o ./text

# Discover hidden content
web-all discover https://site.com --scrolls 10

# Start web GUI
web-all serve
```

### Web GUI

1. Run: `web-all serve`
2. Open: http://localhost:8000
3. Enter URL, select options, click "Start Cloning"
4. Monitor progress and download results

### API Usage

```bash
# Start a clone job
curl -X POST http://localhost:8000/api/v1/clone \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "depth": 2, "use_tor": false}'

# Check job status
curl http://localhost:8000/api/v1/jobs/{job_id}
```

## 🌐 Hosting on InfinityFree

InfinityFree hosts static sites only. Here's how to upload your cloned site:

### Method 1: Manual Upload

1. Clone the site locally:
   ```bash
   web-all clone https://yoursite.com -o ./upload
   ```

2. Upload via FTP:
   - Connect to your InfinityFree FTP account
   - Upload all files from `./upload` to `/htdocs/`

### Method 2: Automatic (with FTP)

```bash
# After cloning, use an FTP client or script to upload
lftp -u username,password ftpupload.net << EOF
mirror ./upload /htdocs
bye
