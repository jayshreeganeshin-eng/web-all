"""
Universal File Downloader - Download all types of files from the internet.
Supports: documents, archives, media, executables, datasets, and more.
"""

import asyncio
import os
import re
import json
import mimetypes
from pathlib import Path
from typing import Optional, Set, Dict, List, Any
from urllib.parse import urlparse, urljoin, parse_qs
import aiohttp
from bs4 import BeautifulSoup
from tqdm import tqdm
import hashlib


class UniversalFileDownloader:
    """Download any type of file from websites."""
    
    # File categories with extensions
    FILE_CATEGORIES = {
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx', '.md'],
        'archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.pkg', '.dmg'],
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff', '.raw'],
        'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
        'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
        'code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.php', '.rb', '.go', '.rs'],
        'data': ['.json', '.xml', '.csv', '.yaml', '.yml', '.sql', '.db', '.sqlite'],
        'executables': ['.exe', '.msi', '.app', '.bin', '.sh', '.bat', '.cmd'],
        'fonts': ['.ttf', '.otf', '.woff', '.woff2', '.eot'],
        'other': []
    }
    
    def __init__(
        self,
        base_url: str,
        output_dir: str,
        depth: int = 3,
        concurrency: int = 10,
        delay: float = 0.5,
        file_types: Optional[List[str]] = None,  # None = all types
        max_file_size: int = 100 * 1024 * 1024,  # 100MB default
        organize_by_type: bool = True,
        user_agent: Optional[str] = None,
    ):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.depth = depth
        self.concurrency = concurrency
        self.delay = delay
        self.file_types = file_types
        self.max_file_size = max_file_size
        self.organize_by_type = organize_by_type
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        self.visited_urls: Set[str] = set()
        self.downloaded_files: List[Dict] = []
        self.failed_downloads: List[str] = []
        self.domain = urlparse(base_url).netloc
        
    def get_file_category(self, filename: str) -> str:
        """Determine file category from extension."""
        ext = Path(filename).suffix.lower()
        for category, extensions in self.FILE_CATEGORIES.items():
            if ext in extensions:
                return category
        return 'other'
    
    def should_download(self, url: str) -> bool:
        """Check if URL should be downloaded based on file type filters."""
        if not self.file_types:
            return True
            
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # Check if URL matches any requested file type
        for ft in self.file_types:
            if ft.lower() in path or f".{ft.lower()}" in path:
                return True
                
        return False
    
    async def download_file(
        self, 
        session: aiohttp.ClientSession, 
        url: str, 
        save_path: Path,
        progress_bar: Optional[tqdm] = None
    ) -> bool:
        """Download a single file with progress tracking."""
        headers = {"User-Agent": self.user_agent}
        
        try:
            async with session.get(url, headers=headers, timeout=60) as response:
                if response.status != 200:
                    self.failed_downloads.append(url)
                    return False
                    
                # Check file size
                content_length = response.headers.get('Content-Length')
                if content_length and int(content_length) > self.max_file_size:
                    print(f"Skipping {url}: File too large ({content_length} bytes)")
                    return False
                
                save_path.parent.mkdir(parents=True, exist_ok=True)
                
                downloaded = 0
                with open(save_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_bar and progress_bar.total is not None:
                            progress_bar.update(len(chunk))
                
                # Record successful download
                file_info = {
                    'url': url,
                    'path': str(save_path),
                    'size': downloaded,
                    'category': self.get_file_category(save_path.name),
                    'hash': hashlib.md5(save_path.read_bytes()).hexdigest()
                }
                self.downloaded_files.append(file_info)
                
                return True
                
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            self.failed_downloads.append(url)
            return False
    
    def extract_file_links(self, html: str, base_url: str) -> List[str]:
        """Extract all file links from HTML."""
        soup = BeautifulSoup(html, 'lxml')
        file_links = []
        
        # Common file attributes
        file_attrs = ['href', 'src', 'data-src', 'data-url']
        
        for tag in soup.find_all(True):  # All tags
            for attr in file_attrs:
                value = tag.get(attr)
                if value:
                    absolute_url = urljoin(base_url, value)
                    
                    # Check if it looks like a file
                    parsed = urlparse(absolute_url)
                    path = parsed.path
                    
                    # Skip data URLs and javascript
                    if path.startswith(('data:', 'javascript:')):
                        continue
                    
                    # Check if it has a file extension or looks like a download
                    if '.' in path.split('/')[-1] or 'download' in path.lower():
                        if self.should_download(absolute_url):
                            file_links.append(absolute_url)
        
        return file_links
    
    async def crawl_and_download(self):
        """Crawl website and download all files."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        semaphore = asyncio.Semaphore(self.concurrency)
        stats = {'pages': 0, 'files': 0, 'bytes': 0}
        
        async with aiohttp.ClientSession() as session:
            queue = asyncio.Queue()
            await queue.put((self.base_url, 0))  # URL, depth
            
            progress_bar = tqdm(desc="Downloading Files", unit="B", unit_scale=True, total=None)
            
            async def worker():
                while True:
                    try:
                        url, depth = await asyncio.wait_for(queue.get(), timeout=5.0)
                    except asyncio.TimeoutError:
                        break
                    
                    async with semaphore:
                        normalized = url.split('#')[0]  # Remove fragment
                        
                        if normalized in self.visited_urls or depth > self.depth:
                            queue.task_done()
                            continue
                        
                        self.visited_urls.add(normalized)
                        
                        # Fetch page
                        try:
                            async with session.get(url, headers={"User-Agent": self.user_agent}, timeout=30) as response:
                                if response.status == 200:
                                    content_type = response.headers.get('Content-Type', '')
                                    
                                    # Check if it's a file or HTML
                                    if 'text/html' in content_type or depth == 0:
                                        html = await response.text()
                                        stats['pages'] += 1
                                        
                                        # Extract file links
                                        file_links = self.extract_file_links(html, url)
                                        
                                        # Download files
                                        for file_url in file_links:
                                            parsed = urlparse(file_url)
                                            filename = Path(parsed.path).name or 'file'
                                            
                                            if self.organize_by_type:
                                                category = self.get_file_category(filename)
                                                save_path = self.output_dir / category / filename
                                            else:
                                                save_path = self.output_dir / filename
                                            
                                            success = await self.download_file(
                                                session, file_url, save_path, None  # Don't use progress bar for individual files
                                            )
                                            if success:
                                                stats['files'] += 1
                                                if save_path.exists():
                                                    stats['bytes'] += save_path.stat().st_size
                                        
                                        # Queue more pages
                                        if depth < self.depth:
                                            soup = BeautifulSoup(html, 'lxml')
                                            for link in soup.find_all('a', href=True):
                                                href = link['href']
                                                next_url = urljoin(url, href)
                                                
                                                # Only queue HTML pages from same domain
                                                if urlparse(next_url).netloc == self.domain:
                                                    if not any(ext in next_url.lower() for ext in 
                                                              ['.pdf', '.zip', '.jpg', '.png']):
                                                        await queue.put((next_url, depth + 1))
                                    
                                    else:
                                        # It's a direct file
                                        parsed = urlparse(url)
                                        filename = Path(parsed.path).name or 'file'
                                        
                                        if self.organize_by_type:
                                            category = self.get_file_category(filename)
                                            save_path = self.output_dir / category / filename
                                        else:
                                            save_path = self.output_dir / filename
                                        
                                        success = await self.download_file(
                                            session, url, save_path, None  # Don't use progress bar for individual files
                                        )
                                        if success:
                                            stats['files'] += 1
                                            if save_path.exists():
                                                stats['bytes'] += save_path.stat().st_size
                                                
                        except Exception as e:
                            print(f"Error processing {url}: {e}")
                        
                        queue.task_done()
                        await asyncio.sleep(self.delay)
            
            # Start workers
            workers = [asyncio.create_task(worker()) for _ in range(self.concurrency)]
            await asyncio.gather(*workers)
            progress_bar.close()
        
        # Save download manifest
        manifest = {
            'base_url': self.base_url,
            'total_files': len(self.downloaded_files),
            'total_bytes': stats['bytes'],
            'failed_count': len(self.failed_downloads),
            'files': self.downloaded_files,
            'failed_urls': self.failed_downloads,
        }
        
        manifest_path = self.output_dir / 'download_manifest.json'
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"\n{'='*60}")
        print(f"Download Complete!")
        print(f"{'='*60}")
        print(f"Pages crawled: {stats['pages']}")
        print(f"Files downloaded: {stats['files']}")
        print(f"Total size: {stats['bytes'] / (1024*1024):.2f} MB")
        print(f"Failed downloads: {len(self.failed_downloads)}")
        print(f"Output directory: {self.output_dir}")
        print(f"Manifest saved to: {manifest_path}")
        
        # Print summary by category
        if self.organize_by_type:
            print(f"\n{'='*60}")
            print("Files by Category:")
            print(f"{'='*60}")
            categories = {}
            for file_info in self.downloaded_files:
                cat = file_info['category']
                categories[cat] = categories.get(cat, 0) + 1
            
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"  {cat}: {count} files")
        
        return stats


class InternetArchiveDownloader:
    """Download from Internet Archive (archive.org)."""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.base_api = "https://archive.org/advancedsearch.php"
    
    async def search_and_download(
        self,
        query: str,
        fields: Optional[List[str]] = None,
        limit: int = 100,
        file_types: Optional[List[str]] = None,
    ):
        """Search archive.org and download matching items."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if not fields:
            fields = ['identifier', 'title', 'downloads']
        
        params = {
            'q': query,
            'fl': ','.join(fields),
            'rows': limit,
            'output': 'json',
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_api, params=params) as response:
                data = await response.json()
                
                if 'response' not in data:
                    print("No results found")
                    return []
                
                items = data['response']['docs']
                print(f"Found {len(items)} items")
                
                downloaded = []
                for item in tqdm(items, desc="Downloading from Archive"):
                    identifier = item.get('identifier')
                    if not identifier:
                        continue
                    
                    # Get item details
                    metadata_url = f"https://archive.org/metadata/{identifier}"
                    async with session.get(metadata_url) as meta_response:
                        meta_data = await meta_response.json()
                        
                        if 'files' not in meta_data:
                            continue
                        
                        # Download files
                        for file_info in meta_data['files']:
                            filename = file_info.get('name', '')
                            
                            # Filter by file type if specified
                            if file_types:
                                if not any(filename.endswith(ft) for ft in file_types):
                                    continue
                            
                            file_url = f"https://archive.org/download/{identifier}/{filename}"
                            save_path = self.output_dir / identifier / filename
                            
                            try:
                                async with session.get(file_url) as file_response:
                                    if file_response.status == 200:
                                        save_path.parent.mkdir(parents=True, exist_ok=True)
                                        with open(save_path, 'wb') as f:
                                            f.write(await file_response.read())
                                        downloaded.append(str(save_path))
                            except Exception as e:
                                print(f"Failed to download {filename}: {e}")
                
                return downloaded


async def test_universal_downloader():
    """Test the universal file downloader."""
    print("Testing Universal File Downloader...")
    
    downloader = UniversalFileDownloader(
        base_url="https://example.com",
        output_dir="./test_downloads",
        depth=2,
        concurrency=5,
    )
    
    stats = await downloader.crawl_and_download()
    print(f"Test complete! Downloaded {stats['files']} files")


if __name__ == '__main__':
    asyncio.run(test_universal_downloader())
