# 🌐 web-all v2.0.0

**Universal Website Cloner & Crawler with Tor Support**

Clone any website including .onion sites, discover hidden content, download images/text, and host on InfinityFree!

## ✨ Features

- 🔗 **Full Site Cloning** - Download complete websites with all assets
- 🧅 **Tor/.onion Support** - Clone hidden services anonymously
- 🔍 **Invisible Content Discovery** - Click, hover, scroll to reveal hidden elements
- 📸 **Image Downloader** - Extract all images including lazy-loaded
- 📝 **Text Extractor** - Clean text extraction from any page
- ⚡ **Dynamic JS Support** - Handle JavaScript-heavy sites with headless browser
- 🌍 **Web GUI** - Beautiful browser-based interface
- 🔌 **REST API** - Programmatic access with job queue
- 📦 **One-Command Install** - Easy setup for beginners

## 🚀 Quick Start

### Installation (Single Command)

```bash
cd web_all_project
./install.sh
```

Or manually:

```bash
pip install requests beautifulsoup4 lxml playwright fastapi uvicorn
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
EOF
```

## 📁 Project Structure

```
web_all_project/
├── cli.py                 # Command-line interface
├── web_all/
│   ├── __init__.py        # Package init
│   ├── core/
│   │   ├── cloner.py      # Main cloning engine
│   │   └── invisible.py   # Hidden content discovery
│   ├── api/
│   │   └── server.py      # FastAPI REST server
│   └── gui/
│       └── index.html     # Web interface
├── tests/                 # Test suite
├── output/                # Downloaded content
├── install.sh             # One-command installer
├── pyproject.toml         # Package configuration
└── README.md              # This file
```

## ⚙️ Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output` | Output directory | `./output` |
| `-d, --depth` | Crawl depth (0-10) | 2 |
| `-c, --concurrency` | Concurrent requests | 3 |
| `--delay` | Delay between requests (seconds) | 1.0 |
| `--tor` | Use Tor proxy | false |
| `--tor-proxy` | Tor proxy address | `http://127.0.0.1:9050` |
| `--dynamic` | Use headless browser | false |
| `--scrolls` | Scroll iterations for discovery | 5 |

## 🔒 Legal & Ethical Use

- Respect `robots.txt` files
- Don't overload servers (use delays)
- Only clone sites you have permission to
- Follow terms of service
- Comply with copyright laws

## 🛠️ Troubleshooting

### Playwright Browser Issues
```bash
python -m playwright install chromium --force
```

### Tor Connection Failed
```bash
# Check if Tor is running
systemctl status tor
# Or start it
sudo systemctl start tor
```

### Permission Errors
```bash
chmod +x install.sh
sudo chown -R $USER:$USER ./output
```

## 📝 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## 📞 Support

- Documentation: https://github.com/web-all/web-all/wiki
- Issues: https://github.com/web-all/web-all/issues
- Discussions: https://github.com/web-all/web-all/discussions
