#!/bin/bash

# Web Cloner Pro - One Command Installer
# This script installs all dependencies and sets up the Web Cloner Pro

set -e

echo "🚀 Web Cloner Pro - Installation Script"
echo "======================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect OS
OS="$(uname -s)"
echo "📋 Detected OS: $OS"

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check for Node.js
check_nodejs() {
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node -v)
        print_status "Node.js found: $NODE_VERSION"
        
        # Check version (need >= 18.0.0)
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1 | sed 's/v//')
        if [ "$NODE_MAJOR" -lt 18 ]; then
            print_warning "Node.js version should be >= 18.0.0"
            return 1
        fi
        return 0
    else
        print_error "Node.js not found"
        return 1
    fi
}

# Check for npm
check_npm() {
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm -v)
        print_status "npm found: $NPM_VERSION"
        return 0
    else
        print_error "npm not found"
        return 1
    fi
}

# Install Node.js if needed
install_nodejs() {
    echo ""
    print_warning "Installing Node.js..."
    
    case "$OS" in
        Linux*)
            if command -v apt-get &> /dev/null; then
                curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
                sudo apt-get install -y nodejs
            elif command -v yum &> /dev/null; then
                curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
                sudo yum install -y nodejs
            elif command -v pacman &> /dev/null; then
                sudo pacman -S nodejs npm
            else
                print_error "Unsupported Linux package manager"
                exit 1
            fi
            ;;
        Darwin*)
            if command -v brew &> /dev/null; then
                brew install node
            else
                print_error "Homebrew not found. Please install Node.js manually."
                exit 1
            fi
            ;;
        *)
            print_error "Unsupported OS. Please install Node.js manually from https://nodejs.org"
            exit 1
            ;;
    esac
    
    print_status "Node.js installed successfully"
}

# Check for Chrome/Chromium
check_chrome() {
    if command -v google-chrome &> /dev/null || command -v chromium &> /dev/null || command -v "Google Chrome" &> /dev/null; then
        print_status "Chrome/Chromium found"
        return 0
    else
        print_warning "Chrome/Chromium not found (will be installed by Puppeteer)"
        return 1
    fi
}

# Check for Git
check_git() {
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version)
        print_status "Git found: $GIT_VERSION"
        return 0
    else
        print_error "Git not found"
        return 1
    fi
}

# Install dependencies
install_dependencies() {
    echo ""
    echo "📦 Installing Node.js dependencies..."
    npm install
    print_status "Dependencies installed"
}

# Create directories
setup_directories() {
    echo ""
    echo "📁 Setting up directories..."
    mkdir -p output logs config
    print_status "Directories created"
}

# Create example config
create_example_config() {
    echo ""
    echo "⚙️  Creating example configuration..."
    
    if [ ! -f "config/custom.yaml" ]; then
        cat > config/custom.yaml << 'EOF'
# Custom Configuration - Copy and modify as needed
target:
  depth: 5
  maxPages: 500

stealth:
  enabled: false

aiAutofix:
  enabled: false

output:
  directory: "./output"
EOF
        print_status "Example config created at config/custom.yaml"
    else
        print_warning "Custom config already exists"
    fi
}

# Show usage instructions
show_instructions() {
    echo ""
    echo "=========================================="
    echo "🎉 Installation Complete!"
    echo "=========================================="
    echo ""
    echo "Usage:"
    echo ""
    echo "  🌐 Start Web Server (with Dashboard):"
    echo "     npm start"
    echo ""
    echo "  🖥️  Clone via CLI:"
    echo "     npm start -- https://example.com"
    echo ""
    echo "  ⚡ With options:"
    echo "     npm start -- https://example.com --stealth --ai-fix"
    echo ""
    echo "  🔧 Use custom config:"
    echo "     npm start --config=config/custom.yaml"
    echo ""
    echo "API Endpoints (when server is running):"
    echo "  - Dashboard: http://localhost:3000"
    echo "  - API: http://localhost:3000/api/clone"
    echo "  - Health: http://localhost:3000/health"
    echo ""
    echo "Environment Variables:"
    echo "  - TARGET_URL: Set target URL"
    echo "  - STEALTH_ENABLED: Enable stealth mode (true/false)"
    echo "  - AI_AUTOFIX_ENABLED: Enable AI auto-fix (true/false)"
    echo "  - API_PORT: Change API port (default: 3000)"
    echo "  - API_AUTH_KEY: Set API authentication key"
    echo ""
    echo "⚠️  Legal Notice:"
    echo "   Only clone websites you own or have explicit"
    echo "   written permission to archive."
    echo ""
}

# Docker installation option
install_docker() {
    echo ""
    print_warning "Docker installation requested..."
    
    if command -v docker &> /dev/null; then
        print_status "Docker found"
        echo ""
        echo "To run with Docker:"
        echo "  docker build -t web-cloner-pro ."
        echo "  docker run -p 3000:3000 -v $(pwd)/output:/app/output web-cloner-pro"
    else
        print_error "Docker not found. Please install Docker first."
    fi
}

# Main installation
main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --docker)
                DOCKER_INSTALL=true
                shift
                ;;
            --force)
                FORCE_INSTALL=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
    
    # Check prerequisites
    echo ""
    echo "🔍 Checking prerequisites..."
    
    NEEDS_NODEJS=false
    
    if ! check_git; then
        print_error "Git is required. Please install Git first."
        exit 1
    fi
    
    if ! check_nodejs; then
        NEEDS_NODEJS=true
    fi
    
    if ! check_npm && [ "$NEEDS_NODEJS" = false ]; then
        NEEDS_NODEJS=true
    fi
    
    if [ "$NEEDS_NODEJS" = true ]; then
        install_nodejs
    fi
    
    check_chrome
    
    # Install dependencies
    install_dependencies
    
    # Setup directories
    setup_directories
    
    # Create example config
    create_example_config
    
    # Docker option
    if [ "$DOCKER_INSTALL" = true ]; then
        install_docker
    fi
    
    # Show instructions
    show_instructions
}

# Run main function
main "$@"
