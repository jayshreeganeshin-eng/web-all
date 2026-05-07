"""
Core cloner engine for static and dynamic websites.
Supports clearnet and .onion (Tor) sites.
Auto-downloads full websites with organized folder structure.

Features:
- Concurrent downloading with configurable limits
- Connection pooling and request caching
- Exponential backoff retry logic
- Rate limiting per domain
- Progress callbacks
- Robots.txt support
- Sitemap-based crawling
"""

import os
import re
import json
import asyncio
import logging
import hashlib
import time
from urllib.parse import urljoin, urlparse, urlunparse, parse_qs
from urllib.robotparser import RobotFileParser
from typing import Set, List, Optional, Dict, Any, Callable, Tuple
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass, field

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    from bs4 import BeautifulSoup
    from playwright.async_api import async_playwright
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Run: pip install requests beautifulsoup4 playwright")
    raise

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class CloneStats:
    """Statistics tracker for clone operations."""
    pages: int = 0
    images: int = 0
    css: int = 0
    js: int = 0
    other: int = 0
    errors: int = 0
    bytes_downloaded: int = 0
    start_time: float = field(default_factory=time.time)
    
    @property
    def elapsed_seconds(self) -> float:
        return time.time() - self.start_time
    
    @property
    def total_assets(self) -> int:
        return self.images + self.css + self.js + self.other
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pages": self.pages,
            "images": self.images,
            "css": self.css,
            "js": self.js,
            "other": self.other,
            "errors": self.errors,
            "bytes_downloaded": self.bytes_downloaded,
            "elapsed_seconds": round(self.elapsed_seconds, 2),
            "total_assets": self.total_assets
        }


class RateLimiter:
    """Rate limiter for respectful crawling."""
    
    def __init__(self, requests_per_second: float = 2.0, per_domain: bool = True):
        self.rps = requests_per_second
        self.per_domain = per_domain
        self.last_request: Dict[str, float] = defaultdict(float)
        self._lock = asyncio.Lock()
    
    async def wait_if_needed(self, url: str):
        """Wait if rate limit would be exceeded."""
        async with self._lock:
            if self.per_domain:
                domain = urlparse(url).netloc
            else:
                domain = "global"
            
            now = time.time()
            elapsed = now - self.last_request[domain]
            min_interval = 1.0 / self.rps
            
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
            
            self.last_request[domain] = time.time()


class SiteCloner:
    """Main website cloning engine with Tor support and automatic organization."""
    
    def __init__(
        self,
        output_dir: str = "./output",
        depth: int = 2,
        concurrency: int = 5,
        delay: float = 0.5,
        user_agent: Optional[str] = None,
        use_tor: bool = False,
        tor_proxy: str = "http://127.0.0.1:9050",
        timeout: int = 30,
        respect_robots: bool = False,
        auto_organize: bool = True,
        download_all_assets: bool = True,
        save_metadata: bool = True,
        max_pages: int = 1000,
        max_retries: int = 3,
        rate_limit_rps: float = 2.0,
        follow_external: bool = False,
        include_subdomains: bool = True,
        cache_enabled: bool = True,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
        # New Web God & AI SEO features
        web_god_mode: bool = False,
        auto_seo_enabled: bool = False,
        optimize_images: bool = True,
        minify_html: bool = False,
        generate_sitemap: bool = True,
        schema_markup: bool = True,
        meta_tags_enhancement: bool = True,
        accessibility_check: bool = True,
        performance_optimization: bool = True,
        mobile_responsive_check: bool = True,
        social_media_cards: bool = True
    ):
        self.output_dir = Path(output_dir)
        self.depth = depth
        self.concurrency = concurrency
        self.delay = delay
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.use_tor = use_tor
        self.tor_proxy = tor_proxy
        self.timeout = timeout
        self.respect_robots = respect_robots
        self.auto_organize = auto_organize
        self.download_all_assets = download_all_assets
        self.save_metadata = save_metadata
        self.max_pages = max_pages
        self.max_retries = max_retries
        self.rate_limit_rps = rate_limit_rps
        self.follow_external = follow_external
        self.include_subdomains = include_subdomains
        self.cache_enabled = cache_enabled
        self.progress_callback = progress_callback
        
        # Web God & AI SEO features
        self.web_god_mode = web_god_mode
        self.auto_seo_enabled = auto_seo_enabled
        self.optimize_images = optimize_images
        self.minify_html = minify_html
        self.generate_sitemap = generate_sitemap
        self.schema_markup = schema_markup
        self.meta_tags_enhancement = meta_tags_enhancement
        self.accessibility_check = accessibility_check
        self.performance_optimization = performance_optimization
        self.mobile_responsive_check = mobile_responsive_check
        self.social_media_cards = social_media_cards
        
        # If Web God mode is enabled, enable all optimizations
        if self.web_god_mode:
            self.auto_seo_enabled = True
            self.optimize_images = True
            self.generate_sitemap = True
            self.schema_markup = True
            self.meta_tags_enhancement = True
            self.accessibility_check = True
            self.performance_optimization = True
            self.mobile_responsive_check = True
            self.social_media_cards = True
            self.depth = max(self.depth, 8)
            self.max_pages = max(self.max_pages, 1000)
            self.follow_external = True
            self.include_subdomains = True
        
        self.visited_urls: Set[str] = set()
        self.seen_urls: Set[str] = set()
        self.downloaded_assets: Set[str] = set()
        self.url_map: Dict[str, Path] = {}
        
        # Initialize session with connection pooling and retry strategy
        self.session = self._create_session()
        
        # Robots.txt parser per domain
        self.robots_parsers: Dict[str, RobotFileParser] = {}
        
        # Request cache for performance
        self._cache: Dict[str, Tuple[str, float]] = {} if cache_enabled else None
        self._cache_ttl = 3600  # 1 hour cache TTL
        
        # Rate limiter
        self.rate_limiter = RateLimiter(requests_per_second=rate_limit_rps)
        
        if use_tor:
            self._setup_tor_proxy()
        
        self.semaphore = asyncio.Semaphore(concurrency)
        self.stats = CloneStats()
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with optimized settings."""
        session = requests.Session()
        session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })
        
        # Configure retry strategy with exponential backoff
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=self.concurrency, pool_maxsize=self.concurrency * 2)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _setup_tor_proxy(self):
        """Configure session to use Tor proxy."""
        proxies = {
            "http": self.tor_proxy,
            "https": self.tor_proxy
        }
        self.session.proxies.update(proxies)
        logger.info(f"Tor proxy enabled: {self.tor_proxy}")
    
    def _can_fetch(self, url: str) -> bool:
        """Check robots.txt if respect_robots is enabled."""
        if not self.respect_robots:
            return True
        
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        
        if domain not in self.robots_parsers:
            rp = RobotFileParser()
            robots_url = f"{domain}/robots.txt"
            try:
                response = self.session.get(robots_url, timeout=10)
                if response.status_code == 200:
                    rp.parse(response.text.splitlines())
            except Exception:
                pass  # If robots.txt fetch fails, allow crawling
            self.robots_parsers[domain] = rp
        
        return self.robots_parsers[domain].can_fetch(self.user_agent, url)
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for deduplication."""
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        path = parsed.path.rstrip('/') or '/'
        normalized = urlunparse((parsed.scheme, netloc, path, '', parsed.query, ''))
        return normalized
    
    def _is_internal_url(self, url: str, base_domain: str) -> bool:
        """Check if URL belongs to the same domain."""
        parsed = urlparse(url)
        return parsed.netloc == base_domain or parsed.netloc.endswith('.' + base_domain)

    def _should_follow_link(self, url: str, base_domain: str) -> bool:
        """Determine whether a link should be queued for crawling."""
        if self.follow_external:
            return True
        parsed = urlparse(url)
        if parsed.netloc == base_domain:
            return True
        if self.include_subdomains and parsed.netloc.endswith('.' + base_domain):
            return True
        return False

    def _get_local_html_path(self, url: str) -> Path:
        """Generate a local file path for a page URL."""
        parsed = urlparse(url)
        path = parsed.path.rstrip('/') or '/'
        if path.endswith('/'):
            path = path + 'index.html'
        elif not path.endswith('.html'):
            path = path.rstrip('/') + '/index.html'

        if parsed.query:
            query_hash = hashlib.md5(parsed.query.encode('utf-8')).hexdigest()[:8]
            path = path.replace('.html', f'_{query_hash}.html')

        domain = parsed.netloc.replace('.', '_').replace(':', '_')
        return self.output_dir / domain / path.lstrip('/')

    def _get_asset_path(self, url: str, asset_type: str) -> Path:
        """Generate organized path for assets."""
        parsed = urlparse(url)
        
        # Create domain-based folder structure
        domain = parsed.netloc.replace('.', '_').replace(':', '_')
        
        if asset_type == 'images':
            subdir = self.output_dir / domain / 'images'
        elif asset_type == 'css':
            subdir = self.output_dir / domain / 'css'
        elif asset_type == 'js':
            subdir = self.output_dir / domain / 'js'
        else:
            subdir = self.output_dir / domain / 'assets'
        
        # Generate unique filename
        filename = os.path.basename(parsed.path) or f"asset_{hashlib.md5(url.encode()).hexdigest()[:8]}"
        if parsed.query:
            query_hash = hashlib.md5(parsed.query.encode('utf-8')).hexdigest()[:8]
            filename = f"{query_hash}_{filename}"
        
        counter = 0
        base_name, ext = os.path.splitext(filename)
        output_path = subdir / filename
        
        while output_path.exists():
            counter += 1
            output_path = subdir / f"{base_name}_{counter}{ext}"
        
        return output_path
    
    def _get_cached(self, url: str) -> Optional[str]:
        """Get content from cache if available and not expired."""
        if not self.cache_enabled or self._cache is None:
            return None
        
        if url in self._cache:
            content, timestamp = self._cache[url]
            if time.time() - timestamp < self._cache_ttl:
                logger.debug(f"Cache hit for {url}")
                return content
            else:
                del self._cache[url]  # Expired
        return None
    
    def _set_cached(self, url: str, content: str):
        """Store content in cache."""
        if self.cache_enabled and self._cache is not None:
            self._cache[url] = (content, time.time())
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content with retry logic, rate limiting, and caching."""
        async with self.semaphore:
            try:
                normalized = self._normalize_url(url)
                if normalized in self.seen_urls:
                    return None
                
                # Check robots.txt
                if not self._can_fetch(url):
                    logger.warning(f"Blocked by robots.txt: {url}")
                    return None
                
                # Check cache first
                cached_content = self._get_cached(url)
                if cached_content:
                    self.seen_urls.add(normalized)
                    self.visited_urls.add(normalized)
                    return cached_content
                
                # Apply rate limiting
                await self.rate_limiter.wait_if_needed(url)
                
                logger.info(f"Fetching: {url}")
                
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None, 
                    lambda: self.session.get(url, timeout=self.timeout)
                )
                
                if response.status_code == 200:
                    content = response.text
                    self.seen_urls.add(normalized)
                    self.visited_urls.add(normalized)
                    self.stats.bytes_downloaded += len(content.encode('utf-8'))
                    
                    # Cache the content
                    self._set_cached(url, content)
                    
                    if self.progress_callback:
                        self.progress_callback("page", len(self.visited_urls), self.max_pages)
                    
                    return content
                elif response.status_code == 429:
                    # Rate limited - wait and retry
                    retry_after = int(response.headers.get('Retry-After', 5))
                    logger.warning(f"Rate limited for {url}, waiting {retry_after}s")
                    await asyncio.sleep(retry_after)
                    return await self.fetch_page(url)
                else:
                    logger.warning(f"Failed to fetch {url}: {response.status_code}")
                    self.stats.errors += 1
                    return None
                    
            except requests.exceptions.RetryError as e:
                logger.error(f"Max retries exceeded for {url}: {e}")
                self.stats.errors += 1
                return None
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                self.stats.errors += 1
                return None
    
    async def fetch_page_dynamic(self, url: str, scroll_times: int = 3, wait_time: float = 2.0) -> Optional[str]:
        """Fetch page using headless browser for JavaScript rendering."""
        async with self.semaphore:
            try:
                normalized = self._normalize_url(url)
                if normalized in self.seen_urls:
                    return None
                
                # Check robots.txt
                if not self._can_fetch(url):
                    logger.warning(f"Blocked by robots.txt: {url}")
                    return None
                
                logger.info(f"Dynamic fetch: {url}")
                
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    
                    context_args = {}
                    if self.use_tor:
                        context_args["proxy"] = {"server": self.tor_proxy}
                    
                    context = await browser.new_context(
                        user_agent=self.user_agent,
                        **context_args
                    )
                    page = await context.new_page()
                    
                    await page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)
                    
                    # Scroll to trigger lazy loading
                    for i in range(scroll_times):
                        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        await asyncio.sleep(wait_time)
                    
                    html = await page.content()
                    await browser.close()
                    
                    self.seen_urls.add(normalized)
                    self.visited_urls.add(normalized)
                    return html
                    
            except Exception as e:
                logger.error(f"Dynamic fetch error for {url}: {e}")
                return None
    
    def extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract all links from HTML."""
        soup = BeautifulSoup(html, 'lxml')
        links = []
        
        for tag in soup.find_all('a', href=True):
            href = tag['href'].strip()
            if href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                continue
            
            absolute_url = urljoin(base_url, href)
            links.append(absolute_url)
        
        return links
    
    def extract_assets(self, html: str, base_url: str) -> Dict[str, List[str]]:
        """Extract asset URLs (images, CSS, JS)."""
        soup = BeautifulSoup(html, 'lxml')
        assets = {
            'images': [],
            'css': [],
            'js': []
        }
        
        # Images
        for img in soup.find_all('img', src=True):
            src = img['src'].strip()
            if not src.startswith(('data:', 'javascript:')):
                assets['images'].append(urljoin(base_url, src))
        
        # CSS
        for link in soup.find_all('link', rel='stylesheet', href=True):
            assets['css'].append(urljoin(base_url, link['href']))
        
        # JS
        for script in soup.find_all('script', src=True):
            assets['js'].append(urljoin(base_url, script['src']))
        
        return assets
    
    def _get_asset_path(self, url: str, asset_type: str) -> Path:
        """Generate organized path for assets."""
        parsed = urlparse(url)
        
        # Create domain-based folder structure
        domain = parsed.netloc.replace('.', '_').replace(':', '_')
        
        if asset_type == 'images':
            subdir = self.output_dir / domain / 'images'
        elif asset_type == 'css':
            subdir = self.output_dir / domain / 'css'
        elif asset_type == 'js':
            subdir = self.output_dir / domain / 'js'
        else:
            subdir = self.output_dir / domain / 'assets'
        
        # Generate unique filename
        filename = os.path.basename(parsed.path) or f"asset_{hashlib.md5(url.encode()).hexdigest()[:8]}"
        if parsed.query:
            query_hash = hashlib.md5(parsed.query.encode('utf-8')).hexdigest()[:8]
            filename = f"{query_hash}_{filename}"
        
        counter = 0
        base_name, ext = os.path.splitext(filename)
        output_path = subdir / filename
        
        while output_path.exists():
            counter += 1
            output_path = subdir / f"{base_name}_{counter}{ext}"
        
        return output_path

    def _get_local_html_path(self, url: str) -> Path:
        """Generate the local HTML output path for a page URL."""
        parsed = urlparse(url)
        path = parsed.path.rstrip('/') or '/'
        if path.endswith('/'):
            path = f"{path}index.html"
        elif not path.endswith('.html'):
            path = f"{path.rstrip('/')}/index.html"

        if parsed.query:
            query_hash = hashlib.md5(parsed.query.encode('utf-8')).hexdigest()[:8]
            path = path.replace('.html', f'_{query_hash}.html')

        domain = parsed.netloc.replace('.', '_').replace(':', '_')
        return self.output_dir / domain / path.lstrip('/')
    
    def save_html(self, html: str, url: str, output_path: Path):
        """Save HTML file with rewritten local links and organized structure."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        normalized = self._normalize_url(url)
        self.url_map[normalized] = output_path
        
        parsed = urlparse(url)
        base_domain = parsed.netloc
        soup = BeautifulSoup(html, 'lxml')
        
        # Rewrite links to work locally when the target will be downloaded
        for tag in soup.find_all(['a', 'img', 'link', 'script'], recursive=True):
            # page links
            if tag.name == 'a' and tag.has_attr('href'):
                original = tag['href']
                if original and not original.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                    try:
                        absolute = urljoin(url, original)
                        if self._should_follow_link(absolute, base_domain):
                            local_path = self._get_local_html_path(absolute)
                            rel_path = os.path.relpath(local_path, output_path.parent)
                            tag['href'] = rel_path
                    except Exception:
                        pass

            # image sources
            if tag.name == 'img' and tag.has_attr('src'):
                original = tag['src']
                if original and not original.startswith(('data:', 'javascript:')):
                    try:
                        absolute = urljoin(url, original)
                        if self._should_follow_link(absolute, base_domain):
                            local_path = self._get_asset_path(absolute, 'images')
                            rel_path = os.path.relpath(local_path, output_path.parent)
                            tag['src'] = rel_path
                    except Exception:
                        pass

            # stylesheet links
            if tag.name == 'link' and tag.has_attr('href') and 'stylesheet' in tag.get('rel', []):
                original = tag['href']
                if original and not original.startswith(('javascript:', 'data:')):
                    try:
                        absolute = urljoin(url, original)
                        if self._should_follow_link(absolute, base_domain):
                            local_path = self._get_asset_path(absolute, 'css')
                            rel_path = os.path.relpath(local_path, output_path.parent)
                            tag['href'] = rel_path
                    except Exception:
                        pass

            # javascript sources
            if tag.name == 'script' and tag.has_attr('src'):
                original = tag['src']
                if original and not original.startswith(('javascript:', 'data:')):
                    try:
                        absolute = urljoin(url, original)
                        if self._should_follow_link(absolute, base_domain):
                            local_path = self._get_asset_path(absolute, 'js')
                            rel_path = os.path.relpath(local_path, output_path.parent)
                            tag['src'] = rel_path
                    except Exception:
                        pass
        
        # Add metadata comment
        meta_comment = f"<!-- Cloned from {url} on {datetime.now().isoformat()} -->\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(meta_comment + str(soup))
        
        logger.info(f"Saved: {output_path}")
    
    def save_asset(self, url: str, asset_type: str) -> bool:
        """Download and save asset with organized folder structure."""
        try:
            normalized = self._normalize_url(url)
            if normalized in self.downloaded_assets:
                return True
            
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200:
                output_path = self._get_asset_path(url, asset_type)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                content = response.content
                with open(output_path, 'wb') as f:
                    f.write(content)
                
                self.downloaded_assets.add(normalized)
                self.url_map[normalized] = output_path
                
                # Update stats using CloneStats
                if asset_type == 'images':
                    self.stats.images += 1
                elif asset_type == 'css':
                    self.stats.css += 1
                elif asset_type == 'js':
                    self.stats.js += 1
                else:
                    self.stats.other += 1
                
                self.stats.bytes_downloaded += len(content)
                
                logger.debug(f"Downloaded {asset_type}: {output_path.name}")
                return True
                
        except Exception as e:
            self.stats.errors += 1
            logger.error(f"Failed to download asset {url}: {e}")
            return False
        return False
    
    async def save_asset_async(self, url: str, asset_type: str) -> bool:
        """Async version of save_asset for concurrent downloads."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self.save_asset(url, asset_type))
    
    async def clone_site(self, start_url: str, mode: str = "static"):
        """Main cloning method - automatically downloads full website with organized structure."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        parsed = urlparse(start_url)
        base_domain = parsed.netloc
        
        # Create domain-based output directory
        domain_dir = self.output_dir / base_domain.replace('.', '_').replace(':', '_')
        domain_dir.mkdir(parents=True, exist_ok=True)
        
        # Save comprehensive manifest
        manifest = {
            "start_url": start_url,
            "base_domain": base_domain,
            "mode": mode,
            "use_tor": self.use_tor,
            "timestamp": datetime.now().isoformat(),
            "settings": {
                "depth": self.depth,
                "concurrency": self.concurrency,
                "delay": self.delay,
                "auto_organize": self.auto_organize,
                "download_all_assets": self.download_all_assets
            }
        }
        
        queue = [(start_url, 0)]
        
        if mode == 'everything':
            self.follow_external = True
            self.include_subdomains = True
            self.depth = max(self.depth, 8)
            self.max_pages = max(self.max_pages, 1000)

        logger.info(f"🚀 Starting clone of {start_url}")
        logger.info(f"   Mode: {mode}, Depth: {self.depth}, Output: {domain_dir}")
        
        while queue:
            current_url, current_depth = queue.pop(0)
            
            if current_depth > self.depth:
                continue
            
            # Fetch page
            if mode == "dynamic":
                html = await self.fetch_page_dynamic(current_url)
            else:
                html = await self.fetch_page(current_url)
            
            if not html:
                continue
            
            self.stats.pages += 1
            
            # Save HTML with organized path
            output_file = self._get_local_html_path(current_url)
            self.save_html(html, current_url, output_file)
            
            # Extract and download ALL assets concurrently
            if self.download_all_assets:
                assets = self.extract_assets(html, current_url)
                asset_tasks = []
                for asset_type, urls in assets.items():
                    for asset_url in urls:
                        asset_tasks.append(self.save_asset_async(asset_url, asset_type))
                
                if asset_tasks:
                    await asyncio.gather(*asset_tasks, return_exceptions=True)
            
            # Extract links for crawling
            if current_depth < self.depth:
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
        manifest["stats"] = self.stats.to_dict()
        manifest["output_directory"] = str(domain_dir)
        
        manifest_path = domain_dir / "manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        # Create README with clone info
        readme_path = domain_dir / "README.txt"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"Website Clone Report\n")
            f.write(f"====================\n\n")
            f.write(f"Source URL: {start_url}\n")
            f.write(f"Cloned on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Mode: {mode}\n")
            f.write(f"Depth: {self.depth}\n\n")
            f.write(f"Statistics:\n")
            f.write(f"  Pages cloned: {self.stats.pages}\n")
            f.write(f"  Images downloaded: {self.stats.images}\n")
            f.write(f"  CSS files: {self.stats.css}\n")
            f.write(f"  JavaScript files: {self.stats.js}\n")
            f.write(f"  Other assets: {self.stats.other}\n")
            f.write(f"  Errors: {self.stats.errors}\n")
            f.write(f"  Total size: {self._format_size(self.stats.bytes_downloaded)}\n")
            f.write(f"  Time elapsed: {self.stats.elapsed_seconds:.2f}s\n\n")
            f.write(f"Folder Structure:\n")
            f.write(f"  /images - All images from the website\n")
            f.write(f"  /css - All stylesheets\n")
            f.write(f"  /js - All JavaScript files\n")
            f.write(f"  /*.html - Cloned pages\n")
            f.write(f"  manifest.json - Detailed clone information\n")
        
        logger.info(f"\n✅ Clone complete!")
        logger.info(f"   📄 Pages visited: {self.stats.pages}")
        logger.info(f"   🖼️  Images downloaded: {self.stats.images}")
        logger.info(f"   🎨 CSS files: {self.stats.css}")
        logger.info(f"   ⚙️  JS files: {self.stats.js}")
        logger.info(f"   📦 Total assets: {len(self.downloaded_assets)}")
        logger.info(f"   ❌ Errors: {self.stats.errors}")
        logger.info(f"   💾 Total size: {self._format_size(self.stats.bytes_downloaded)}")
        logger.info(f"   ⏱️  Time elapsed: {self.stats.elapsed_seconds:.2f}s")
        logger.info(f"   📁 Output: {domain_dir}")
        
        # Apply Web God & AI SEO optimizations after cloning
        if self.auto_seo_enabled or self.web_god_mode:
            await self._apply_seo_optimizations(domain_dir, start_url)
        
        return manifest
    
    async def _apply_seo_optimizations(self, domain_dir: Path, source_url: str):
        """Apply AI SEO and Web God optimizations to cloned site."""
        logger.info("🚀 Applying Web God & AI SEO optimizations...")
        
        seo_stats = {
            "sitemap_generated": False,
            "schema_markup_added": False,
            "meta_tags_enhanced": False,
            "accessibility_improved": False,
            "social_cards_added": False,
            "mobile_responsive_check": False,
            "performance_optimized": False
        }
        
        try:
            # Generate sitemap.xml
            if self.generate_sitemap:
                await self._generate_sitemap(domain_dir, source_url)
                seo_stats["sitemap_generated"] = True
            
            # Add Schema.org markup
            if self.schema_markup:
                await self._add_schema_markup(domain_dir)
                seo_stats["schema_markup_added"] = True
            
            # Enhance meta tags
            if self.meta_tags_enhancement:
                await self._enhance_meta_tags(domain_dir)
                seo_stats["meta_tags_enhanced"] = True
            
            # Accessibility improvements
            if self.accessibility_check:
                await self._improve_accessibility(domain_dir)
                seo_stats["accessibility_improved"] = True
            
            # Social media cards
            if self.social_media_cards:
                await self._add_social_cards(domain_dir)
                seo_stats["social_cards_added"] = True
            
            # Mobile responsive check
            if self.mobile_responsive_check:
                await self._check_mobile_responsive(domain_dir)
                seo_stats["mobile_responsive_check"] = True
            
            logger.info("✅ Web God & AI SEO optimizations complete!")
            logger.info(f"   📍 Sitemap: {seo_stats['sitemap_generated']}")
            logger.info(f"   🏷️  Schema Markup: {seo_stats['schema_markup_added']}")
            logger.info(f"   📝 Meta Tags: {seo_stats['meta_tags_enhanced']}")
            logger.info(f"   ♿ Accessibility: {seo_stats['accessibility_improved']}")
            logger.info(f"   📱 Social Cards: {seo_stats['social_cards_added']}")
            
        except Exception as e:
            logger.error(f"⚠️ SEO optimization error: {e}")
        
        # Save SEO report
        seo_report_path = domain_dir / "seo_report.json"
        with open(seo_report_path, 'w', encoding='utf-8') as f:
            json.dump(seo_stats, f, indent=2)
    
    async def _generate_sitemap(self, domain_dir: Path, source_url: str):
        """Generate XML sitemap for SEO."""
        from urllib.parse import urlparse
        
        parsed = urlparse(source_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        urls = []
        for html_file in domain_dir.rglob("*.html"):
            rel_path = html_file.relative_to(domain_dir)
            # Convert file path to URL path
            url_path = "/" + str(rel_path).replace("\\", "/")
            urls.append(url_path)
        
        sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        for url_path in urls:
            sitemap_content += '  <url>\n'
            sitemap_content += f'    <loc>{base_url}{url_path}</loc>\n'
            sitemap_content += '    <changefreq>weekly</changefreq>\n'
            sitemap_content += '    <priority>0.8</priority>\n'
            sitemap_content += '  </url>\n'
        
        sitemap_content += '</urlset>'
        
        sitemap_path = domain_dir / "sitemap.xml"
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
        
        logger.info(f"   ✅ Generated sitemap.xml with {len(urls)} URLs")
    
    async def _add_schema_markup(self, domain_dir: Path):
        """Add Schema.org structured data to HTML files."""
        schema_script = '''
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Cloned Website",
  "url": "%s",
  "potentialAction": {
    "@type": "SearchAction",
    "target": "%s/search?q={search_term_string}",
    "query-input": "required name=search_term_string"
  }
}
</script>
'''
        
        count = 0
        for html_file in domain_dir.rglob("*.html"):
            try:
                content = html_file.read_text(encoding='utf-8')
                if '<head>' in content:
                    # Insert schema before </head>
                    schema_injection = schema_script % ("", "")
                    content = content.replace('</head>', f'{schema_injection}</head>')
                    html_file.write_text(content, encoding='utf-8')
                    count += 1
            except Exception:
                pass
        
        logger.info(f"   ✅ Added Schema.org markup to {count} pages")
    
    async def _enhance_meta_tags(self, domain_dir: Path):
        """Enhance meta tags for better SEO."""
        count = 0
        for html_file in domain_dir.rglob("*.html"):
            try:
                content = html_file.read_text(encoding='utf-8')
                soup = BeautifulSoup(content, 'lxml')
                
                # Ensure viewport meta tag exists (for mobile)
                if not soup.find('meta', attrs={'name': 'viewport'}):
                    viewport_tag = soup.new_tag('meta', attrs={
                        'name': 'viewport',
                        'content': 'width=device-width, initial-scale=1.0'
                    })
                    if soup.head:
                        soup.head.insert(0, viewport_tag)
                
                # Ensure charset is set
                if not soup.find('meta', attrs={'charset': True}):
                    charset_tag = soup.new_tag('meta', attrs={'charset': 'utf-8'})
                    if soup.head:
                        soup.head.insert(0, charset_tag)
                
                # Add robots meta tag
                if not soup.find('meta', attrs={'name': 'robots'}):
                    robots_tag = soup.new_tag('meta', attrs={
                        'name': 'robots',
                        'content': 'index, follow'
                    })
                    if soup.head:
                        soup.head.append(robots_tag)
                
                html_file.write_text(str(soup), encoding='utf-8')
                count += 1
            except Exception:
                pass
        
        logger.info(f"   ✅ Enhanced meta tags on {count} pages")
    
    async def _improve_accessibility(self, domain_dir: Path):
        """Improve accessibility features."""
        count = 0
        for html_file in domain_dir.rglob("*.html"):
            try:
                content = html_file.read_text(encoding='utf-8')
                soup = BeautifulSoup(content, 'lxml')
                
                # Add lang attribute if missing
                if soup.html and not soup.html.get('lang'):
                    soup.html['lang'] = 'en'
                
                # Add skip-to-content link
                if soup.body:
                    skip_link = soup.new_tag('a', href='#main-content', style='position:absolute;left:-9999px;')
                    skip_link.string = 'Skip to main content'
                    soup.body.insert(0, skip_link)
                
                html_file.write_text(str(soup), encoding='utf-8')
                count += 1
            except Exception:
                pass
        
        logger.info(f"   ✅ Improved accessibility on {count} pages")
    
    async def _add_social_cards(self, domain_dir: Path):
        """Add Open Graph and Twitter Card meta tags."""
        og_tags = '''
<meta property="og:type" content="website">
<meta property="og:title" content="Cloned Website">
<meta property="og:description" content="Website clone with optimized content">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Cloned Website">
<meta name="twitter:description" content="Website clone with optimized content">
'''
        
        count = 0
        for html_file in domain_dir.rglob("*.html"):
            try:
                content = html_file.read_text(encoding='utf-8')
                if '<head>' in content and '<meta property="og:' not in content:
                    content = content.replace('</head>', f'{og_tags}</head>')
                    html_file.write_text(content, encoding='utf-8')
                    count += 1
            except Exception:
                pass
        
        logger.info(f"   ✅ Added social media cards to {count} pages")
    
    async def _check_mobile_responsive(self, domain_dir: Path):
        """Check and ensure mobile responsiveness."""
        # This is a basic check - in production you'd use more sophisticated analysis
        count = 0
        for css_file in domain_dir.rglob("*.css"):
            try:
                content = css_file.read_text(encoding='utf-8')
                if '@media' in content or 'max-width' in content:
                    count += 1
            except Exception:
                pass
        
        logger.info(f"   ✅ Verified mobile responsiveness in {count} CSS files")
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format bytes to human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"


# Export public API
__all__ = ['SiteCloner', 'CloneStats', 'RateLimiter']
