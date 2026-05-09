# 🐧 web-all Installation Guide for Kubuntu/Linux

## ✅ Quick Installation (Recommended)

### Step 1: Install System Dependencies

Open a terminal and run:

```bash
# Update package list
sudo apt update

# Install Python 3.10+ and pip (if not already installed)
sudo apt install -y python3 python3-pip python3-venv

# Install required system libraries for Playwright/Chromium
sudo apt install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libdrm2 libdbus-1-3 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libasound2 libpango-1.0-0 libcairo2
```

### Step 2: Install web-all

Choose one of these methods:

#### Method A: Using the install script (Easiest)
```bash
cd /path/to/web-all
chmod +x install.sh
./install.sh
```

#### Method B: Manual installation
```bash
cd /path/to/web-all

# Install in development mode
pip3 install -e .

# Install Playwright browser (Chromium)
python3 -m playwright install chromium

# Install Playwright system dependencies
python3 -m playwright install-deps chromium
```

#### Method C: Install from PyPI
```bash
pip3 install web-all
python3 -m playwright install chromium
python3 -m playwright install-deps chromium
```

### Step 3: Verify Installation

```bash
# Check version
web-all --version
# Should output: web-all v4.2.0

# Check help
web-all --help
```

---

## 🚀 How to Use

### CLI Commands

#### 1. Clone a Website
```bash
# Basic clone
web-all clone https://example.com -o mysite

# Clone with dynamic rendering (for JavaScript-heavy sites)
web-all clone https://example.com -o mysite --dynamic

# Clone everything (dynamic + hidden content discovery)
web-all clone https://example.com -o mysite --everything

# Deep crawl (depth 0 = all pages)
web-all clone https://example.com -o mysite -d 0 --max-pages 100
```

#### 2. Download Images
```bash
web-all images https://example.com -o images_folder
```

#### 3. Extract Text
```bash
web-all text https://example.com -o text_folder
```

#### 4. Start Web GUI Server
```bash
# Start server on default port (8000)
web-all serve

# Start on custom port
web-all serve -p 8080

# API only (no GUI)
web-all serve --no-gui
```

Then open your browser at: `http://localhost:8000`

---

## ✅ Verification Tests

Run these tests to ensure everything works:

### Test 1: Basic Clone
```bash
cd /tmp
web-all clone https://example.com -o test_clone
ls -la test_clone/example_com/
cat test_clone/example_com/index.html
```

Expected: Should see HTML files downloaded successfully.

### Test 2: Text Extraction
```bash
web-all text https://example.com -o test_text
cat test_text/example_com.txt
```

Expected: Should extract visible text from the page.

### Test 3: Run Unit Tests
```bash
cd /path/to/web-all
pip3 install pytest pytest-asyncio
python3 -m pytest tests/ -v
```

Expected: All 37 tests should pass.

### Test 4: Web Server
```bash
# Start server (in background or new terminal)
web-all serve -p 8080 &

# Test API endpoint
curl http://localhost:8080/api/health

# Stop server
kill %1
```

Expected: Health check should return `{"status": "ok"}`

---

## 🔧 Troubleshooting

### Issue: "No space left on device" during Playwright install
**Solution:** Free up disk space or install to a different location:
```bash
# Check available space
df -h

# Clean up old files
sudo apt autoremove
sudo apt clean
```

### Issue: Missing system libraries
**Solution:** Install all required dependencies:
```bash
python3 -m playwright install-deps chromium
```

### Issue: Permission errors
**Solution:** Use user-level installation:
```bash
pip3 install --user -e .
```

### Issue: Python version too old
**Solution:** web-all requires Python 3.10+:
```bash
# Check version
python3 --version

# If needed, install newer Python
sudo apt install python3.11 python3.11-venv python3.11-dev
```

---

## 📋 Features Summary

✅ **Multi-Language Support**: 11 languages (EN, ES, FR, DE, ZH, JA, KO, RU, AR, PT, IT)  
✅ **Full Website Cloning**: HTML, CSS, JS, images, fonts, videos  
✅ **Hidden Content Discovery**: Click/hover elements, lazy-loading, accordions  
✅ **Dynamic Rendering**: Headless browser for JavaScript SPAs  
✅ **AI-Powered Analysis**: Auto-summarize and extract data  
✅ **Web GUI**: Beautiful browser-based dashboard  
✅ **REST API**: Programmatic access with job queue  
✅ **CLI**: Fast command-line interface  

---

## 🎯 Quick Start Examples

### Beginner: Clone a simple site
```bash
web-all clone https://example.com -o my_first_clone
```

### Intermediate: Clone with all features
```bash
web-all clone https://react-site.com -o full_clone --everything --dynamic
```

### Advanced: Start GUI and use browser interface
```bash
web-all serve
# Open http://localhost:8000 in browser
```

---

## 📞 Need Help?

- View detailed help: `web-all --help`
- Command-specific help: `web-all clone --help`
- Documentation: See README.md in the project directory
- Issues: Report bugs on GitHub

---

**🎉 Enjoy cloning websites with web-all!**
