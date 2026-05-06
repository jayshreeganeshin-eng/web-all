#!/bin/bash
# web-all v3.0 Universal Installer
# Works on Linux, macOS, and Windows (Git Bash/WSL)

set -e

echo "🌐 web-all v3.0 - Universal Website Cloner & Crawler"
echo "====================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking requirements..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python not found! Please install Python 3.10+${NC}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Python $PYTHON_VERSION detected"

# Check if pip is available
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo -e "${RED}❌ pip not found! Please install pip${NC}"
    exit 1
fi
echo "✅ pip detected"

# Create virtual environment (optional but recommended)
echo ""
read -p "Create a virtual environment? (recommended) [Y/n]: " create_venv
create_venv=${create_venv:-Y}

if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "📦 Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo "✅ Virtual environment activated (Linux/macOS)"
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
        echo "✅ Virtual environment activated (Windows)"
    fi
fi

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
$PYTHON_CMD -m pip install --upgrade pip

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
$PYTHON_CMD -m pip install \
    requests>=2.31.0 \
    beautifulsoup4>=4.12.0 \
    lxml>=4.9.0 \
    playwright>=1.40.0 \
    fastapi>=0.104.0 \
    uvicorn>=0.24.0 \
    python-multipart>=0.0.6 \
    aiohttp>=3.9.0

# Install Playwright browsers
echo ""
echo "🌐 Installing Playwright browsers (this may take a few minutes)..."
$PYTHON_CMD -m playwright install chromium

# Install the package in development mode
echo ""
echo "🔧 Installing web-all package..."
$PYTHON_CMD -m pip install -e .

# Create output directory
echo ""
echo "📁 Creating output directory..."
mkdir -p output
chmod 755 output

# Verify installation
echo ""
echo "🧪 Verifying installation..."
if $PYTHON_CMD -c "import web_all; print('✅ web-all imported successfully')" 2>/dev/null; then
    echo -e "${GREEN}✅ Installation successful!${NC}"
else
    echo -e "${RED}❌ Installation failed. Please check the error messages above.${NC}"
    exit 1
fi

# Display usage instructions
echo ""
echo "====================================================="
echo "✨ web-all has been successfully installed!"
echo "====================================================="
echo ""
echo "Quick Start Guide:"
echo "------------------"
echo "1. Clone a website:"
echo "   web-all clone https://example.com -o ./mysite"
echo ""
echo "2. Start the web GUI:"
echo "   web-all serve"
echo "   Then open: http://localhost:8000"
echo ""
echo "3. For .onion sites (requires Tor):"
echo "   web-all clone http://example.onion --tor"
echo ""
echo "Commands:"
echo "---------"
echo "  web-all clone <url>     - Clone a complete website"
echo "  web-all images <url>    - Download all images"
echo "  web-all text <url>      - Extract text content"
echo "  web-all discover <url>  - Discover hidden content"
echo "  web-all serve           - Start web GUI & API"
echo ""
echo "For more help: web-all --help"
echo ""
echo -e "${YELLOW}Note: If you created a virtual environment, remember to activate it:${NC}"
echo "  source venv/bin/activate  (Linux/macOS)"
echo "  venv\\Scripts\\activate    (Windows)"
echo ""
echo "Happy cloning! 🚀"
