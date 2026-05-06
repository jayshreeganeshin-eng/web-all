# 🌐 web-all v3.0 - Complete Installation & Deployment Guide

**Universal Website Cloner & Crawler with Tor Support and AI Integration**

---

## 📋 Table of Contents

1. [Features](#features)
2. [Localhost Installation](#localhost-installation)
3. [InfinityFree Deployment](#infinityfree-deployment)
4. [Usage Guide](#usage-guide)
5. [Troubleshooting](#troubleshooting)

---

## ✨ Features

- 🔗 **Full Site Cloning** - Download complete websites with all assets
- 🧅 **Tor/.onion Support** - Clone hidden services anonymously
- 🔍 **Invisible Content Discovery** - Click, hover, scroll to reveal hidden elements
- 📸 **Image Downloader** - Extract all images including lazy-loaded
- 📝 **Text Extractor** - Clean text extraction from any page
- ⚡ **Dynamic JS Support** - Handle JavaScript-heavy sites with headless browser
- 🤖 **AI Integration** - Auto-summarization, tagging, and data extraction (optional)
- 🌍 **Web GUI** - Beautiful browser-based interface
- 🔌 **REST API** - Programmatic access with job queue
- 📦 **One-Command Install** - Easy setup for beginners

---

## 🏠 Localhost Installation

### Prerequisites

- **Python 3.10 or higher** ([Download](https://www.python.org/downloads/))
- **pip** (comes with Python 3.10+)
- **Git** (optional, for cloning the repository)
- **Tor** (optional, for .onion sites)

### Method 1: One-Command Installation (Recommended)

```bash
# Navigate to the project directory
cd web_all_project

# Make installer executable
chmod +x install.sh

# Run the installer
./install.sh
```

The installer will:
1. Check Python version
2. Create a virtual environment (optional)
3. Install all dependencies
4. Install Playwright browsers
5. Set up the web-all package
6. Create output directories

### Method 2: Manual Installation

```bash
# Step 1: Install dependencies
pip install requests beautifulsoup4 lxml playwright fastapi uvicorn python-multipart aiohttp

# Step 2: Install Playwright browsers
python -m playwright install chromium

# Step 3: Install the package
pip install -e .

# Step 4: Verify installation
web-all --help
```

### For .onion Sites (Optional)

**Linux:**
```bash
sudo apt update
sudo apt install tor
sudo systemctl start tor
sudo systemctl enable tor
```

**macOS:**
```bash
brew install tor
brew services start tor
```

**Windows:**
1. Download Tor Expert Bundle from https://www.torproject.org/download/
2. Extract and run `tor.exe`
3. Keep it running in the background

---

## ☁️ InfinityFree Deployment

**Important:** InfinityFree only supports **static websites** (HTML, CSS, JavaScript). The web-all cloning tool runs on your **local computer**, and you upload the **cloned results** to InfinityFree.

### Step-by-Step Guide

#### Step 1: Clone Website Locally

```bash
# Activate virtual environment if created
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Clone the website you want to host
web-all clone https://example.com -o ./mysite --depth 3
```

#### Step 2: Prepare Files for Upload

Your cloned site will be in the `./mysite` directory with this structure:
```
mysite/
├── example_com/
│   ├── index.html
│   ├── css/
│   ├── js/
│   ├── images/
│   └── manifest.json
```

#### Step 3: Upload to InfinityFree

**Method A: Using FTP (Recommended)**

1. **Get FTP Credentials:**
   - Log in to InfinityFree control panel
   - Go to "FTP Details" section
   - Note: Hostname, Username, Password

2. **Connect via FTP Client:**
   - Download FileZilla or similar FTP client
   - Connect using your FTP credentials
   - Navigate to `/htdocs/` folder

3. **Upload Files:**
   - Drag all files from `mysite/example_com/` to `/htdocs/`
   - Wait for upload to complete

**Method B: Using Online File Manager**

1. Log in to InfinityFree control panel
2. Go to "File Manager"
3. Navigate to `htdocs`
4. Upload files individually or as ZIP:
   - Compress your cloned site: 
     ```bash
     cd mysite/example_com
     zip -r ../site.zip .
     ```
   - Upload `site.zip` via File Manager
   - Extract using File Manager's extract feature

**Method C: Using Command Line (Advanced)**

```bash
# Install lftp
sudo apt install lftp  # Linux
brew install lftp      # macOS

# Upload via command line
lftp -u YOUR_USERNAME,YOUR_PASSWORD ftpupload.net << EOF
mirror ./mysite/example_com /htdocs
bye
EOF
```

#### Step 4: Verify Your Site

1. Visit your InfinityFree domain (e.g., `yoursite.rf.gd`)
2. Check that all pages load correctly
3. Verify images and CSS are working
4. Test navigation links

---

## 💻 Usage Guide

### CLI Commands

```bash
# Clone a complete website
web-all clone https://example.com -o ./mysite

# Clone with custom depth
web-all clone https://example.com -o ./mysite --depth 5

# Use dynamic mode for JavaScript sites
web-all clone https://example.com -o ./mysite --dynamic

# Clone .onion site (requires Tor)
web-all clone http://example.onion --tor -o ./onion-site

# Download all images
web-all images https://gallery.com -o ./images

# Extract text content
web-all text https://docs.example.com -o ./text

# Discover hidden content
web-all discover https://site.com --scrolls 10

# Start web GUI
web-all serve
```

### Web GUI

1. **Start the server:**
   ```bash
   web-all serve
   ```

2. **Open your browser:**
   ```
   http://localhost:8000
   ```

3. **Use the interface:**
   - Enter target URL
   - Select options (Tor, depth, mode)
   - Click "Start Cloning"
   - Monitor progress
   - Download results

### API Usage

```bash
# Start API server
web-all serve

# Create a clone job
curl -X POST http://localhost:8000/api/v1/clone \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "depth": 2,
    "mode": "static",
    "use_tor": false
  }'

# Check job status
curl http://localhost:8000/api/v1/jobs/{job_id}

# List all jobs
curl http://localhost:8000/api/v1/jobs

# Download result
curl http://localhost:8000/api/v1/download/{job_id}
```

### AI Features (Optional)

web-all supports multiple free AI providers:

1. **Ollama** (Local, completely free)
2. **Groq Cloud** (Free tier available)
3. **OpenRouter** (Free tier with multiple models)
4. **HuggingFace** (Free inference API)

**Configure AI:**
- Via Web GUI: Go to "AI Settings" tab
- Via API: POST to `/api/v1/ai/config`

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Playwright Browser Installation Fails

```bash
# Force reinstall
python -m playwright install chromium --force

# Or install system dependencies (Linux)
sudo apt-get install libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 libpango-1.0-0 libcairo2
```

#### 2. Tor Connection Failed

```bash
# Check if Tor is running
systemctl status tor  # Linux
brew services list    # macOS

# Start Tor
sudo systemctl start tor  # Linux
brew services start tor   # macOS

# Test connection
curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org
```

#### 3. Permission Errors

```bash
# Fix ownership
sudo chown -R $USER:$USER ./output

# Fix permissions
chmod -R 755 ./output
```

#### 4. Module Not Found Error

```bash
# Reinstall package
pip uninstall web-all
pip install -e .

# Or install missing dependency
pip install <missing-module>
```

#### 5. Virtual Environment Issues

```bash
# Delete and recreate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

#### 6. InfinityFree Upload Issues

- **File size limit:** InfinityFree has a 10MB per file limit
  - Solution: Compress images before uploading
  - Use FTP instead of File Manager for large uploads

- **Wrong directory:** Files must be in `/htdocs/`
  - Solution: Upload to correct folder

- **Index file not found:** Main page must be named `index.html`
  - Solution: Rename main file to `index.html`

---

## 📊 Configuration Options

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

---

## ⚖️ Legal & Ethical Use

- ✅ Respect `robots.txt` files
- ✅ Don't overload servers (use delays)
- ✅ Only clone sites you have permission to
- ✅ Follow terms of service
- ✅ Comply with copyright laws
- ❌ Don't use for malicious purposes
- ❌ Don't violate website terms

---

## 📞 Support

- **Documentation:** Check README.md
- **Issues:** Report bugs via GitHub Issues
- **Discussions:** Join community discussions

---

## 🎉 Quick Reference

### Localhost Setup (5 minutes)
```bash
cd web_all_project
./install.sh
web-all serve
# Open http://localhost:8000
```

### InfinityFree Deployment (10 minutes)
```bash
# 1. Clone locally
web-all clone https://yoursite.com -o ./upload

# 2. Upload via FTP
# Connect to ftpupload.net with your credentials
# Upload contents of ./upload to /htdocs/

# 3. Visit your domain
# https://yourdomain.rf.gd
```

---

**Happy Cloning! 🚀**
