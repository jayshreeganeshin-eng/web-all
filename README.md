# 🕷️ web-all - Universal Website Cloner & Crawler

**The most advanced open-source tool for downloading entire websites including hidden content, videos, images, and text.**

## ✨ Features

### Core Capabilities
- **Full Website Cloning** - Download complete websites with all assets (HTML, CSS, JS, images)
- **Invisible Content Discovery** - Uncover hidden content behind clicks, hovers, accordions, and lazy-loading
- **Infinite Scroll Support** - Automatically scroll pages to load all dynamic content
- **Sitemap Parsing** - Discover pages from sitemap.xml that aren't linked
- **Path Guessing** - Find hidden admin/login pages automatically
- **Mobile Emulation** - Capture mobile-specific content (iPhone, Pixel, iPad)
- **Video Downloads** - Extract videos using yt-dlp integration
- **Text Extraction** - Clean text extraction from any website
- **Image Gallery Download** - Download all images from galleries
- **Interactive Login** - Manual login support with cookie saving
- **ZIP Archiving** - Package cloned sites into ZIP files
- **FTP Upload** - Direct upload to hosting providers (InfinityFree, etc.)

### Interfaces
- **CLI** - Full-featured command-line interface
- **Web GUI** - Beautiful browser-based interface
- **REST API** - Programmatic access with job queue

---

## 🚀 One-Command Installation

### For Noob Users (Easiest)
```bash
curl -sSL https://raw.githubusercontent.com/web-all/web-all/main/install.sh | bash
```

Or if you've already cloned the repo:
```bash
cd /path/to/web-all && ./install.sh
```

### Alternative Methods

**Via pip:**
```bash
pip install web-all
python -m playwright install chromium
```

**Via Docker:**
```bash
docker run -d --name web-all -p 8000:8000 -v $(pwd)/output:/app/output web-all:latest
```

---

## 💻 How to Run Locally

### CLI Mode (Command Line)

#### 1. Clone a Complete Website
```bash
web-all clone https://example.com -o ./mycopy --depth 5 --discover-invisible
```

#### 2. Download All Images
```bash
web-all images-only https://photogallery.com -o ./images --discover-invisible
```

#### 3. Extract Text Content
```bash
web-all text-only https://docs.example.com -o ./text --depth 3
```

#### 4. Download Videos
```bash
web-all videos-only https://youtube.com/playlist -o ./videos
```

#### 5. Capture as Mobile Device
```bash
web-all mobile-capture https://example.com -o mobile.html --device iphone12
```

#### 6. Interactive Login (for protected sites)
```bash
web-all login https://mysite.com/login -c cookies.json
```

#### 7. Deep Crawl with Sitemap
```bash
web-all deep-crawl https://example.com --sitemap --path-guess
```

#### 8. Create ZIP Archive
```bash
web-all archive ./mycopy -o backup.zip
```

#### 9. Upload to FTP (InfinityFree)
```bash
web-all upload ./mycopy --host ftpupload.net --user epiz_XXXXXX --password YOUR_PASS
```

#### 10. Start Web GUI Server
```bash
web-all serve --port 8000
# Open http://localhost:8000 in your browser
```

### GUI Mode (Web Interface)

1. **Start the server:** `web-all serve`
2. **Open browser:** Navigate to `http://localhost:8000`
3. **Use the interface:** Enter URL, select mode, click "Start Download"

---

## 🌐 How to Host on InfinityFree.com

### Method 1: Manual Upload
1. Clone locally: `web-all clone https://target-site.com -o ./for-upload`
2. Upload files via FTP to `/htdocs/` on InfinityFree
3. Access at your domain!

### Method 2: Direct FTP Upload
```bash
web-all upload ./for-upload --host ftpupload.net --user epiz_XXXXXX --password YOUR_PASSWORD
```

> ⚠️ Cloned sites are static mirrors. Dynamic features won't work.

---

## 📋 Command Reference

| Command | Description |
|---------|-------------|
| `clone` | Full website mirror |
| `scroll` | Single page infinite scroll |
| `images-only` | Download all images |
| `text-only` | Extract clean text |
| `videos-only` | Download videos |
| `mobile-capture` | Capture as mobile device |
| `login` | Interactive login |
| `archive` | Create ZIP archive |
| `upload` | Upload to FTP |
| `deep-crawl` | Crawl with sitemap |
| `serve` | Start web GUI |

---

## 🛡️ Ethics

- Respects `robots.txt` by default
- Configurable rate limiting
- Use responsibly and respect website terms

**Made with ❤️ for the web archiving community**
