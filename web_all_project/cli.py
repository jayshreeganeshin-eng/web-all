#!/usr/bin/env python3
"""
web-all Command Line Interface
Universal website cloner with Tor support, invisible content discovery, and more.
"""

import sys
import argparse
import asyncio
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from web_all.core.cloner import SiteCloner
from web_all.core.invisible import InvisibleContentEngine
from web_all.api.server import start_api


def cmd_clone(args):
    """Clone a website."""
    print(f"🚀 Starting clone of {args.url}")

    cloner = SiteCloner(
        output_dir=args.output,
        depth=args.depth,
        concurrency=args.concurrency,
        delay=args.delay,
        use_tor=args.tor,
        tor_proxy=args.tor_proxy if args.tor else "http://127.0.0.1:9050"
    )

    mode = "dynamic" if args.dynamic else "static"

    try:
        manifest = asyncio.run(cloner.clone_site(args.url, mode=mode))
        print(f"\n✅ Clone complete!")
        print(f"   Pages visited: {manifest.get('visited_count', 0)}")
        print(f"   Assets downloaded: {manifest.get('assets_count', 0)}")
        print(f"   Output directory: {args.output}")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


def cmd_images(args):
    """Download images only."""
    print(f"📸 Downloading images from {args.url}")

    cloner = SiteCloner(
        output_dir=args.output,
        depth=args.depth,
        use_tor=args.tor
    )

    async def run():
        html = await cloner.fetch_page_dynamic(args.url) if args.dynamic else await cloner.fetch_page(args.url)
        if html:
            assets = cloner.extract_assets(html, args.url)
            for img_url in assets['images']:
                cloner.save_asset(img_url, 'images')
            print(f"\n✅ Downloaded {len(cloner.downloaded_assets)} images")
            return 0
        else:
            print("❌ Failed to fetch page")
            return 1

    try:
        return asyncio.run(run())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


def cmd_text(args):
    """Extract text from pages."""
    from bs4 import BeautifulSoup

    print(f"📝 Extracting text from {args.url}")

    cloner = SiteCloner(
        output_dir=args.output,
        use_tor=args.tor
    )

    async def run():
        html = await cloner.fetch_page_dynamic(args.url) if args.dynamic else await cloner.fetch_page(args.url)
        if not html:
            print("❌ Failed to fetch page")
            return 1

        soup = BeautifulSoup(html, 'lxml')

        # Remove scripts and styles
        for tag in soup(['script', 'style']):
            tag.decompose()

        text = soup.get_text(separator='\n', strip=True)

        output_file = Path(args.output) / "extracted.txt"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"\n✅ Text extracted to {output_file}")
        return 0

    try:
        return asyncio.run(run())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


def cmd_discover(args):
    """Discover invisible content."""
    print(f"🔍 Discovering invisible content on {args.url}")

    engine = InvisibleContentEngine(use_tor=args.tor)

    async def run():
        try:
            html = await engine.expand_all_content(
                args.url,
                scroll_iterations=args.scrolls,
                click_selectors=None,
                hover_selectors=None
            )

            output_file = Path(args.output) / "expanded.html"
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)

            print(f"\n✅ Expanded content saved to {output_file}")

            # Also try sitemap
            from urllib.parse import urlparse
            parsed = urlparse(args.url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"

            sitemap_urls = await engine.discover_sitemap_urls(base_url)
            if sitemap_urls:
                print(f"📍 Found {len(sitemap_urls)} URLs in sitemap")
                sitemap_file = Path(args.output) / "sitemap_urls.txt"
                with open(sitemap_file, 'w') as f:
                    for url in sitemap_urls:
                        f.write(url + '\n')
                print(f"   Saved to {sitemap_file}")

            return 0

        except Exception as e:
            print(f"\n❌ Error: {e}")
            return 1

    try:
        return asyncio.run(run())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


def cmd_serve(args):
    """Start the web API and GUI server."""
    gui_path = Path(__file__).parent / "web_all" / "gui"

    print(f"🌐 Starting web-all server...")
    print(f"   API: http://{args.host}:{args.port}/api/v1")
    print(f"   GUI: http://{args.host}:{args.port}")
    print(f"\nPress Ctrl+C to stop")

    try:
        start_api(host=args.host, port=args.port, gui_dir=str(gui_path))
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        prog="web-all",
        description="Universal Website Cloner & Crawler with Tor Support"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Clone command
    p_clone = subparsers.add_parser("clone", help="Clone a complete website")
    p_clone.add_argument("url", help="Target URL")
    p_clone.add_argument("-o", "--output", default="./output/clone", help="Output directory")
    p_clone.add_argument("-d", "--depth", type=int, default=2, help="Crawl depth")
    p_clone.add_argument("-c", "--concurrency", type=int, default=3, help="Concurrent requests")
    p_clone.add_argument("--delay", type=float, default=1.0, help="Delay between requests")
    p_clone.add_argument("--tor", action="store_true", help="Use Tor proxy")
    p_clone.add_argument("--tor-proxy", default="http://127.0.0.1:9050", help="Tor proxy address")
    p_clone.add_argument("--dynamic", action="store_true", help="Use headless browser for JS sites")
    p_clone.set_defaults(func=cmd_clone)

    # Images command
    p_images = subparsers.add_parser("images", help="Download all images")
    p_images.add_argument("url", help="Target URL")
    p_images.add_argument("-o", "--output", default="./output/images", help="Output directory")
    p_images.add_argument("-d", "--depth", type=int, default=0, help="Crawl depth")
    p_images.add_argument("--tor", action="store_true", help="Use Tor proxy")
    p_images.add_argument("--dynamic", action="store_true", help="Use headless browser")
    p_images.set_defaults(func=cmd_images)

    # Text command
    p_text = subparsers.add_parser("text", help="Extract text from pages")
    p_text.add_argument("url", help="Target URL")
    p_text.add_argument("-o", "--output", default="./output/text", help="Output directory")
    p_text.add_argument("--tor", action="store_true", help="Use Tor proxy")
    p_text.add_argument("--dynamic", action="store_true", help="Use headless browser")
    p_text.set_defaults(func=cmd_text)

    # Discover command
    p_discover = subparsers.add_parser("discover", help="Discover invisible content")
    p_discover.add_argument("url", help="Target URL")
    p_discover.add_argument("-o", "--output", default="./output/discovered", help="Output directory")
    p_discover.add_argument("--tor", action="store_true", help="Use Tor proxy")
    p_discover.add_argument("--scrolls", type=int, default=5, help="Number of scroll iterations")
    p_discover.set_defaults(func=cmd_discover)

    # Serve command
    p_serve = subparsers.add_parser("serve", help="Start web API and GUI server")
    p_serve.add_argument("--host", default="0.0.0.0", help="Host to bind")
    p_serve.add_argument("-p", "--port", type=int, default=8000, help="Port to bind")
    p_serve.set_defaults(func=cmd_serve)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())