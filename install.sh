#!/bin/bash
# web-all Universal Installer
# One-command installation for noob users

set -e

echo "🕷️  web-all Universal Installer"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    echo "Please install Python 3.10+ first:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  macOS: brew install python@3.11"
    echo "  Windows: Download from https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python $PYTHON_VERSION"

# Check Python version (need 3.10+)
REQUIRED_VERSION="3.10"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python 3.10+ required. You have $PYTHON_VERSION"
    exit 1
fi

# Install pip if not available
if ! command -v pip3 &> /dev/null; then
    echo "⚠️  pip not found, installing..."
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3
fi

echo ""
echo "📦 Installing web-all dependencies..."

# Upgrade pip
python3 -m pip install --upgrade pip --quiet

# Install web-all in current directory (development mode)
echo "🔧 Installing web-all package..."
python3 -m pip install -e . --quiet

# Install Playwright browsers
echo "🌐 Installing Chromium browser for Playwright..."
python3 -m playwright install chromium

echo ""
echo "✅ Installation complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📖 Quick Start Guide:"
echo ""
echo "  CLI Mode:"
echo "    web-all clone https://example.com --output ./mycopy"
echo ""
echo "  GUI Mode:"
echo "    web-all serve"
echo "    Then open http://localhost:8000"
echo ""
echo "  Help:"
echo "    web-all --help"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎉 Happy cloning!"
