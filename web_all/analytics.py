"""
Analytics and reporting for web-all.
Generates statistics, reports, and insights about cloned websites.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from urllib.parse import urlparse


@dataclass
class PageStats:
    """Statistics for a single page."""
    url: str
    title: str = ""
    size_bytes: int = 0
    load_time_ms: int = 0
    images_count: int = 0
    links_count: int = 0
    text_length: int = 0
    status_code: int = 200
    
    
@dataclass
class SiteReport:
    """Complete report for a cloned site."""
    base_url: str
    clone_date: str
    total_pages: int = 0
    total_size_bytes: int = 0
    total_images: int = 0
    total_links: int = 0
    failed_urls: List[str] = None
    pages: List[PageStats] = None
    domains: Dict[str, int] = None
    content_types: Dict[str, int] = None
    
    def __post_init__(self):
        if self.failed_urls is None:
            self.failed_urls = []
        if self.pages is None:
            self.pages = []
        if self.domains is None:
            self.domains = {}
        if self.content_types is None:
            self.content_types = {}


class AnalyticsEngine:
    """Analyze cloned websites and generate reports."""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.pages: List[PageStats] = []
        self.failed_urls: List[str] = []
        
    def add_page(self, stats: PageStats) -> None:
        """Add page statistics."""
        self.pages.append(stats)
        
    def add_failed_url(self, url: str) -> None:
        """Track failed URL."""
        self.failed_urls.append(url)
        
    def analyze_site(self, base_url: str) -> SiteReport:
        """Generate complete site analysis."""
        total_size = sum(p.size_bytes for p in self.pages)
        total_images = sum(p.images_count for p in self.pages)
        total_links = sum(p.links_count for p in self.pages)
        
        # Analyze domains
        domains = {}
        for page in self.pages:
            domain = urlparse(page.url).netloc
            domains[domain] = domains.get(domain, 0) + 1
            
        # Analyze content types (simplified)
        content_types = {}
        for page in self.pages:
            ext = Path(urlparse(page.url).path).suffix or '.html'
            content_types[ext] = content_types.get(ext, 0) + 1
            
        report = SiteReport(
            base_url=base_url,
            clone_date=datetime.now().isoformat(),
            total_pages=len(self.pages),
            total_size_bytes=total_size,
            total_images=total_images,
            total_links=total_links,
            failed_urls=self.failed_urls.copy(),
            pages=self.pages.copy(),
            domains=domains,
            content_types=content_types,
        )
        
        return report
        
    def save_report(self, report: SiteReport, output_file: Optional[str] = None) -> str:
        """Save report to JSON file."""
        if output_file is None:
            output_file = str(self.output_dir / "site_report.json")
            
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict for JSON serialization
        data = asdict(report)
        output_path.write_text(json.dumps(data, indent=2), encoding='utf-8')
        
        return str(output_path)
        
    def print_summary(self, report: SiteReport) -> None:
        """Print human-readable summary."""
        print("\n" + "="*60)
        print("📊 SITE CLONE REPORT")
        print("="*60)
        print(f"Base URL: {report.base_url}")
        print(f"Clone Date: {report.clone_date}")
        print("-"*60)
        print(f"Total Pages: {report.total_pages:,}")
        print(f"Total Size: {self._format_size(report.total_size_bytes)}")
        print(f"Total Images: {report.total_images:,}")
        print(f"Total Links: {report.total_links:,}")
        print(f"Failed URLs: {len(report.failed_urls)}")
        
        if report.domains:
            print("\n📁 Domains:")
            for domain, count in sorted(report.domains.items(), key=lambda x: -x[1])[:10]:
                print(f"  {domain}: {count} pages")
                
        if report.content_types:
            print("\n📄 Content Types:")
            for ext, count in sorted(report.content_types.items(), key=lambda x: -x[1])[:10]:
                print(f"  {ext}: {count} files")
                
        if report.failed_urls:
            print("\n❌ Failed URLs:")
            for url in report.failed_urls[:10]:
                print(f"  {url}")
            if len(report.failed_urls) > 10:
                print(f"  ... and {len(report.failed_urls) - 10} more")
                
        print("="*60 + "\n")
        
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format bytes to human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"


class PerformanceMonitor:
    """Monitor and track performance metrics."""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {
            'requests': 0,
            'successful': 0,
            'failed': 0,
            'total_time_ms': 0,
            'start_time': None,
            'end_time': None,
        }
        
    def start(self) -> None:
        """Start monitoring."""
        self.metrics['start_time'] = datetime.now()
        
    def stop(self) -> None:
        """Stop monitoring."""
        self.metrics['end_time'] = datetime.now()
        
    def record_request(self, success: bool, time_ms: int) -> None:
        """Record a single request."""
        self.metrics['requests'] += 1
        if success:
            self.metrics['successful'] += 1
        else:
            self.metrics['failed'] += 1
        self.metrics['total_time_ms'] += time_ms
        
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if self.metrics['requests'] == 0:
            return self.metrics
            
        duration = None
        if self.metrics['start_time'] and self.metrics['end_time']:
            duration = (self.metrics['end_time'] - self.metrics['start_time']).total_seconds()
            
        return {
            **self.metrics,
            'duration_seconds': duration,
            'avg_time_per_request_ms': self.metrics['total_time_ms'] / self.metrics['requests'],
            'success_rate': self.metrics['successful'] / self.metrics['requests'] * 100,
            'requests_per_second': self.metrics['requests'] / duration if duration else 0,
        }
        
    def print_stats(self) -> None:
        """Print performance statistics."""
        stats = self.get_stats()
        print("\n⚡ PERFORMANCE STATISTICS")
        print("-"*40)
        print(f"Total Requests: {stats['requests']}")
        print(f"Successful: {stats['successful']}")
        print(f"Failed: {stats['failed']}")
        print(f"Success Rate: {stats['success_rate']:.1f}%")
        if stats['duration_seconds']:
            print(f"Duration: {stats['duration_seconds']:.2f}s")
            print(f"Requests/sec: {stats['requests_per_second']:.2f}")
            print(f"Avg Time/Request: {stats['avg_time_per_request_ms']:.0f}ms")
        print()
