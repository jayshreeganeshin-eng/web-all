#!/bin/bash
# web-all v4.5.0 Universal Installer
# One-command installation for all users with automatic venv setup

set -e

echo "🕷️  web-all v4.5.0 Universal Installer"
echo "======================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed.${NC}"
    echo "Please install Python 3.10+ first:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  macOS: brew install python@3.11"
    echo "  Windows: Download from https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✅ Found Python $PYTHON_VERSION${NC}"

# Check Python version (need 3.10+)
REQUIRED_VERSION="3.10"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}❌ Python 3.10+ required. You have $PYTHON_VERSION${NC}"
    exit 1
fi

# Install pip if not available
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  pip not found, installing...${NC}"
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3
fi

# Detect OS and install system dependencies
echo ""
echo -e "${YELLOW}📦 Checking system dependencies...${NC}"

if [ -f /etc/debian_version ]; then
    # Debian/Ubuntu/Kubuntu
    if ! dpkg -l | grep -q "python3-venv"; then
        echo -e "${YELLOW}⚠️  Installing python3-venv...${NC}"
        sudo apt-get update -qq && sudo apt-get install -y -qq python3-venv python3-dev build-essential
    fi
elif [ -f /etc/redhat-release ]; then
    # RHEL/CentOS/Fedora
    if ! rpm -qa | grep -q "python3-virtualenv"; then
        echo -e "${YELLOW}⚠️  Installing python3-virtualenv...${NC}"
        sudo dnf install -y -q python3-virtualenv python3-devel gcc
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo -e "${YELLOW}⚠️  macOS detected, ensuring Xcode tools...${NC}"
    xcode-select --install 2>/dev/null || true
fi

echo ""
echo -e "${GREEN}🔧 Setting up virtual environment...${NC}"

# Create virtual environment in user's home or current directory
if [ -z "$WEBALL_VENV" ]; then
    VENV_DIR="$HOME/.web-all-venv"
else
    VENV_DIR="$WEBALL_VENV"
fi

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✅ Created virtual environment at $VENV_DIR${NC}"
else
    echo -e "${GREEN}✅ Virtual environment already exists at $VENV_DIR${NC}"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Upgrade pip in venv
echo ""
echo -e "${YELLOW}📦 Upgrading pip in virtual environment...${NC}"
pip install --upgrade pip

# Install web-all with full dependencies
echo ""
echo -e "${YELLOW}🔧 Installing web-all v4.5.0 with full dependencies...${NC}"
pip install -e ".[full,gui]"

# Install Playwright browsers
echo ""
echo -e "${YELLOW}🌐 Installing Chromium browser for Playwright...${NC}"
playwright install chromium

echo ""
echo -e "${GREEN}✅ Installation complete!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📖 Quick Start Guide:"
echo ""
echo "  🌐 GUI Mode (Full Version):"
echo "    web-all-gui"
echo "    Then open http://localhost:8000"
echo ""
echo "  💻 CLI Mode:"
echo "    web-all-cli"
echo "    Or use: web-all clone https://example.com"
echo ""
echo "  🔧 All Commands:"
echo "    web-all --help"
echo ""
echo "  📦 Virtual Environment Location:"
echo "    $VENV_DIR"
echo ""
echo "  🔄 To activate manually:"
echo "    source $VENV_DIR/bin/activate"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}🎉 Happy cloning with web-all v4.5.0!${NC}"
