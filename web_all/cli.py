#!/usr/bin/env python3
"""CLI entry point for web-all."""

import argparse
import asyncio
import sys
from pathlib import Path


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="web-all",
        description="Universal Website Cloner - Download visible and invisible content"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Clone command
    clone_p = subparsers.add_parser("clone", help="Full website clone with assets")
    clone_p.add_argument("url", help="Target website URL")
    clone_p.add_argument("-o", "--output", default="./output", help="Output directory")
    clone_p.add_argument("-d", "--depth", type=int, default=2, help="Crawl depth")
    clone_p.add_argument("-c", "--concurrency", type=int, default=5, help="Concurrent requests")
    clone_p.add_argument("--delay", type=float, default=0.5, help="Delay between requests")
    clone_p.add_argument("--tor", action="store_true", help="Use Tor proxy")
    clone_p.add_argument("--dynamic", action="store_true", help="Use dynamic rendering")
    clone_p.add_argument("--discover-invisible", action="store_true", help="Discover hidden content")

    # Images command
    img_p = subparsers.add_parser("images", help="Download all images")
    img_p.add_argument("url", help="Target website URL")
    img_p.add_argument("-o", "--output", default="./output/images", help="Output directory")
    img_p.add_argument("-d", "--depth", type=int, default=1, help="Crawl depth")

    # Text command
    txt_p = subparsers.add_parser("text", help="Extract text from pages")
    txt_p.add_argument("url", help="Target website URL")
    txt_p.add_argument("-o", "--output", default="./output/text", help="Output directory")
    txt_p.add_argument("-d", "--depth", type=int, default=2, help="Crawl depth")

    # Serve command (GUI + API)
    serve_p = subparsers.add_parser("serve", help="Start web GUI server")
    serve_p.add_argument("-p", "--port", type=int, default=8000, help="Server port")
    serve_p.add_argument("--host", default="0.0.0.0", help="Server host")
    serve_p.add_argument("--no-gui", action="store_true", help="API only, no GUI")

    args = parser.parse_args()

    if args.command == "clone":
        _handle_clone(args)
    elif args.command == "images":
        _handle_images(args)
    elif args.command == "text":
        _handle_text(args)
    elif args.command == "serve":
        _handle_serve(args)
    else:
        parser.print_help()
        sys.exit(0)


def _handle_clone(args):
    """Handle clone command."""
    from .core.cloner import SiteCloner
    from .core.invisible import InvisibleContentEngine

    print(f"🚀 Cloning {args.url}...")

    cloner = SiteCloner(
        output_dir=args.output,
        depth=args.depth,
        concurrency=args.concurrency,
        delay=args.delay,
        use_tor=args.tor
    )

    async def run():
        if args.discover_invisible:
            print("🔍 Discovering invisible content...")
            engine = InvisibleContentEngine(use_tor=args.tor)
            expanded = await engine.expand_all_content(args.url)
            output_path = Path(args.output) / "expanded.html"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(expanded, encoding="utf-8")
            print(f"✓ Saved expanded content to {output_path}")

        mode = "dynamic" if args.dynamic else "static"
        await cloner.clone_site(args.url, mode=mode)

    asyncio.run(run())
    print(f"✅ Clone complete! Output: {args.output}")


def _handle_images(args):
    """Handle images command."""
    from .core.cloner import SiteCloner
    from bs4 import BeautifulSoup
    import aiohttp

    print(f"📸 Downloading images from {args.url}...")

    async def run():
        cloner = SiteCloner(output_dir=args.output, depth=args.depth)
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        html = await cloner.fetch_page(args.url)
        if not html:
            print("❌ Failed to fetch page")
            return

        soup = BeautifulSoup(html, "lxml")
        imgs = soup.find_all("img", src=True)
        print(f"Found {len(imgs)} images")

        async with aiohttp.ClientSession() as session:
            for i, img in enumerate(imgs[:50]):
                src = img.get("src", "")
                if src.startswith(("http://", "https://")):
                    try:
                        async with session.get(src) as resp:
                            if resp.status == 200:
                                name = src.split("/")[-1].split("?")[0] or f"image_{i}.jpg"
                                path = output_dir / name
                                path.write_bytes(await resp.read())
                                print(f"  ✓ {name}")
                    except Exception as e:
                        print(f"  ✗ {src}: {e}")

    asyncio.run(run())
    print(f"✅ Images saved to {args.output}")


def _handle_text(args):
    """Handle text command."""
    from .core.cloner import SiteCloner
    from bs4 import BeautifulSoup
    from urllib.parse import urlparse

    print(f"📝 Extracting text from {args.url}...")

    async def run():
        cloner = SiteCloner(output_dir=args.output, depth=args.depth)
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        html = await cloner.fetch_page(args.url)
        if not html:
            print("❌ Failed to fetch page")
            return

        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)

        parsed = urlparse(args.url)
        out_file = output_dir / f"{parsed.netloc.replace('.', '_')}.txt"
        out_file.write_text(text, encoding="utf-8")

        print(f"✓ Extracted {len(text)} characters")

    asyncio.run(run())
    print(f"✅ Text saved to {args.output}")


def _handle_serve(args):
    """Handle serve command."""
    from .api.server import start_api
    from pathlib import Path

    gui_dir = None if args.no_gui else str(Path(__file__).parent / "gui")
    print(f"🌐 Starting web-all server on http://{args.host}:{args.port}")
    if gui_dir:
        print(f"   Serving GUI from {gui_dir}")

    start_api(host=args.host, port=args.port, gui_dir=gui_dir)


if __name__ == "__main__":
    main()
