# web-all v4.5.0 - Quick Start Guide

## 🚀 Installation Commands

### Command 1: Install with venv (Full Version)
```bash
# One-command installation with automatic virtual environment setup
curl -sSL https://raw.githubusercontent.com/web-all/web-all/main/install.sh | bash
```

Or manually:
```bash
chmod +x install.sh
./install.sh
```

This will:
- ✅ Check Python 3.10+ installation
- ✅ Create virtual environment at `~/.web-all-venv`
- ✅ Install all dependencies including full AI features
- ✅ Install Playwright browsers
- ✅ Set up CLI and GUI commands

---

## 🎯 Three Main Commands

After installation, you have **3 main commands** available:

### 1️⃣ `web-all-gui` - Full GUI Version
Launch the web-based graphical interface:
```bash
web-all-gui
```
Then open http://localhost:8000 in your browser.

**Features:**
- 🌐 Full visual interface
- 📊 Job management dashboard
- 🤖 AI configuration panel
- 📥 Download cloned sites as ZIP
- 🔍 Hidden content discovery
- 🌍 Multi-language support

---

### 2️⃣ `web-all-cli` - Interactive CLI Mode
Launch interactive command-line interface:
```bash
web-all-cli
```

Or use direct commands:
```bash
# Clone a website
web-all clone https://example.com --output ./mycopy

# Clone with everything (dynamic + hidden content + AI)
web-all clone https://example.com --everything

# Extract images only
web-all images https://example.com -o ./images

# Extract text only
web-all text https://example.com -o ./text

# Start server (API + GUI)
web-all serve --port 8000

# Help
web-all --help
```

---

### 3️⃣ `web-all` / `wa` - Universal Command
The main command that works for both CLI operations and server mode:
```bash
# Same as web-all
wa clone https://example.com
wa serve
wa --version
```

---

## 📦 Virtual Environment Management

The installer creates a virtual environment at `~/.web-all-venv`.

### Activate manually:
```bash
source ~/.web-all-venv/bin/activate
```

### Deactivate:
```bash
deactivate
```

### Custom venv location:
```bash
WEBALL_VENV=/path/to/custom/venv ./install.sh
```

---

## ✨ Key Features v4.5.0

- 🕷️ **Universal Website Cloning** - Clone any website worldwide
- 🌐 **Multi-Language Support** - 11 languages included
- 🧅 **Tor/.onion Support** - Access dark web content
- 🤖 **AI Integration** - 5 AI providers (Ollama, OpenRouter, Groq, HuggingFace, NVIDIA)
- 🔍 **Hidden Content Discovery** - Find invisible content on pages
- 📁 **Auto-Organize Assets** - Automatic organization of images, CSS, JS
- 📦 **ZIP Export** - Download complete clones as ZIP files
- 🎨 **Modern GUI** - Beautiful web-based interface
- 💻 **Powerful CLI** - Full-featured command-line tools

---

## 🔧 Troubleshooting

### Python not found:
```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip python3-venv

# macOS
brew install python@3.11

# Windows
# Download from https://python.org
```

### Permission errors:
```bash
# Make installer executable
chmod +x install.sh

# Run with sudo if needed
sudo ./install.sh
```

### Playwright browser issues:
```bash
# Reinstall browsers
playwright install chromium
```

---

## 📖 Documentation

- README.md - Full documentation
- HOW_TO_USE.md - Detailed usage guide
- SPECIFICATION.md - Technical specifications

---

**🎉 Happy cloning with web-all v4.5.0!**
