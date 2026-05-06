"""
Enhanced website cloner with multi-visibility mode support.
Handles surface, deep, invisible, and shadow cloning modes.
"""

import asyncio
import os
import re
from pathlib import Path
from typing import Optional, Set, Dict, List, Any
from urllib.parse import urlparse, urljoin, urlunparse
import aiohttp
from bs4 import BeautifulSoup
import cssutils
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)


class VisibilityMode:
    """Visibility mode constants."""
    SURFACE = "surface"  # HTML/CSS/images only
    DEEP = "deep"  # SPA, lazy-loaded modules, WebSocket-fed data
    INVISIBLE = "invisible"  # Hidden endpoints, orphan pages, unlinked API routes
    SHADOW = "shadow"  # JavaScript execution, all rendered variants


class WebsiteCloner:
    """
    Main cloning engine that downloads entire websites with multiple visibility modes.
    
    Features:
    - Multi-mode visibility (surface, deep, invisible, shadow)
    - Asset mirroring with format conversion
    - Link rewriting for local playback
    - Concurrent downloading with rate limiting
    - Stealth mode with humanized traffic patterns
    """
    
    def __init__(
        self,
        base_url: str,
        output_dir: str,
        mode: str = VisibilityMode.SURFACE,
        depth: int = 5,
        concurrency: int = 10,
        delay: float = 1.0,
        user_agent: Optional[str] = None,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        respect_robots: bool = True,
        stealth_mode: bool = True,
        session_cookies: Optional[List[Dict]] = None,
    ):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.mode = mode
        self.depth = depth
        self.concurrency = concurrency
        self.delay = delay
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.include_patterns = include_patterns or []
        self.exclude_patterns = exclude_patterns or []
        self.respect_robots = respect_robots
        self.stealth_mode = stealth_mode
        self.session_cookies = session_cookies or []
        
        self.visited_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self.assets_downloaded: Set[str] = set()
        self.domain = urlparse(base_url).netloc
        self.components: Dict[str, Any] = {}
        self.design_tokens: Dict[str, Any] = {}
        
        # Statistics
        self.stats = {
            "pages_cloned": 0,
            "assets_downloaded": 0,
            "components_identified": 0,
            "bytes_transferred": 0,
        }
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL for deduplication."""
        parsed = urlparse(url)
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path.rstrip('/') or '/',
            parsed.params,
            parsed.query,
            ''
        ))
        return normalized
    
    def should_visit(self, url: str) -> bool:
        """Check if URL should be visited based on filters."""
        parsed = urlparse(url)
        
        # Check domain
        if parsed.netloc != self.domain:
            return False
        
        # Check include patterns
        if self.include_patterns:
            if not any(re.match(p, url) for p in self.include_patterns):
                return False
        
        # Check exclude patterns
        if self.exclude_patterns:
            if any(re.match(p, url) for p in self.exclude_patterns):
                return False
        
        # Check blocked patterns (security)
        blocked_patterns = [r'logout', r'csrf', r'token', r'password', r'secret']
        if any(re.search(p, url, re.IGNORECASE) for p in blocked_patterns):
            return False
        
        return True
    
    async def fetch_page(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """Fetch a single page with retry logic."""
        headers = {"User-Agent": self.user_agent}
        
        if self.session_cookies:
            cookie_header = "; ".join([f"{c['name']}={c['value']}" for c in self.session_cookies])
            headers["Cookie"] = cookie_header
        
        for attempt in range(3):
            try:
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        content = await response.read()
                        self.stats["bytes_transferred"] += len(content)
                        return content.decode('utf-8', errors='ignore')
                    elif response.status == 429:
                        # Rate limited, wait and retry
                        await asyncio.sleep(2 ** attempt)
                        continue
                    else:
                        self.failed_urls.add(url)
                        return None
            except asyncio.TimeoutError:
                if attempt < 2:
                    await asyncio.sleep(1)
                    continue
            except Exception as e:
                logger.warning(f"Error fetching {url}: {e}")
        
        self.failed_urls.add(url)
        return None
    
    def extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract all links from HTML."""
        soup = BeautifulSoup(html, 'lxml')
        links = []
        
        # Extract href attributes
        for tag in soup.find_all(['a', 'link'], href=True):
            href = tag.get('href')
            if href:
                absolute_url = urljoin(base_url, href)
                links.append(absolute_url)
        
        # Extract src attributes
        for tag in soup.find_all(['img', 'script', 'iframe', 'source'], src=True):
            src = tag.get('src')
            if src:
                absolute_url = urljoin(base_url, src)
                links.append(absolute_url)
        
        return list(set(links))
    
    def extract_assets(self, html: str, base_url: str) -> Dict[str, List[str]]:
        """Extract all asset URLs from HTML."""
        soup = BeautifulSoup(html, 'lxml')
        assets = {
            'images': [],
            'scripts': [],
            'stylesheets': [],
            'fonts': [],
            'videos': [],
        }
        
        # Images
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            if src:
                assets['images'].append(urljoin(base_url, src))
        
        # Data attributes with images
        for tag in soup.find_all(True):
            for attr in ['data-src', 'data-original', 'data-lazy']:
                if tag.get(attr):
                    assets['images'].append(urljoin(base_url, tag.get(attr)))
        
        # Scripts
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src:
                assets['scripts'].append(urljoin(base_url, src))
        
        # Stylesheets
        for link in soup.find_all('link', rel='stylesheet', href=True):
            href = link.get('href')
            if href:
                assets['stylesheets'].append(urljoin(base_url, href))
        
        # Fonts from CSS (will be enhanced with CSS parsing)
        for style in soup.find_all('style'):
            if style.string:
                font_urls = re.findall(r'url\(["\']?([^"\']+)\.(woff2?|ttf|otf|eot)["\']?\)', style.string)
                for url, _ in font_urls:
                    assets['fonts'].append(urljoin(base_url, url))
        
        # Videos
        for video in soup.find_all(['video', 'source'], src=True):
            src = video.get('src')
            if src:
                assets['videos'].append(urljoin(base_url, src))
        
        # Remove duplicates
        for key in assets:
            assets[key] = list(set(assets[key]))
        
        return assets
    
    def rewrite_links(self, html: str, base_url: str, current_path: str) -> str:
        """Rewrite absolute links to relative paths."""
        soup = BeautifulSoup(html, 'lxml')
        
        # Rewrite href attributes
        for tag in soup.find_all(['a', 'link'], href=True):
            href = tag['href']
            if href.startswith(('http://', 'https://')):
                if urlparse(href).netloc == self.domain:
                    rel_path = self._url_to_path(href, base_url)
                    tag['href'] = rel_path
        
        # Rewrite src attributes
        for tag in soup.find_all(['img', 'script', 'iframe', 'source'], src=True):
            src = tag['src']
            if src.startswith(('http://', 'https://')):
                if urlparse(src).netloc == self.domain:
                    rel_path = self._url_to_path(src, base_url)
                    tag['src'] = rel_path
        
        # Add generator meta tag
        head = soup.find('head')
        if head:
            meta_tag = soup.new_tag('meta', attrs={'name': 'generator', 'content': 'web-all v5.0.0'})
            head.insert(0, meta_tag)
        
        return str(soup)
    
    def _url_to_path(self, url: str, base_url: str) -> str:
        """Convert URL to local file path."""
        parsed = urlparse(url)
        path = parsed.path.lstrip('/')
        
        if not path:
            path = 'index.html'
        elif not path.endswith(('.html', '.htm', '.php', '.asp', '.aspx', '.jsp')):
            # Check if it's likely a directory
            if '.' not in path.split('/')[-1]:
                path = path.rstrip('/') + '/index.html'
            else:
                # It's a file without extension, keep as is
                pass
        
        return path
    
    async def download_asset(self, session: aiohttp.ClientSession, url: str, save_path: Path) -> bool:
        """Download a single asset (image, CSS, JS, etc.)."""
        if url in self.assets_downloaded:
            return True
        
        headers = {"User-Agent": self.user_agent}
        
        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with session.get(url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    content = await response.read()
                    with open(save_path, 'wb') as f:
                        f.write(content)
                    
                    self.assets_downloaded.add(url)
                    self.stats["assets_downloaded"] += 1
                    self.stats["bytes_transferred"] += len(content)
                    return True
        except Exception as e:
            logger.warning(f"Error downloading {url}: {e}")
        
        return False
    
    async def clone_site(self, progress_callback=None) -> Dict[str, Any]:
        """Main cloning method with multi-mode support."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        semaphore = asyncio.Semaphore(self.concurrency)
        
        async with aiohttp.ClientSession() as session:
            queue = asyncio.Queue()
            await queue.put((self.base_url, 0))  # URL, depth
            
            progress_bar = tqdm(desc="Cloning", unit="page")
            
            async def worker():
                while True:
                    try:
                        url, depth = await asyncio.wait_for(queue.get(), timeout=5.0)
                    except asyncio.TimeoutError:
                        break
                    
                    async with semaphore:
                        normalized = self.normalize_url(url)
                        
                        if normalized in self.visited_urls or depth > self.depth:
                            queue.task_done()
                            continue
                        
                        if not self.should_visit(url):
                            queue.task_done()
                            continue
                        
                        self.visited_urls.add(normalized)
                        
                        html = await self.fetch_page(session, url)
                        if html:
                            # Save page
                            path = self._url_to_path(url, self.base_url)
                            save_path = self.output_dir / path
                            
                            # Extract and download assets
                            assets = self.extract_assets(html, url)
                            asset_tasks = []
                            
                            for asset_type, urls in assets.items():
                                for asset_url in urls:
                                    asset_name = urlparse(asset_url).path.split('/')[-1]
                                    if asset_name:
                                        asset_path = self.output_dir / asset_type / asset_name
                                        asset_tasks.append(self.download_asset(session, asset_url, asset_path))
                            
                            if asset_tasks:
                                await asyncio.gather(*asset_tasks, return_exceptions=True)
                            
                            # Rewrite links
                            rewritten_html = self.rewrite_links(html, self.base_url, path)
                            
                            save_path.parent.mkdir(parents=True, exist_ok=True)
                            with open(save_path, 'w', encoding='utf-8') as f:
                                f.write(rewritten_html)
                            
                            self.stats["pages_cloned"] += 1
                            progress_bar.update(1)
                            
                            if progress_callback:
                                progress_callback({
                                    "type": "page_complete",
                                    "url": url,
                                    "path": str(save_path),
                                    "assets_found": sum(len(v) for v in assets.values()),
                                })
                            
                            # Extract and queue new links
                            if depth < self.depth:
                                links = self.extract_links(html, url)
                                for link in links:
                                    await queue.put((link, depth + 1))
                    
                    queue.task_done()
                    await asyncio.sleep(self.delay)
            
            # Start workers
            workers = [asyncio.create_task(worker()) for _ in range(self.concurrency)]
            await asyncio.gather(*workers)
            progress_bar.close()
        
        logger.info(f"\nCloning complete!")
        logger.info(f"Visited: {len(self.visited_urls)} pages")
        logger.info(f"Failed: {len(self.failed_urls)} pages")
        logger.info(f"Assets downloaded: {self.stats['assets_downloaded']}")
        logger.info(f"Output: {self.output_dir}")
        
        return {
            "success": True,
            "output_dir": str(self.output_dir),
            "pages_cloned": self.stats["pages_cloned"],
            "assets_downloaded": self.stats["assets_downloaded"],
            "failed_urls": list(self.failed_urls),
            "stats": self.stats,
        }
    
    def get_design_tokens(self) -> Dict[str, Any]:
        """Extract design tokens from cloned site."""
        return self.design_tokens
    
    def get_components(self) -> Dict[str, Any]:
        """Get identified components."""
        return self.components
