#!/bin/bash
# web-all One-Command Installer
# Works on Linux, macOS, and WSL

set -e

echo "🚀 Installing web-all v3.0.0..."

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

# Create virtual environment (optional but recommended)
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install requests beautifulsoup4 lxml playwright fastapi uvicorn python-multipart

# Install browser for Playwright
echo "🌐 Installing Chromium browser (this may take a few minutes)..."
python -m playwright install chromium

# Install web-all in development mode
echo "🔧 Installing web-all..."
pip install -e .

echo ""
echo "✅ Installation complete!"
echo ""
echo "Usage:"
echo "  source venv/bin/activate"
echo "  web-all clone https://example.com -o ./mysite"
echo "  web-all serve  # Start web GUI at http://localhost:8000"
echo ""
echo "For .onion sites:"
echo "  1. Install Tor: sudo apt install tor (Linux) or brew install tor (macOS)"
echo "  2. Start Tor service"
echo "  3. Run: web-all clone http://example.onion --tor"
echo ""
