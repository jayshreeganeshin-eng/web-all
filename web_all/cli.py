#!/usr/bin/env python3
"""CLI entry point for web-all."""

import argparse
import asyncio
import sys
from pathlib import Path
from urllib.parse import urlparse

__version__ = "4.5.0"


def _validate_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("Invalid URL. Use a valid http:// or https:// address.")
    return url


def run_gui():
    """Entry point for GUI mode."""
    from .api.server import start_api
    gui_dir = str(Path(__file__).parent / "gui")
    print(f"🌐 Starting web-all GUI v{__version__}...")
    start_api(host="0.0.0.0", port=8000, gui_dir=gui_dir)


def run_cli():
    """Entry point for CLI mode (interactive)."""
    print(f"🚀 web-all CLI v{__version__} - Interactive Mode")
    print("=" * 50)
    main()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="web-all",
        description=f"Universal Website Cloner v{__version__} - Download visible and invisible content",
    )

    # Add version argument
    parser.add_argument(
        "--version",
        action="version",
        version=f"web-all v{__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Clone command
    clone_p = subparsers.add_parser("clone", help="Full website clone with assets")
    clone_p.add_argument("url", help="Target website URL")
    clone_p.add_argument("-o", "--output", default="./output", help="Output directory")
    clone_p.add_argument(
        "-d", "--depth", type=int, default=0, help="Crawl depth (0 = all pages from domain)"
    )
    clone_p.add_argument("-c", "--concurrency", type=int, default=5, help="Concurrent requests")
    clone_p.add_argument("--delay", type=float, default=0.5, help="Delay between requests")
    clone_p.add_argument("--tor", action="store_true", help="Use Tor proxy")
    clone_p.add_argument("--dynamic", action="store_true", help="Use dynamic rendering")
    clone_p.add_argument(
        "--discover-invisible", action="store_true", help="Discover hidden content"
    )
    clone_p.add_argument(
        "--everything",
        action="store_true",
        help="Run full capture: dynamic rendering, hidden content discovery, and deep crawl",
    )
    clone_p.add_argument(
        "--ai-enabled", action="store_true", help="Enable AI analysis for this clone"
    )
    clone_p.add_argument(
        "--ai-provider",
        choices=["openrouter", "groq", "huggingface", "nvidia", "ollama"],
        default="ollama",
        help="AI provider to use",
    )
    clone_p.add_argument("--ai-key", help="API key for AI provider (not needed for ollama)")
    clone_p.add_argument("--ai-model", help="Specific model to use (optional)")
    clone_p.add_argument(
        "--max-pages", type=int, default=1000, help="Maximum number of pages to crawl"
    )

    # Images command
    img_p = subparsers.add_parser("images", help="Download all images")
    img_p.add_argument("url", help="Target website URL")
    img_p.add_argument("-o", "--output", default="./output/images", help="Output directory")
    img_p.add_argument(
        "-d", "--depth", type=int, default=0, help="Crawl depth (0 = all pages from domain)"
    )

    # Text command
    txt_p = subparsers.add_parser("text", help="Extract text from pages")
    txt_p.add_argument("url", help="Target website URL")
    txt_p.add_argument("-o", "--output", default="./output/text", help="Output directory")
    txt_p.add_argument(
        "-d", "--depth", type=int, default=0, help="Crawl depth (0 = all pages from domain)"
    )

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
    from .utils.ai_engine import AIEngine

    try:
        _validate_url(args.url)
    except ValueError as exc:
        print(f"❌ {exc}")
        sys.exit(1)

    if args.max_pages < 1:
        print("❌ --max-pages must be at least 1")
        sys.exit(1)

    print(f"🚀 Cloning {args.url}...")

    cloner = SiteCloner(
        output_dir=args.output,
        depth=args.depth,
        concurrency=args.concurrency,
        delay=args.delay,
        use_tor=args.tor,
        max_pages=args.max_pages,
    )

    async def run():
        if args.everything:
            print(
                "⚡ Running full capture: dynamic rendering, hidden content, "
                "deeper crawl, and AI analysis"
            )
            args.dynamic = True
            args.discover_invisible = True
            args.ai_enabled = True
            if args.depth < 4:
                args.depth = 4

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

        if args.ai_enabled:
            try:
                ai_config = {
                    "enabled": True,
                    "provider": args.ai_provider,
                    "base_url": "http://localhost:11434" if args.ai_provider == "ollama" else None,
                }

                # Add API key if provided or required
                if args.ai_key:
                    ai_config["api_key"] = args.ai_key
                elif args.ai_provider in ["openrouter", "groq", "huggingface", "nvidia"]:
                    # Try to get from environment
                    import os

                    env_key_map = {
                        "openrouter": "OPENROUTER_API_KEY",
                        "groq": "GROQ_API_KEY",
                        "huggingface": "HUGGINGFACE_API_KEY",
                        "nvidia": "NVIDIA_API_KEY",
                    }
                    env_key = os.environ.get(env_key_map.get(args.ai_provider, ""))
                    if env_key:
                        ai_config["api_key"] = env_key
                    else:
                        msg = (
                            f"⚠️ No API key for {args.ai_provider}. "
                            f"Set --ai-key or {env_key_map.get(args.ai_provider, '')} env var."
                        )
                        print(msg)

                if args.ai_model:
                    ai_config["model"] = args.ai_model

                ai_engine = AIEngine(ai_config)
                parsed = urlparse(args.url)
                index_html = Path(args.output) / parsed.netloc.replace(".", "_") / "index.html"
                if index_html.exists():
                    html = index_html.read_text(encoding="utf-8")
                    await ai_engine.analyze_and_enhance(html, args.url, index_html.parent)
                    print(f"✅ AI analysis complete with {args.ai_provider}!")
                else:
                    print("⚠️ index.html not found in clone output; skipping AI analysis.")
            except Exception as e:
                print(f"⚠️ AI analysis failed: {e}")

    asyncio.run(run())
    print(f"✅ Clone complete! Output: {args.output}")


def _handle_images(args):
    """Handle images command."""
    import aiohttp
    from bs4 import BeautifulSoup

    from .core.cloner import SiteCloner

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
    from bs4 import BeautifulSoup

    from .core.cloner import SiteCloner

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

    gui_dir = None if args.no_gui else str(Path(__file__).parent / "gui")
    print(f"🌐 Starting web-all server v{__version__} on http://{args.host}:{args.port}")
    if gui_dir:
        print(f"   Serving GUI from {gui_dir}")

    start_api(host=args.host, port=args.port, gui_dir=gui_dir)


if __name__ == "__main__":
    main()
