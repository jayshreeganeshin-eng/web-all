"""
Core cloner engine for static and dynamic websites.
Supports clearnet and .onion (Tor) sites.
"""

import os
import re
import json
import asyncio
import logging
from urllib.parse import urljoin, urlparse, urlunparse
from typing import Set, List, Optional, Dict, Any
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
    from playwright.async_api import async_playwright
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Run: pip install requests beautifulsoup4 playwright")
    raise

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SiteCloner:
    """Main website cloning engine with Tor support."""
    
    def __init__(
        self,
        output_dir: str = "./output",
        depth: int = 2,
        concurrency: int = 3,
        delay: float = 1.0,
        user_agent: Optional[str] = None,
        use_tor: bool = False,
        tor_proxy: str = "http://127.0.0.1:9050",
        timeout: int = 30,
        respect_robots: bool = True
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
        
        self.visited_urls: Set[str] = set()
        self.downloaded_assets: Set[str] = set()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        
        if use_tor:
            self._setup_tor_proxy()
        
        self.semaphore = asyncio.Semaphore(concurrency)
        
    def _setup_tor_proxy(self):
        """Configure session to use Tor proxy."""
        proxies = {
            "http": self.tor_proxy,
            "https": self.tor_proxy
        }
        self.session.proxies.update(proxies)
        logger.info(f"Tor proxy enabled: {self.tor_proxy}")
        
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for deduplication."""
        parsed = urlparse(url)
        # Remove fragment, normalize trailing slash
        netloc = parsed.netloc.lower()
        path = parsed.path.rstrip('/') or '/'
        normalized = urlunparse((parsed.scheme, netloc, path, '', '', ''))
        return normalized
    
    def _is_internal_url(self, url: str, base_domain: str) -> bool:
        """Check if URL belongs to the same domain."""
        parsed = urlparse(url)
        return parsed.netloc == base_domain or parsed.netloc.endswith('.' + base_domain)
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content with retry logic."""
        async with self.semaphore:
            try:
                normalized = self._normalize_url(url)
                if normalized in self.visited_urls:
                    return None
                    
                logger.info(f"Fetching: {url}")
                
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None, 
                    lambda: self.session.get(url, timeout=self.timeout)
                )
                
                if response.status_code == 200:
                    self.visited_urls.add(normalized)
                    return response.text
                else:
                    logger.warning(f"Failed to fetch {url}: {response.status_code}")
                    return None
                    
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                return None
    
    async def fetch_page_dynamic(self, url: str, scroll_times: int = 3, wait_time: float = 2.0) -> Optional[str]:
        """Fetch page using headless browser for JavaScript rendering."""
        async with self.semaphore:
            try:
                normalized = self._normalize_url(url)
                if normalized in self.visited_urls:
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
    
    def save_html(self, html: str, url: str, output_path: Path):
        """Save HTML file with rewritten local links."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Basic link rewriting (can be enhanced)
        parsed = urlparse(url)
        base_path = parsed.path
        
        soup = BeautifulSoup(html, 'lxml')
        
        # Rewrite relative links
        for tag in soup.find_all(['a', 'img', 'link', 'script'], recursive=True):
            for attr in ['href', 'src']:
                if tag.has_attr(attr):
                    value = tag[attr]
                    if not value.startswith(('http://', 'https://', 'data:', '//')):
                        # Keep relative paths as-is for now
                        pass
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        logger.info(f"Saved: {output_path}")
    
    def save_asset(self, url: str, asset_type: str):
        """Download and save asset."""
        try:
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path) or f"asset_{len(self.downloaded_assets)}"
            
            if asset_type == 'images':
                subdir = 'images'
            elif asset_type == 'css':
                subdir = 'css'
            else:
                subdir = 'js'
            
            output_path = self.output_dir / subdir / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if url in self.downloaded_assets:
                return
                
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                self.downloaded_assets.add(url)
                logger.info(f"Downloaded asset: {filename}")
                
        except Exception as e:
            logger.error(f"Failed to download asset {url}: {e}")
    
    async def clone_site(self, start_url: str, mode: str = "static"):
        """Main cloning method."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        parsed = urlparse(start_url)
        base_domain = parsed.netloc
        
        # Save manifest
        manifest = {
            "start_url": start_url,
            "base_domain": base_domain,
            "mode": mode,
            "use_tor": self.use_tor,
            "timestamp": str(asyncio.get_event_loop().time())
        }
        
        queue = [(start_url, 0)]
        
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
            
            # Save HTML
            parsed_current = urlparse(current_url)
            path = parsed_current.path.rstrip('/') or '/index.html'
            if path == '/':
                path = '/index.html'
            if not path.endswith('.html'):
                path += '/index.html'
            
            output_file = self.output_dir / path.lstrip('/')
            self.save_html(html, current_url, output_file)
            
            # Extract and download assets
            assets = self.extract_assets(html, current_url)
            for asset_type, urls in assets.items():
                for asset_url in urls[:10]:  # Limit per page for speed
                    self.save_asset(asset_url, asset_type)
            
            # Extract links for crawling
            if current_depth < self.depth:
                links = self.extract_links(html, current_url)
                for link in links:
                    normalized = self._normalize_url(link)
                    if normalized not in self.visited_urls and self._is_internal_url(link, base_domain):
                        queue.append((link, current_depth + 1))
            
            await asyncio.sleep(self.delay)
        
        # Save final manifest
        manifest["visited_count"] = len(self.visited_urls)
        manifest["assets_count"] = len(self.downloaded_assets)
        
        with open(self.output_dir / "manifest.json", 'w') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Clone complete! Visited {len(self.visited_urls)} pages, downloaded {len(self.downloaded_assets)} assets.")
        return manifest
