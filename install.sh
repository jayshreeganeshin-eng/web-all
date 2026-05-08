#!/bin/bash
# web-all Universal Installer v4
# One-command installation for noob users
# Automatically creates virtual environment for compatibility

set -e

echo "🕷️  web-all Universal Installer v4"
echo "==================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed.${NC}"
    echo "Please install Python 3.10+ first:"
    echo "  Ubuntu/Debian/Kubuntu: sudo apt install python3 python3-pip python3-venv"
    echo "  macOS: brew install python@3.11"
    echo "  Windows: Download from https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✅${NC} Found Python $PYTHON_VERSION"

# Check Python version (need 3.10+)
REQUIRED_VERSION="3.10"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}❌ Python 3.10+ required. You have $PYTHON_VERSION${NC}"
    exit 1
fi

# Check for venv module
if ! python3 -c "import venv" &> /dev/null; then
    echo -e "${YELLOW}⚠️  python3-venv not found, attempting to install...${NC}"
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y python3-venv python3-full
    else
        echo -e "${RED}❌ Please install python3-venv manually:${NC}"
        echo "  Ubuntu/Debian/Kubuntu: sudo apt install python3-venv python3-full"
        exit 1
    fi
fi

# Install pip if not available
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  pip not found, installing...${NC}"
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3
fi

echo ""
echo "📦 Setting up virtual environment..."

# Create virtual environment in the project directory
VENV_DIR=".venv"
if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment already exists, recreating...${NC}"
    rm -rf "$VENV_DIR"
fi

python3 -m venv "$VENV_DIR"
echo -e "${GREEN}✅${NC} Virtual environment created at $VENV_DIR"

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Verify we're in the venv
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${RED}❌ Failed to activate virtual environment${NC}"
    exit 1
fi

echo ""
echo "📦 Installing web-all dependencies..."

# Upgrade pip in venv
python -m pip install --upgrade pip --quiet

# Install wheel and setuptools
python -m pip install wheel setuptools --quiet

# Install web-all in current directory (development mode)
echo "🔧 Installing web-all package..."
python -m pip install -e . --quiet

# Install Playwright browsers (optional, can be done manually later)
echo "🌐 Installing Chromium browser for Playwright..."
if python -m playwright install chromium 2>&1; then
    echo "✅ Playwright browser installed successfully"
    
    # Install system dependencies for Playwright (Chromium)
    echo "🔧 Installing Playwright system dependencies..."
    python -m playwright install-deps chromium 2>/dev/null || {
        echo -e "${YELLOW}⚠️  Could not auto-install system dependencies.${NC}"
        echo "   You may need to run: sudo apt install libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 libpango-1.0-0 libcairo2"
    }
else
    echo -e "${YELLOW}⚠️  Playwright browser installation skipped (disk space or network issue).${NC}"
    echo "   You can install it later with: source .venv/bin/activate && playwright install chromium"
    echo "   Static mode will still work without Playwright!"
fi

echo ""
echo -e "${GREEN}✅ Installation complete!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📖 Quick Start Guide:"
echo ""
echo "  🚀 Option 1: Use the activation script"
echo "     source .venv/bin/activate"
echo "     web-all clone https://example.com --output ./mycopy"
echo ""
echo "  🚀 Option 2: Run directly with the venv python"
echo "     .venv/bin/web-all clone https://example.com --output ./mycopy"
echo ""
echo "  🖥️  GUI Mode:"
echo "     source .venv/bin/activate"
echo "     web-all serve"
echo "     Then open http://localhost:8000"
echo ""
echo "  ℹ️  Help:"
echo "     web-all --help"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}🎉 Happy cloning!${NC}"
echo ""
echo "💡 Tip: Add this to your ~/.bashrc for convenience:"
echo "   alias web-all='$(pwd)/.venv/bin/web-all'"
