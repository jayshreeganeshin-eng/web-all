#!/usr/bin/env python3
"""
weball_noob - Easy-to-use interface for weball
Perfect for beginners! One file to rule them all.

Usage:
    python weball_noob.py                    # Start web server with GUI
    python weball_noob.py clone <url>        # Clone a website
    python weball_noob.py serve              # Start web server
    python weball_noob.py --help             # Show help
"""

import sys
import argparse
import asyncio
from pathlib import Path

# Add the weball package to path
sys.path.insert(0, str(Path(__file__).parent))

print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🌐  weball v4.0 - AI-Powered Website Cloner            ║
║       Production Ready | Free AI | Auto-Detection         ║
║                                                           ║
║   Features:                                               ║
║   ✅ Frontend - Modern Web Interface                      ║
║   ✅ Backend - Robust Cloning Engine                      ║
║   ✅ Admin Panel - User & Job Management                  ║
║   ✅ Users - Authentication System                        ║
║   ✅ AI Services - Free AI Integration                    ║
║   ✅ Tor Support - .onion sites                           ║
║   ✅ Auto-Update - Production Ready                       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""")


def cmd_clone(args):
    """Clone a website from command line."""
    print(f"\n🚀 Starting clone of {args.url}")
    
    try:
        from weball.core.cloner import SiteCloner
        
        cloner = SiteCloner(
            output_dir=args.output or "./output/clone",
            depth=args.depth,
            use_tor=args.tor
        )
        
        mode = "dynamic" if args.dynamic else "static"
        manifest = asyncio.run(cloner.clone_site(args.url, mode=mode))
        
        print(f"\n✅ Clone complete!")
        print(f"   Pages visited: {manifest.get('visited_count', 0)}")
        print(f"   Assets downloaded: {manifest.get('assets_count', 0)}")
        print(f"   Output directory: {manifest.get('output_directory', './output')}")
        
        if manifest.get('stats'):
            print(f"\n📊 Statistics:")
            print(f"   Images: {manifest['stats'].get('images', 0)}")
            print(f"   CSS files: {manifest['stats'].get('css', 0)}")
            print(f"   JavaScript files: {manifest['stats'].get('js', 0)}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


def cmd_serve(args):
    """Start the web server with frontend, backend, and admin panel."""
    print("\n🌐 Starting weball Server...")
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    print(f"   URL: http://{args.host}:{args.port}")
    print("\n✨ Features enabled:")
    print("   ✅ Frontend - Modern Web Interface")
    print("   ✅ Backend API - RESTful endpoints")
    print("   ✅ Admin Panel - User & job management")
    print("   ✅ AI Services - Free AI integration (Ollama)")
    print("   ✅ User Authentication")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        from weball.api.server import start_api
        
        # Get frontend directory
        frontend_dir = Path(__file__).parent / "frontend"
        
        start_api(
            host=args.host,
            port=args.port,
            gui_dir=str(frontend_dir)
        )
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


def cmd_quickstart(args):
    """Quick start guide for beginners."""
    print("""
╔═══════════════════════════════════════════════════════════╗
║           🎯 weball Quick Start Guide                     ║
╚═══════════════════════════════════════════════════════════╝

📌 STEP 1: Install Dependencies
   pip install -e .

📌 STEP 2: Start the Web Server
   python weball_noob.py serve
   
   Or use custom host/port:
   python weball_noob.py serve --host 0.0.0.0 --port 8080

📌 STEP 3: Open Your Browser
   Navigate to: http://localhost:8000

📌 STEP 4: Use the Interface
   - Clone Website: Enter URL and click "Start Cloning"
   - View Jobs: Check status of your cloning jobs
   - Admin Panel: Manage users and settings
   - Login: Access your account

📌 COMMAND LINE USAGE:
   Clone a website:
   python weball_noob.py clone https://example.com
   
   Clone with options:
   python weball_noob.py clone https://example.com --depth 3 --dynamic
   
   Clone .onion site (requires Tor):
   python weball_noob.py clone http://example.onion --tor

📌 AI FEATURES (Auto-enabled, Free!):
   - Automatic content summarization
   - Smart tagging and categorization
   - Data extraction
   - Content cleaning
   
   Default: Ollama (local, completely free)
   Alternatives: Groq, OpenRouter (free tiers available)

📌 DEFAULT CREDENTIALS:
   Username: admin
   Password: admin123
   (Change these in production!)

📌 OUTPUT LOCATION:
   Cloned websites are saved to: ./output/

🎉 That's it! You're ready to use weball!
""")
    return 0


def cmd_status(args):
    """Show system status."""
    print("\n📊 weball System Status\n")
    
    # Check dependencies
    print("📦 Dependencies:")
    deps = {
        "requests": False,
        "beautifulsoup4": False,
        "playwright": False,
        "fastapi": False,
        "uvicorn": False,
        "aiohttp": False
    }
    
    for pkg in deps.keys():
        try:
            __import__(pkg.replace("beautifulsoup4", "bs4"))
            deps[pkg] = True
            print(f"   ✅ {pkg}")
        except ImportError:
            print(f"   ❌ {pkg} - Not installed")
    
    # Check directories
    print("\n📁 Directories:")
    dirs = ["./output", "./data", "./frontend"]
    for d in dirs:
        path = Path(d)
        if path.exists():
            print(f"   ✅ {d}")
        else:
            path.mkdir(parents=True, exist_ok=True)
            print(f"   ➕ Created {d}")
    
    # Check AI availability
    print("\n🤖 AI Services:")
    try:
        import aiohttp
        print("   ✅ HTTP client ready")
        
        # Try to check Ollama
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 11434))
            if result == 0:
                print("   ✅ Ollama detected (local AI)")
            else:
                print("   ⚠️  Ollama not running (will use cloud alternatives)")
            sock.close()
        except:
            print("   ⚠️  Could not check Ollama status")
    except:
        print("   ⚠️  AI services unavailable")
    
    print("\n✨ System Ready!")
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="weball_noob",
        description="🌐 weball - AI-Powered Universal Website Cloner (Easy Mode)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python weball_noob.py serve                    # Start web server
  python weball_noob.py clone https://example.com  # Clone a site
  python weball_noob.py quickstart               # Show quick start guide
  python weball_noob.py status                   # Check system status
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Clone command
    p_clone = subparsers.add_parser("clone", help="Clone a website")
    p_clone.add_argument("url", help="Target URL (https://... or .onion)")
    p_clone.add_argument("-o", "--output", default="./output/clone", help="Output directory")
    p_clone.add_argument("-d", "--depth", type=int, default=2, help="Crawl depth (0-10)")
    p_clone.add_argument("--tor", action="store_true", help="Use Tor proxy for .onion sites")
    p_clone.add_argument("--dynamic", action="store_true", help="Use headless browser for JS sites")
    p_clone.set_defaults(func=cmd_clone)
    
    # Serve command
    p_serve = subparsers.add_parser("serve", help="Start web server with GUI")
    p_serve.add_argument("--host", default="localhost", help="Host to bind")
    p_serve.add_argument("-p", "--port", type=int, default=8000, help="Port number")
    p_serve.set_defaults(func=cmd_serve)
    
    # Quickstart command
    p_quickstart = subparsers.add_parser("quickstart", help="Show quick start guide")
    p_quickstart.set_defaults(func=cmd_quickstart)
    
    # Status command
    p_status = subparsers.add_parser("status", help="Show system status")
    p_status.set_defaults(func=cmd_status)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        print("\n💡 Tip: Run 'python weball_noob.py quickstart' for a quick start guide!")
        return 1
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
