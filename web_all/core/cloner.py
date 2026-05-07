"""
Core cloner engine for static and dynamic websites.
Supports clearnet and .onion (Tor) sites.
Auto-downloads full websites with organized folder structure.
"""

import os
import re
import json
import asyncio
import logging
import hashlib
from urllib.parse import urljoin, urlparse, urlunparse
from typing import Set, List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime

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
        save_metadata: bool = True
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
        
        self.visited_urls: Set[str] = set()
        self.seen_urls: Set[str] = set()
        self.downloaded_assets: Set[str] = set()
        self.url_map: Dict[str, Path] = {}
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        self.follow_external = False
        self.include_subdomains = True
        self.max_pages = 1000
        
        if use_tor:
            self._setup_tor_proxy()
        
        self.semaphore = asyncio.Semaphore(concurrency)
        self.stats = {
            "pages": 0,
            "images": 0,
            "css": 0,
            "js": 0,
            "other": 0,
            "errors": 0
        }
        
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
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content with retry logic."""
        async with self.semaphore:
            try:
                normalized = self._normalize_url(url)
                if normalized in self.seen_urls:
                    return None
                    
                logger.info(f"Fetching: {url}")
                
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None, 
                    lambda: self.session.get(url, timeout=self.timeout)
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
    
    async def fetch_page_dynamic(self, url: str, scroll_times: int = 3, wait_time: float = 2.0) -> Optional[str]:
        """Fetch page using headless browser for JavaScript rendering."""
        async with self.semaphore:
            try:
                normalized = self._normalize_url(url)
                if normalized in self.seen_urls:
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
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                self.downloaded_assets.add(normalized)
                self.url_map[normalized] = output_path
                
                # Update stats
                if asset_type == 'images':
                    self.stats['images'] += 1
                elif asset_type == 'css':
                    self.stats['css'] += 1
                elif asset_type == 'js':
                    self.stats['js'] += 1
                else:
                    self.stats['other'] += 1
                
                logger.info(f"Downloaded {asset_type}: {output_path.name}")
                
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Failed to download asset {url}: {e}")
    
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
                self.stats['errors'] += 1
                continue
            
            self.stats['pages'] += 1
            
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
        manifest["stats"] = self.stats
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
            f.write(f"  Pages cloned: {self.stats['pages']}\n")
            f.write(f"  Images downloaded: {self.stats['images']}\n")
            f.write(f"  CSS files: {self.stats['css']}\n")
            f.write(f"  JavaScript files: {self.stats['js']}\n")
            f.write(f"  Other assets: {self.stats['other']}\n")
            f.write(f"  Errors: {self.stats['errors']}\n\n")
            f.write(f"Folder Structure:\n")
            f.write(f"  /images - All images from the website\n")
            f.write(f"  /css - All stylesheets\n")
            f.write(f"  /js - All JavaScript files\n")
            f.write(f"  /*.html - Cloned pages\n")
            f.write(f"  manifest.json - Detailed clone information\n")
        
        logger.info(f"\n✅ Clone complete!")
        logger.info(f"   📄 Pages visited: {self.stats['pages']}")
        logger.info(f"   🖼️  Images downloaded: {self.stats['images']}")
        logger.info(f"   🎨 CSS files: {self.stats['css']}")
        logger.info(f"   ⚙️  JS files: {self.stats['js']}")
        logger.info(f"   📦 Total assets: {len(self.downloaded_assets)}")
        logger.info(f"   ❌ Errors: {self.stats['errors']}")
        logger.info(f"   📁 Output: {domain_dir}")
        
        return manifest
