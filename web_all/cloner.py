"""
Core cloner engine for web-all.
Handles full website mirroring with asset downloading and link rewriting.
"""

import asyncio
import os
import re
from pathlib import Path
from typing import Optional, Set, Dict, List
from urllib.parse import urlparse, urljoin, urlunparse
import aiohttp
from bs4 import BeautifulSoup
import cssutils
from tqdm import tqdm

class WebsiteCloner:
    """Main cloning engine that downloads entire websites."""
    
    def __init__(
        self,
        base_url: str,
        output_dir: str,
        depth: int = 5,
        concurrency: int = 5,
        delay: float = 1.0,
        user_agent: Optional[str] = None,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        respect_robots: bool = True,
    ):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.depth = depth
        self.concurrency = concurrency
        self.delay = delay
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.include_patterns = include_patterns
        self.exclude_patterns = exclude_patterns
        self.respect_robots = respect_robots
        
        self.visited_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self.domain = urlparse(base_url).netloc
        
    def normalize_url(self, url: str) -> str:
        """Normalize URL for deduplication."""
        parsed = urlparse(url)
        # Remove fragment, normalize trailing slash
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
                
        return True
    
    async def fetch_page(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """Fetch a single page."""
        headers = {"User-Agent": self.user_agent}
        try:
            async with session.get(url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    self.failed_urls.add(url)
                    return None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            self.failed_urls.add(url)
            return None
    
    def extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract all links from HTML."""
        soup = BeautifulSoup(html, 'lxml')
        links = []
        
        for tag in soup.find_all(['a', 'link', 'script'], href=True):
            href = tag.get('href') or tag.get('src')
            if href:
                absolute_url = urljoin(base_url, href)
                links.append(absolute_url)
                
        return links
    
    def rewrite_links(self, html: str, base_url: str, current_path: str) -> str:
        """Rewrite absolute links to relative paths."""
        soup = BeautifulSoup(html, 'lxml')
        
        # Rewrite href attributes
        for tag in soup.find_all(['a', 'link'], href=True):
            href = tag['href']
            if href.startswith(('http://', 'https://')):
                if urlparse(href).netloc == self.domain:
                    # Convert to relative path
                    rel_path = self._url_to_path(href, base_url)
                    tag['href'] = rel_path
                    
        # Rewrite src attributes
        for tag in soup.find_all(['img', 'script'], src=True):
            src = tag['src']
            if src.startswith(('http://', 'https://')):
                if urlparse(src).netloc == self.domain:
                    rel_path = self._url_to_path(src, base_url)
                    tag['src'] = rel_path
                    
        return str(soup)
    
    def _url_to_path(self, url: str, base_url: str) -> str:
        """Convert URL to local file path."""
        parsed = urlparse(url)
        path = parsed.path.lstrip('/')
        if not path:
            path = 'index.html'
        return path
    
    async def download_asset(self, session: aiohttp.ClientSession, url: str, save_path: Path):
        """Download a single asset (image, CSS, JS, etc.)."""
        headers = {"User-Agent": self.user_agent}
        try:
            async with session.get(url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(save_path, 'wb') as f:
                        f.write(await response.read())
        except Exception as e:
            print(f"Error downloading {url}: {e}")
    
    async def clone_site(self):
        """Main cloning method."""
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
                            
                            # Rewrite links
                            rewritten_html = self.rewrite_links(html, self.base_url, path)
                            
                            save_path.parent.mkdir(parents=True, exist_ok=True)
                            with open(save_path, 'w', encoding='utf-8') as f:
                                f.write(rewritten_html)
                                
                            progress_bar.update(1)
                            
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
            
        print(f"\nCloning complete!")
        print(f"Visited: {len(self.visited_urls)} pages")
        print(f"Failed: {len(self.failed_urls)} pages")
        print(f"Output: {self.output_dir}")
