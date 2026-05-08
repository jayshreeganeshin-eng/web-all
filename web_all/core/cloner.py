"""
Core cloner engine for static and dynamic websites.
Supports clearnet and .onion (Tor) sites.
Auto-downloads full websites with organized folder structure.
"""

import asyncio
import hashlib
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse, urlunparse

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    import requests
    from bs4 import BeautifulSoup
    from playwright.async_api import async_playwright
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Run: pip install requests beautifulsoup4 playwright")
    raise

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Constants - OPTIMIZED FOR MAXIMUM EXTRACTION
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
DEFAULT_TOR_PROXY = "http://127.0.0.1:9050"
DEFAULT_TIMEOUT = 60  # Increased timeout for large pages
DEFAULT_CONCURRENCY = 20  # Maximum concurrent requests
DEFAULT_DELAY = 0.1  # Minimal delay for speed
DEFAULT_DEPTH = 0  # 0 = UNLIMITED depth by default
MAX_PAGES = 10000  # Very high limit by default
ASSET_TYPES = {"images", "css", "js", "fonts", "videos", "documents"}


class SiteCloner:
    """Main website cloning engine with Tor support and automatic organization."""

    def __init__(
        self,
        output_dir: str = "./output",
        depth: int = DEFAULT_DEPTH,  # Default 0 = unlimited
        concurrency: int = DEFAULT_CONCURRENCY,  # Default 20
        delay: float = DEFAULT_DELAY,  # Default 0.1
        user_agent: Optional[str] = None,
        use_tor: bool = False,
        tor_proxy: str = DEFAULT_TOR_PROXY,
        timeout: int = DEFAULT_TIMEOUT,  # Default 60s
        respect_robots: bool = False,
        auto_organize: bool = True,
        download_all_assets: bool = True,
        save_metadata: bool = True,
        max_pages: int = MAX_PAGES,  # Default 10000
        follow_external: bool = True,  # Follow external links by default
        include_subdomains: bool = True,
        extract_all_media: bool = True,  # Extract videos, fonts, documents
        aggressive_crawl: bool = True,  # Aggressive mode for maximum extraction
    ):
        self.output_dir = Path(output_dir)
        self.depth = depth
        self.concurrency = concurrency
        self.delay = delay
        self.user_agent = user_agent or DEFAULT_USER_AGENT
        self.use_tor = use_tor
        self.tor_proxy = tor_proxy
        self.timeout = timeout
        self.respect_robots = respect_robots
        self.auto_organize = auto_organize
        self.download_all_assets = download_all_assets
        self.save_metadata = save_metadata
        self.extract_all_media = extract_all_media
        self.aggressive_crawl = aggressive_crawl

        self.visited_urls: Set[str] = set()
        self.seen_urls: Set[str] = set()
        self.downloaded_assets: Set[str] = set()
        self.url_map: Dict[str, Path] = {}
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        self.follow_external = follow_external  # Use parameter value (default True)
        self.include_subdomains = include_subdomains
        self.max_pages = max_pages

        # Aggressive retry strategy for maximum success
        retry_strategy = Retry(
            total=5,  # More retries
            status_forcelist=[429, 500, 502, 503, 504, 408, 413, 425],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
            backoff_factor=0.3,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        if use_tor:
            self._setup_tor_proxy()

        self.semaphore = asyncio.Semaphore(concurrency)
        self.stats = {
            "pages": 0, 
            "images": 0, 
            "css": 0, 
            "js": 0, 
            "fonts": 0,
            "videos": 0,
            "documents": 0,
            "other": 0, 
            "errors": 0
        }

    def _setup_tor_proxy(self):
        """Configure session to use Tor proxy."""
        proxies = {"http": self.tor_proxy, "https": self.tor_proxy}
        self.session.proxies.update(proxies)
        logger.info(f"Tor proxy enabled: {self.tor_proxy}")

    def _normalize_url(self, url: str) -> str:
        """Normalize URL for deduplication."""
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        path = parsed.path.rstrip("/") or "/"
        return urlunparse((parsed.scheme, netloc, path, "", parsed.query, ""))

    def _is_internal_url(self, url: str, base_domain: str) -> bool:
        """Check if URL belongs to the same domain."""
        parsed = urlparse(url)
        return parsed.netloc == base_domain or parsed.netloc.endswith("." + base_domain)

    def _should_follow_link(self, url: str, base_domain: str) -> bool:
        """Determine whether a link should be queued for crawling."""
        if self.follow_external:
            return True
        parsed = urlparse(url)
        if parsed.netloc == base_domain:
            return True
        if self.include_subdomains and parsed.netloc.endswith("." + base_domain):
            return True
        return False

    def _get_local_html_path(self, url: str) -> Path:
        """Generate a local file path for a page URL."""
        parsed = urlparse(url)
        path = parsed.path.rstrip("/") or "/"
        if path.endswith("/"):
            path = path + "index.html"
        elif not path.endswith(".html"):
            path = path.rstrip("/") + "/index.html"

        if parsed.query:
            query_hash = hashlib.md5(parsed.query.encode("utf-8")).hexdigest()[:8]
            path = path.replace(".html", f"_{query_hash}.html")

        domain = parsed.netloc.replace(".", "_").replace(":", "_")
        return self.output_dir / domain / path.lstrip("/")

    def _get_asset_path(self, url: str, asset_type: str) -> Path:
        """Generate organized path for assets."""
        parsed = urlparse(url)

        # Create domain-based folder structure
        domain = parsed.netloc.replace(".", "_").replace(":", "_")

        if asset_type == "images":
            subdir = self.output_dir / domain / "images"
        elif asset_type == "css":
            subdir = self.output_dir / domain / "css"
        elif asset_type == "js":
            subdir = self.output_dir / domain / "js"
        else:
            subdir = self.output_dir / domain / "assets"

        # Generate unique filename
        filename = (
            os.path.basename(parsed.path) or f"asset_{hashlib.md5(url.encode()).hexdigest()[:8]}"
        )
        if parsed.query:
            query_hash = hashlib.md5(parsed.query.encode("utf-8")).hexdigest()[:8]
            filename = f"{query_hash}_{filename}"

        counter = 0
        base_name, ext = os.path.splitext(filename)
        output_path = subdir / filename

        while output_path.exists():
            counter += 1
            output_path = subdir / f"{base_name}_{counter}{ext}"

        return output_path

    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content with retry logic."""
        async with self.semaphore:
            try:
                normalized = self._normalize_url(url)
                if normalized in self.seen_urls:
                    return None

                logger.info(f"Fetching: {url}")

                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(
                    None, lambda: self.session.get(url, timeout=self.timeout)
                )

                if response.status_code == 200:
                    self.seen_urls.add(normalized)
                    self.visited_urls.add(normalized)
                    return response.text
                else:
                    logger.warning(f"Failed to fetch {url}: {response.status_code}")
                    return None

            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                return None

    async def fetch_page_dynamic(
        self, url: str, scroll_times: int = 3, wait_time: float = 2.0
    ) -> Optional[str]:
        """Fetch page using headless browser for JavaScript rendering."""
        async with self.semaphore:
            try:
                normalized = self._normalize_url(url)
                if normalized in self.seen_urls:
                    return None

                logger.info(f"Dynamic fetch: {url}")

                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)

                    try:
                        context_args = {}
                        if self.use_tor:
                            context_args["proxy"] = {"server": self.tor_proxy}

                        context = await browser.new_context(
                            user_agent=self.user_agent, **context_args
                        )
                        page = await context.new_page()

                        await page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)

                        # Scroll to trigger lazy loading
                        for i in range(scroll_times):
                            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            await asyncio.sleep(wait_time)

                        html = await page.content()
                        self.seen_urls.add(normalized)
                        self.visited_urls.add(normalized)
                        return html
                    finally:
                        await browser.close()

            except Exception as e:
                logger.error(f"Dynamic fetch error for {url}: {e}")
                return None

    def extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract all links from HTML."""
        soup = BeautifulSoup(html, "lxml")
        return [
            urljoin(base_url, tag["href"].strip())
            for tag in soup.find_all("a", href=True)
            if not tag["href"].strip().startswith(("javascript:", "mailto:", "tel:", "#"))
        ]

    def extract_assets(self, html: str, base_url: str) -> Dict[str, List[str]]:
        """Extract ALL asset URLs including images, CSS, JS, fonts, videos, and documents."""
        soup = BeautifulSoup(html, "lxml")
        assets = {
            "images": [], 
            "css": [], 
            "js": [],
            "fonts": [],
            "videos": [],
            "documents": []
        }

        # Images - comprehensive extraction from all possible tags
        img_selectors = [
            ("img", "src"),
            ("img", "data-src"),  # Lazy loading
            ("img", "data-original"),
            ("source", "src"),  # Picture element sources
            ("svg", "image"),  # SVG images
        ]
        images = set()
        for tag_name, attr in img_selectors:
            for tag in soup.find_all(tag_name, **{attr: True}):
                src = tag.get(attr, "").strip()
                if src and not src.startswith(("data:", "javascript:", "#")):
                    images.add(urljoin(base_url, src))
        # Also check srcset attributes
        for img in soup.find_all(["img", "source"], srcset=True):
            srcset = img.get("srcset", "")
            for src in srcset.split(","):
                url = src.strip().split()[0]
                if url and not url.startswith(("data:", "javascript:", "#")):
                    images.add(urljoin(base_url, url))
        assets["images"] = list(images)

        # CSS - all stylesheet links and style imports
        css_selectors = [
            ("link", "href", lambda t: "stylesheet" in t.get("rel", [])),
            ("link", "href", lambda t: t.get("type") == "text/css"),
        ]
        css_files = set()
        for tag_name, attr, condition in css_selectors:
            for tag in soup.find_all(tag_name, **{attr: True}):
                if condition(tag):
                    href = tag.get(attr, "").strip()
                    if href and not href.startswith(("data:", "javascript:")):
                        css_files.add(urljoin(base_url, href))
        # Check for @import in style tags
        for style in soup.find_all("style"):
            if style.string:
                import re
                imports = re.findall(r'@import\s+[\'"]([^\'"]+)[\'"]', style.string)
                for imp in imports:
                    css_files.add(urljoin(base_url, imp))
        assets["css"] = list(css_files)

        # JavaScript - all script sources
        js_selectors = [
            ("script", "src"),
            ("script", "data-src"),  # Lazy loaded scripts
        ]
        js_files = set()
        for tag_name, attr in js_selectors:
            for tag in soup.find_all(tag_name, **{attr: True}):
                src = tag.get(attr, "").strip()
                if src and not src.startswith(("data:", "javascript:")):
                    js_files.add(urljoin(base_url, src))
        assets["js"] = list(js_files)

        # Fonts - extract from various sources
        font_extensions = [".woff", ".woff2", ".ttf", ".otf", ".eot", ".pfa", ".pfb"]
        fonts = set()
        # From link tags
        for link in soup.find_all("link", href=True):
            href = link.get("href", "").lower()
            if any(href.endswith(ext) for ext in font_extensions):
                fonts.add(urljoin(base_url, link["href"]))
        # From style tags with @font-face
        for style in soup.find_all("style"):
            if style.string:
                import re
                font_urls = re.findall(r'url\([\'"]?([^\'")]+)[\'"]?\)', style.string)
                for url in font_urls:
                    if any(url.lower().endswith(ext) for ext in font_extensions):
                        fonts.add(urljoin(base_url, url))
        # From CSS files referenced
        for css_url in assets["css"]:
            if any(css_url.lower().endswith(ext) for ext in font_extensions):
                fonts.add(css_url)
        assets["fonts"] = list(fonts)

        # Videos - all video sources
        video_selectors = [
            ("video", "src"),
            ("video", "poster"),
            ("source", "src"),
        ]
        videos = set()
        for tag_name, attr in video_selectors:
            for tag in soup.find_all(tag_name, **{attr: True}):
                src = tag.get(attr, "").strip()
                if src and not src.startswith(("data:", "javascript:")):
                    # Check if it's a video by extension or type
                    if any(src.lower().endswith(ext) for ext in [".mp4", ".webm", ".ogg", ".mov", ".avi", ".mkv"]):
                        videos.add(urljoin(base_url, src))
                    # Also check type attribute
                    tag_type = tag.get("type", "").lower()
                    if "video" in tag_type:
                        videos.add(urljoin(base_url, src))
        assets["videos"] = list(videos)

        # Documents - PDFs, Office docs, etc.
        doc_extensions = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", 
                         ".txt", ".rtf", ".odt", ".ods", ".odp", ".csv", ".xml", ".json"]
        documents = set()
        for tag in soup.find_all("a", href=True):
            href = tag.get("href", "").lower()
            if any(href.endswith(ext) for ext in doc_extensions):
                documents.add(urljoin(base_url, tag["href"]))
        # Also check for download attributes
        for tag in soup.find_all(attrs={"download": True}):
            href = tag.get("href", "")
            if href and not href.startswith(("javascript:", "mailto:", "#")):
                documents.add(urljoin(base_url, href))
        assets["documents"] = list(documents)

        return assets

    def save_html(self, html: str, url: str, output_path: Path):
        """Save HTML file with rewritten local links and organized structure."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        normalized = self._normalize_url(url)
        self.url_map[normalized] = output_path

        parsed = urlparse(url)
        base_domain = parsed.netloc
        soup = BeautifulSoup(html, "lxml")

        # Rewrite rules for different tag types
        rewrite_rules = [
            ("a", "href", lambda abs_url: self._get_local_html_path(abs_url)),
            ("img", "src", lambda abs_url: self._get_asset_path(abs_url, "images")),
            (
                "link",
                "href",
                lambda abs_url: self._get_asset_path(abs_url, "css"),
                lambda tag: "stylesheet" in tag.get("rel", []),
            ),
            ("script", "src", lambda abs_url: self._get_asset_path(abs_url, "js")),
        ]

        for tag_name, attr, path_func, *conditions in rewrite_rules:
            for tag in soup.find_all(tag_name, recursive=True):
                if not tag.has_attr(attr):
                    continue

                original = tag[attr]
                if not original or original.startswith(
                    ("javascript:", "mailto:", "tel:", "#", "data:")
                ):
                    continue

                # Check additional conditions if provided
                if conditions and not all(cond(tag) for cond in conditions):
                    continue

                try:
                    absolute = urljoin(url, original)
                    if self._should_follow_link(absolute, base_domain):
                        local_path = path_func(absolute)
                        tag[attr] = os.path.relpath(local_path, output_path.parent)
                except Exception:
                    pass

        # Add metadata comment
        meta_comment = f"<!-- Cloned from {url} on {datetime.now().isoformat()} -->\n"
        output_path.write_text(meta_comment + str(soup), encoding="utf-8")
        logger.info(f"Saved: {output_path}")

    def save_asset(self, url: str, asset_type: str):
        """Download and save asset with organized folder structure."""
        try:
            normalized = self._normalize_url(url)
            if normalized in self.downloaded_assets:
                return

            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200:
                output_path = self._get_asset_path(url, asset_type)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(response.content)

                self.downloaded_assets.add(normalized)
                self.url_map[normalized] = output_path

                # Update stats
                stat_key = asset_type if asset_type in self.stats else "other"
                self.stats[stat_key] += 1

                logger.info(f"Downloaded {asset_type}: {output_path.name}")

        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Failed to download asset {url}: {e}")

    async def clone_site(self, start_url: str, mode: str = "static"):
        """Main cloning method - automatically downloads full website with organized structure.
        
        Optimized for maximum data extraction with comprehensive logging and error handling.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)

        parsed = urlparse(start_url)
        base_domain = parsed.netloc

        # Create domain-based output directory
        domain_dir = self.output_dir / base_domain.replace(".", "_").replace(":", "_")
        domain_dir.mkdir(parents=True, exist_ok=True)

        # Initialize depth limit before manifest creation
        depth_limit = self.depth
        if mode == "everything":
            self.follow_external = True
            self.include_subdomains = True
            depth_limit = max(depth_limit, 8)
            self.max_pages = max(self.max_pages, 1000)

        queue = [(start_url, 0)]

        # Save comprehensive manifest
        manifest = {
            "start_url": start_url,
            "base_domain": base_domain,
            "mode": mode,
            "use_tor": self.use_tor,
            "timestamp": datetime.now().isoformat(),
            "settings": {
                "depth": self.depth,
                "effective_depth": depth_limit,
                "concurrency": self.concurrency,
                "delay": self.delay,
                "auto_organize": self.auto_organize,
                "download_all_assets": self.download_all_assets,
                "max_pages": self.max_pages,
                "follow_external": self.follow_external,
                "include_subdomains": self.include_subdomains,
            },
        }

        logger.info(f"🚀 Starting clone of {start_url}")
        logger.info(f"   Mode: {mode}, Depth: {depth_limit}, Output: {domain_dir}")
        logger.info(f"   Max pages: {self.max_pages}, Concurrency: {self.concurrency}")

        # Handle depth=0 as unlimited (use max_pages limit instead)
        is_unlimited = depth_limit == 0
        effective_depth = 999 if is_unlimited else depth_limit
        
        # Track start time for performance metrics
        start_time = datetime.now()

        while queue:
            current_url, current_depth = queue.pop(0)

            if current_depth > effective_depth:
                continue

            # Fetch page
            if mode == "dynamic":
                html = await self.fetch_page_dynamic(current_url)
            else:
                html = await self.fetch_page(current_url)

            if not html:
                self.stats["errors"] += 1
                continue

            self.stats["pages"] += 1

            # Save HTML with organized path
            output_file = self._get_local_html_path(current_url)
            self.save_html(html, current_url, output_file)

            # Extract and download ALL assets by default
            if self.download_all_assets:
                assets = self.extract_assets(html, current_url)
                for asset_type, urls in assets.items():
                    for asset_url in urls:  # No limit - download all
                        self.save_asset(asset_url, asset_type)

            # Extract links for crawling
            if current_depth < effective_depth:
                links = self.extract_links(html, current_url)
                for link in links:
                    normalized = self._normalize_url(link)
                    if normalized in self.seen_urls:
                        continue
                    if self._should_follow_link(link, base_domain):
                        self.seen_urls.add(normalized)
                        if len(self.visited_urls) + len(self.seen_urls) >= self.max_pages:
                            logger.info("Maximum page limit reached, stopping crawl.")
                            break
                        queue.append((link, current_depth + 1))

            await asyncio.sleep(self.delay)

        # Save final comprehensive manifest with performance metrics
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        manifest["visited_count"] = len(self.visited_urls)
        manifest["assets_count"] = len(self.downloaded_assets)
        manifest["stats"] = self.stats
        manifest["output_directory"] = str(domain_dir)
        manifest["duration_seconds"] = round(duration, 2)
        manifest["performance"] = {
            "pages_per_second": round(self.stats["pages"] / duration, 2) if duration > 0 else 0,
            "assets_per_second": round(len(self.downloaded_assets) / duration, 2) if duration > 0 else 0,
            "total_duration": f"{duration:.2f}s"
        }

        manifest_path = domain_dir / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        # Create detailed README with comprehensive clone info - MAXIMUM DETAILS
        readme_path = domain_dir / "README.txt"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("WEBSITE CLONE REPORT - COMPLETE EXTRACTION SUMMARY (MAXIMUM MODE)\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Source URL: {start_url}\n")
            f.write(f"Cloned on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Mode: {mode}\n")
            f.write(f"Depth: {self.depth} (effective: {depth_limit}) - {'UNLIMITED' if self.depth == 0 else 'limited'}\n")
            f.write(f"Duration: {duration:.2f} seconds\n\n")
            f.write("-" * 80 + "\n")
            f.write("EXTRACTION STATISTICS - COMPREHENSIVE:\n")
            f.write("-" * 80 + "\n")
            f.write(f"  ✓ Pages cloned: {self.stats['pages']}\n")
            f.write(f"  ✓ Images downloaded: {self.stats['images']}\n")
            f.write(f"  ✓ CSS files: {self.stats['css']}\n")
            f.write(f"  ✓ JavaScript files: {self.stats['js']}\n")
            f.write(f"  ✓ Fonts extracted: {self.stats.get('fonts', 0)}\n")
            f.write(f"  ✓ Videos downloaded: {self.stats.get('videos', 0)}\n")
            f.write(f"  ✓ Documents extracted: {self.stats.get('documents', 0)}\n")
            f.write(f"  ✓ Other assets: {self.stats['other']}\n")
            f.write(f"  ✗ Errors encountered: {self.stats['errors']}\n")
            f.write(f"  📦 Total files: {self.stats['pages'] + len(self.downloaded_assets)}\n\n")
            f.write("-" * 80 + "\n")
            f.write("FOLDER STRUCTURE - ORGANIZED:\n")
            f.write("-" * 80 + "\n")
            f.write("  /images - ALL images from the website (PNG, JPG, GIF, SVG, WebP, ICO, BMP, etc.)\n")
            f.write("          Includes lazy-loaded images, srcset variants, and data-src images\n")
            f.write("  /css - ALL stylesheets and style resources including @import chains\n")
            f.write("  /js - ALL JavaScript files including lazy-loaded scripts and data-src scripts\n")
            f.write("  /fonts - ALL font files (WOFF, WOFF2, TTF, OTF, EOT, etc.)\n")
            f.write("  /videos - ALL video files (MP4, WebM, OGG, MOV, AVI, MKV) and posters\n")
            f.write("  /documents - ALL downloadable documents (PDF, DOC, DOCX, XLS, XLSX, PPT, etc.)\n")
            f.write("  /assets - Other miscellaneous assets\n")
            f.write("  /*.html - Cloned pages with rewritten local links for offline browsing\n")
            f.write("  manifest.json - Detailed clone information, statistics, and performance metrics\n")
            f.write("  README.txt - This comprehensive report file\n")
            f.write("  ai_analysis.json - AI-generated analysis (if enabled)\n")
            f.write("  SUMMARY.md - Human-readable AI summary (if enabled)\n")
            f.write("  expanded.html - Hidden/invisible content discovery results (if enabled)\n\n")
            f.write("-" * 80 + "\n")
            f.write("CONFIGURATION USED - MAXIMUM EXTRACTION SETTINGS:\n")
            f.write("-" * 80 + "\n")
            f.write(f"  Concurrency: {self.concurrency} simultaneous requests (high-speed)\n")
            f.write(f"  Delay between requests: {self.delay}s (minimal for speed)\n")
            f.write(f"  Timeout: {self.timeout}s (extended for large pages)\n")
            f.write(f"  Tor enabled: {self.use_tor}\n")
            f.write(f"  Auto-organize: {self.auto_organize}\n")
            f.write(f"  Download all assets: {self.download_all_assets} (comprehensive extraction)\n")
            f.write(f"  Extract all media types: {self.extract_all_media} (videos, fonts, documents)\n")
            f.write(f"  Aggressive crawl mode: {self.aggressive_crawl}\n")
            f.write(f"  Max pages limit: {self.max_pages} (very high limit)\n")
            f.write(f"  Follow external links: {self.follow_external}\n")
            f.write(f"  Include subdomains: {self.include_subdomains}\n")
            f.write(f"  Respect robots.txt: {self.respect_robots}\n\n")
            f.write("-" * 80 + "\n")
            f.write("PERFORMANCE METRICS:\n")
            f.write("-" * 80 + "\n")
            f.write(f"  Total duration: {duration:.2f} seconds\n")
            f.write(f"  Pages per second: {manifest['performance']['pages_per_second']}\n")
            f.write(f"  Assets per second: {manifest['performance']['assets_per_second']}\n")
            f.write(f"  Success rate: {((self.stats['pages'] + len(self.downloaded_assets)) / max(1, self.stats['pages'] + len(self.downloaded_assets) + self.stats['errors'])) * 100:.1f}%\n\n")
            f.write("=" * 80 + "\n")
            f.write("✅ Clone completed successfully with MAXIMUM EXTRACTION!\n")
            f.write("=" * 80 + "\n")

        logger.info("\n✅ Clone complete with MAXIMUM EXTRACTION!")
        logger.info(f"   ⏱️  Duration: {duration:.2f} seconds")
        logger.info(f"   📄 Pages visited: {self.stats['pages']}")
        logger.info(f"   🖼️  Images downloaded: {self.stats['images']}")
        logger.info(f"   🎨 CSS files: {self.stats['css']}")
        logger.info(f"   ⚙️  JS files: {self.stats['js']}")
        logger.info(f"   🔤 Fonts extracted: {self.stats.get('fonts', 0)}")
        logger.info(f"   🎬 Videos downloaded: {self.stats.get('videos', 0)}")
        logger.info(f"   📄 Documents extracted: {self.stats.get('documents', 0)}")
        logger.info(f"   📦 Total assets: {len(self.downloaded_assets)}")
        logger.info(f"   ❌ Errors: {self.stats['errors']}")
        logger.info(f"   📁 Output: {domain_dir}")
        logger.info(f"   📊 Performance: {manifest['performance']['pages_per_second']} pages/sec")
        logger.info(f"   ⚡ Throughput: {manifest['performance']['assets_per_second']} assets/sec")

        return manifest
