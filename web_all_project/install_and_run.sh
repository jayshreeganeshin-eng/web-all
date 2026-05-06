#!/bin/bash
# web-all v3.0.0 - Complete One-Command Installer & Runner
# Works on Linux, macOS, and WSL
# Single command to install everything and start using

set -e

echo "🚀 web-all v3.0.0 - Universal Website Cloner"
echo "=============================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.10+ is required but not installed."
    echo "Please install Python 3.10 or higher first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.10"

if [[ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]]; then
    echo "❌ Python 3.10+ required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install all dependencies
echo "📥 Installing dependencies..."
pip install requests beautifulsoup4 lxml playwright fastapi uvicorn python-multipart aiohttp yt-dlp --quiet

# Install browser for Playwright (Chromium only for faster install)
echo "🌐 Installing Chromium browser (this may take a few minutes)..."
python -m playwright install chromium --with-deps 2>/dev/null || python -m playwright install chromium

# Install web-all in development mode
echo "🔧 Installing web-all..."
pip install -e . --quiet

echo ""
echo "✅ Installation complete!"
echo ""
echo "=================================================="
echo "web-all v3.0.0 is ready to use!"
echo "=================================================="
echo ""
echo "Quick Start:"
echo "  source venv/bin/activate"
echo "  web-all clone https://example.com -o ./mysite"
echo ""
echo "Advanced Usage:"
echo "  web-all clone https://example.com --dynamic -d 3"
echo "  web-all images https://example.com -o ./images"
echo "  web-all text https://example.com -o ./text"
echo "  web-all discover https://example.com --scrolls 5"
echo "  web-all serve  # Start web GUI at http://localhost:8000"
echo ""
echo "For .onion sites:"
echo "  1. Install Tor: sudo apt install tor (Linux) or brew install tor (macOS)"
echo "  2. Start Tor service: sudo systemctl start tor"
echo "  3. Run: web-all clone http://example.onion --tor"
echo ""
echo "Features:"
echo "  ✅ Auto-download full websites with all assets"
echo "  ✅ Organized folder structure (images/, css/, js/)"
echo "  ✅ Dynamic JavaScript rendering support"
echo "  ✅ Tor/.onion anonymity support"
echo "  ✅ Invisible content discovery (click, hover, scroll)"
echo "  ✅ AI-powered analysis (optional)"
echo "  ✅ ZIP download for offline use"
echo "  ✅ REST API for automation"
echo "  ✅ Beautiful web GUI"
echo ""
