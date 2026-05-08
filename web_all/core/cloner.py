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
from typing import Any, Dict, List, Optional, Set
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


# Constants
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
DEFAULT_TOR_PROXY = "http://127.0.0.1:9050"
DEFAULT_TIMEOUT = 30
DEFAULT_CONCURRENCY = 5
DEFAULT_DELAY = 0.5
DEFAULT_DEPTH = 2
MAX_PAGES = 1000
ASSET_TYPES = {"images", "css", "js"}


class SiteCloner:
    """Main website cloning engine with Tor support and automatic organization."""

    # Class-level cache for robots.txt to avoid repeated fetches
    _robots_cache: Dict[str, tuple] = {}
    ROBOTS_CACHE_TTL = 3600  # 1 hour cache

    def __init__(
        self,
        output_dir: str = "./output",
        depth: int = DEFAULT_DEPTH,
        concurrency: int = DEFAULT_CONCURRENCY,
        delay: float = DEFAULT_DELAY,
        user_agent: Optional[str] = None,
        use_tor: bool = False,
        tor_proxy: str = DEFAULT_TOR_PROXY,
        timeout: int = DEFAULT_TIMEOUT,
        respect_robots: bool = False,
        auto_organize: bool = True,
        download_all_assets: bool = True,
        save_metadata: bool = True,
        max_pages: int = MAX_PAGES,
        enable_caching: bool = True,
        asset_timeout: Optional[int] = None,
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
        self.enable_caching = enable_caching
        self.asset_timeout = asset_timeout or (timeout // 2)  # Faster timeout for assets

        self.visited_urls: Set[str] = set()
        self.seen_urls: Set[str] = set()
        self.downloaded_assets: Set[str] = set()
        self.url_map: Dict[str, Path] = {}
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        self.follow_external = False
        self.include_subdomains = True
        self.max_pages = max_pages

        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=0.5,
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy, pool_connections=concurrency, pool_maxsize=concurrency * 2
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        if use_tor:
            self._setup_tor_proxy()

        self.semaphore = asyncio.Semaphore(concurrency)
        self.stats = {"pages": 0, "images": 0, "css": 0, "js": 0, "other": 0, "errors": 0}

        # Performance tracking
        self._perf_metrics: Dict[str, List[float]] = {"fetch": [], "save": [], "download": []}

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
        """Fetch page content with retry logic and performance tracking."""
        import time

        start_time = time.perf_counter()

        async with self.semaphore:
            try:
                normalized = self._normalize_url(url)
                if normalized in self.seen_urls:
                    return None

                # Check robots.txt if enabled
                if self.respect_robots and not self._check_robots_allowed(url):
                    logger.info(f"Blocked by robots.txt: {url}")
                    return None

                logger.info(f"Fetching: {url}")

                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(
                    None, lambda: self.session.get(url, timeout=self.timeout)
                )

                if response.status_code == 200:
                    self.seen_urls.add(normalized)
                    self.visited_urls.add(normalized)

                    # Track performance
                    elapsed = time.perf_counter() - start_time
                    self._perf_metrics["fetch"].append(elapsed)

                    return response.text
                elif response.status_code == 304:  # Not modified (cached)
                    logger.debug(f"Cache hit (304): {url}")
                    return None
                else:
                    logger.warning(f"Failed to fetch {url}: {response.status_code}")
                    return None

            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                return None

    def _check_robots_allowed(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt with caching."""
        import time
        from urllib.parse import urlparse

        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        # Check cache first
        current_time = time.time()
        if base_url in self._robots_cache:
            allowed_set, timestamp = self._robots_cache[base_url]
            if current_time - timestamp < self.ROBOTS_CACHE_TTL:
                return parsed.path in allowed_set or any(
                    parsed.path.startswith(p) for p in allowed_set
                )

        # Fetch and parse robots.txt
        try:
            robots_url = f"{base_url}/robots.txt"
            response = self.session.get(robots_url, timeout=5)
            if response.status_code == 200:
                allowed_paths = set()
                lines = response.text.split("\n")
                current_user_agent = None
                found_matching_agent = False

                for line in lines:
                    line = line.strip().lower()
                    if line.startswith("user-agent:"):
                        agent = line.split(":", 1)[1].strip()
                        current_user_agent = agent
                        found_matching_agent = agent == "*" or agent in self.user_agent.lower()
                    elif line.startswith("disallow:") and found_matching_agent:
                        path = line.split(":", 1)[1].strip()
                        if path:
                            allowed_paths.discard(path)
                    elif line.startswith("allow:") and found_matching_agent:
                        path = line.split(":", 1)[1].strip()
                        if path:
                            allowed_paths.add(path)

                # Cache the result
                self._robots_cache[base_url] = (allowed_paths, current_time)
                return parsed.path in allowed_paths or not any(
                    parsed.path.startswith(d) for d in []
                )
            else:
                # No robots.txt or error, allow all
                self._robots_cache[base_url] = (set([parsed.path]), current_time)
                return True
        except Exception:
            # On error, assume allowed
            self._robots_cache[base_url] = (set([parsed.path]), current_time)
            return True

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
        """Extract asset URLs (images, CSS, JS)."""
        soup = BeautifulSoup(html, "lxml")
        assets = {"images": [], "css": [], "js": []}

        # Images
        assets["images"] = [
            urljoin(base_url, img["src"].strip())
            for img in soup.find_all("img", src=True)
            if not img["src"].strip().startswith(("data:", "javascript:"))
        ]

        # CSS
        assets["css"] = [
            urljoin(base_url, link["href"].strip())
            for link in soup.find_all("link", rel="stylesheet", href=True)
        ]

        # JS
        assets["js"] = [
            urljoin(base_url, script["src"].strip())
            for script in soup.find_all("script", src=True)
        ]

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
        """Download and save asset with organized folder structure and optimized timeout."""
        import time

        start_time = time.perf_counter()

        try:
            normalized = self._normalize_url(url)
            if normalized in self.downloaded_assets:
                return

            # Use shorter timeout for assets (they're less critical)
            response = self.session.get(url, timeout=self.asset_timeout)
            if response.status_code == 200:
                output_path = self._get_asset_path(url, asset_type)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(response.content)

                self.downloaded_assets.add(normalized)
                self.url_map[normalized] = output_path

                # Update stats
                stat_key = asset_type if asset_type in self.stats else "other"
                self.stats[stat_key] += 1

                # Track performance
                elapsed = time.perf_counter() - start_time
                self._perf_metrics["download"].append(elapsed)

                logger.info(f"Downloaded {asset_type}: {output_path.name}")

        except Exception as e:
            self.stats["errors"] += 1
            logger.debug(
                f"Failed to download asset {url}: {e}"
            )  # Debug level for noisy asset errors

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance statistics for the cloning session."""
        import statistics

        metrics = {}
        for operation, times in self._perf_metrics.items():
            if times:
                metrics[f"{operation}_avg_ms"] = round(statistics.mean(times) * 1000, 2)
                metrics[f"{operation}_min_ms"] = round(min(times) * 1000, 2)
                metrics[f"{operation}_max_ms"] = round(max(times) * 1000, 2)
                if len(times) > 1:
                    metrics[f"{operation}_stddev_ms"] = round(statistics.stdev(times) * 1000, 2)

        metrics["total_operations"] = sum(len(v) for v in self._perf_metrics.values())
        return metrics

    async def clone_site(self, start_url: str, mode: str = "static"):
        """Main cloning method - automatically downloads full website with organized structure."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        parsed = urlparse(start_url)
        base_domain = parsed.netloc

        # Create domain-based output directory
        domain_dir = self.output_dir / base_domain.replace(".", "_").replace(":", "_")
        domain_dir.mkdir(parents=True, exist_ok=True)

        # Initialize depth_limit before using it in manifest
        depth_limit = self.depth
        if mode == "everything":
            self.follow_external = True
            self.include_subdomains = True
            depth_limit = max(depth_limit, 8)
            self.max_pages = max(self.max_pages, 1000)

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

        queue = [(start_url, 0)]

        logger.info(f"🚀 Starting clone of {start_url}")
        logger.info(f"   Mode: {mode}, Depth: {depth_limit}, Output: {domain_dir}")

        # Handle depth=0 as unlimited (use max_pages limit instead)
        is_unlimited = depth_limit == 0
        effective_depth = 999 if is_unlimited else depth_limit

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

        # Save final comprehensive manifest
        manifest["visited_count"] = len(self.visited_urls)
        manifest["assets_count"] = len(self.downloaded_assets)
        manifest["stats"] = self.stats
        manifest["output_directory"] = str(domain_dir)

        manifest_path = domain_dir / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        # Create README with clone info
        readme_path = domain_dir / "README.txt"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write("Website Clone Report\n")
            f.write("====================\n\n")
            f.write(f"Source URL: {start_url}\n")
            f.write(f"Cloned on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Mode: {mode}\n")
            f.write(f"Depth: {self.depth}\n\n")
            f.write("Statistics:\n")
            f.write(f"  Pages cloned: {self.stats['pages']}\n")
            f.write(f"  Images downloaded: {self.stats['images']}\n")
            f.write(f"  CSS files: {self.stats['css']}\n")
            f.write(f"  JavaScript files: {self.stats['js']}\n")
            f.write(f"  Other assets: {self.stats['other']}\n")
            f.write(f"  Errors: {self.stats['errors']}\n\n")
            f.write("Folder Structure:\n")
            f.write("  /images - All images from the website\n")
            f.write("  /css - All stylesheets\n")
            f.write("  /js - All JavaScript files\n")
            f.write("  /*.html - Cloned pages\n")
            f.write("  manifest.json - Detailed clone information\n")

        logger.info("\n✅ Clone complete!")
        logger.info(f"   📄 Pages visited: {self.stats['pages']}")
        logger.info(f"   🖼️  Images downloaded: {self.stats['images']}")
        logger.info(f"   🎨 CSS files: {self.stats['css']}")
        logger.info(f"   ⚙️  JS files: {self.stats['js']}")
        logger.info(f"   📦 Total assets: {len(self.downloaded_assets)}")
        logger.info(f"   ❌ Errors: {self.stats['errors']}")
        logger.info(f"   📁 Output: {domain_dir}")

        return manifest
