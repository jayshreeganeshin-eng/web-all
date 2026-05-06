"""
Visibility manager for handling different cloning modes.
Manages surface, deep, invisible, and shadow visibility modes.
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class VisibilityMode:
    """Visibility mode constants."""
    SURFACE = "surface"
    DEEP = "deep"
    INVISIBLE = "invisible"
    SHADOW = "shadow"


class VisibilityManager:
    """
    Manages different visibility modes for website cloning.
    
    Modes:
    - Surface: HTML/CSS/images only (fastest)
    - Deep: SPA, lazy-loaded modules, WebSocket-fed data
    - Invisible: Hidden endpoints, orphan pages, unlinked API routes
    - Shadow: JavaScript execution, all rendered variants (dark-mode, responsive, A/B tests)
    """
    
    def __init__(self, base_url: str, output_dir: str):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.current_mode: str = VisibilityMode.SURFACE
        self.discovered_urls: Dict[str, List[str]] = {
            VisibilityMode.SURFACE: [],
            VisibilityMode.DEEP: [],
            VisibilityMode.INVISIBLE: [],
            VisibilityMode.SHADOW: [],
        }
        self.cloner = None
        self.crawler = None
    
    def set_mode(self, mode: str):
        """Set the current visibility mode."""
        if mode not in [VisibilityMode.SURFACE, VisibilityMode.DEEP, 
                       VisibilityMode.INVISIBLE, VisibilityMode.SHADOW]:
            raise ValueError(f"Invalid mode: {mode}")
        
        self.current_mode = mode
        logger.info(f"Visibility mode set to: {mode}")
    
    async def execute_surface_clone(self, cloner, progress_callback=None) -> Dict[str, Any]:
        """
        Execute surface-level cloning.
        
        Features:
        - Static HTML/CSS/JS download
        - Image asset mirroring
        - Link rewriting
        - No JavaScript execution
        """
        logger.info("Executing surface clone...")
        result = await cloner.clone_site(progress_callback=progress_callback)
        self.discovered_urls[VisibilityMode.SURFACE] = list(cloner.visited_urls)
        return result
    
    async def execute_deep_clone(self, crawler, cloner, progress_callback=None) -> Dict[str, Any]:
        """
        Execute deep cloning for SPAs and dynamic content.
        
        Features:
        - JavaScript execution
        - Lazy-loaded content discovery
        - WebSocket traffic capture
        - Dynamic route discovery
        """
        logger.info("Executing deep clone...")
        
        # Initialize crawler for JS-heavy sites
        await crawler.start()
        
        try:
            # Navigate and capture dynamic content
            await crawler.navigate(self.base_url)
            
            # Scroll to load lazy content
            await crawler.scroll_to_bottom(iterations=5)
            
            # Click expandable elements
            await crawler.click_elements([
                'button[aria-expanded="false"]',
                '.load-more',
                'details > summary',
            ])
            
            # Capture rendered content
            content = await crawler.capture_content()
            
            # Save captured HTML
            output_file = self.output_dir / "deep_capture.html"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(content['html'], encoding='utf-8')
            
            # Export network requests as HAR
            har_file = self.output_dir / "network.har"
            await crawler.export_har(str(har_file))
            
            self.discovered_urls[VisibilityMode.DEEP] = [self.base_url]
            
            return {
                "success": True,
                "mode": VisibilityMode.DEEP,
                "output_file": str(output_file),
                "har_file": str(har_file),
                "images_found": len(content.get('images', [])),
                "links_found": len(content.get('links', [])),
                "network_requests": len(content.get('network_requests', [])),
            }
        
        finally:
            await crawler.close()
    
    async def execute_invisible_clone(self, crawler, progress_callback=None) -> Dict[str, Any]:
        """
        Execute invisible content discovery.
        
        Features:
        - Sitemap.xml parsing
        - robots.txt analysis
        - Common path guessing
        - Directory enumeration
        - Orphan page discovery
        """
        logger.info("Executing invisible clone...")
        
        from .crawler import AsyncCrawler
        
        discovered_urls = set()
        
        # Method 1: Parse sitemap.xml
        sitemap_urls = await self._discover_from_sitemap(crawler)
        discovered_urls.update(sitemap_urls)
        logger.info(f"Discovered {len(sitemap_urls)} URLs from sitemap")
        
        # Method 2: Try common paths
        common_paths = await self._discover_common_paths(crawler)
        discovered_urls.update(common_paths)
        logger.info(f"Discovered {len(common_paths)} URLs from common paths")
        
        # Method 3: Check robots.txt for hidden paths
        robots_urls = await self._discover_from_robots(crawler)
        discovered_urls.update(robots_urls)
        logger.info(f"Discovered {len(robots_urls)} URLs from robots.txt")
        
        self.discovered_urls[VisibilityMode.INVISIBLE] = list(discovered_urls)
        
        # Save discovered URLs
        urls_file = self.output_dir / "invisible_urls.txt"
        urls_file.parent.mkdir(parents=True, exist_ok=True)
        urls_file.write_text('\n'.join(sorted(discovered_urls)), encoding='utf-8')
        
        return {
            "success": True,
            "mode": VisibilityMode.INVISIBLE,
            "urls_discovered": len(discovered_urls),
            "urls_file": str(urls_file),
        }
    
    async def execute_shadow_clone(self, crawler, cloner, progress_callback=None) -> Dict[str, Any]:
        """
        Execute shadow cloning for all visual variants.
        
        Features:
        - Dark mode capture
        - Responsive breakpoint screenshots
        - A/B test variant discovery
        - State-based rendering capture
        """
        logger.info("Executing shadow clone...")
        
        await crawler.start()
        
        try:
            variants_captured = []
            
            # Normal view
            await crawler.navigate(self.base_url)
            normal_content = await crawler.capture_content()
            variants_captured.append({
                "variant": "normal",
                "url": self.base_url,
            })
            
            # Dark mode (if supported)
            await crawler.page.emulate_media({"colorScheme": "dark"})
            await crawler.navigate(self.base_url)
            dark_content = await crawler.capture_content()
            variants_captured.append({
                "variant": "dark",
                "url": self.base_url,
            })
            
            # Mobile viewport
            await crawler.page.set_viewport_size({"width": 375, "height": 667})
            await crawler.navigate(self.base_url)
            mobile_content = await crawler.capture_content()
            variants_captured.append({
                "variant": "mobile",
                "viewport": "375x667",
                "url": self.base_url,
            })
            
            # Tablet viewport
            await crawler.page.set_viewport_size({"width": 768, "height": 1024})
            await crawler.navigate(self.base_url)
            tablet_content = await crawler.capture_content()
            variants_captured.append({
                "variant": "tablet",
                "viewport": "768x1024",
                "url": self.base_url,
            })
            
            # Restore desktop viewport
            await crawler.page.set_viewport_size({"width": 1920, "height": 1080})
            
            # Save variants
            variants_dir = self.output_dir / "shadow_variants"
            variants_dir.mkdir(parents=True, exist_ok=True)
            
            for i, variant in enumerate(variants_captured):
                variant_file = variants_dir / f"variant_{i}_{variant['variant']}.html"
                
                if variant['variant'] == 'normal':
                    content = normal_content
                elif variant['variant'] == 'dark':
                    content = dark_content
                elif variant['variant'] == 'mobile':
                    content = mobile_content
                elif variant['variant'] == 'tablet':
                    content = tablet_content
                
                variant_file.write_text(content['html'], encoding='utf-8')
                variant['file'] = str(variant_file)
            
            self.discovered_urls[VisibilityMode.SHADOW] = [self.base_url]
            
            return {
                "success": True,
                "mode": VisibilityMode.SHADOW,
                "variants_captured": len(variants_captured),
                "variants": variants_captured,
                "output_dir": str(variants_dir),
            }
        
        finally:
            await crawler.close()
    
    async def _discover_from_sitemap(self, crawler) -> List[str]:
        """Discover URLs from sitemap.xml."""
        import xml.etree.ElementTree as ET
        from urllib.parse import urljoin, urlparse
        
        sitemap_url = urljoin(self.base_url, '/sitemap.xml')
        urls = []
        
        try:
            await crawler.navigate(sitemap_url)
            content = await crawler.page.content()
            
            try:
                root = ET.fromstring(content.encode('utf-8'))
                ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                
                for loc in root.findall('.//ns:loc', ns):
                    url = loc.text
                    if url:
                        urls.append(url)
            except ET.ParseError:
                pass
        
        except Exception as e:
            logger.warning(f"Error parsing sitemap: {e}")
        
        return urls
    
    async def _discover_common_paths(self, crawler) -> List[str]:
        """Discover URLs by trying common paths."""
        from urllib.parse import urljoin
        
        common_paths = [
            '/admin', '/wp-admin', '/login', '/signin',
            '/api', '/api/v1', '/graphql',
            '/blog', '/news', '/articles',
            '/products', '/services', '/about', '/contact',
            '/search', '/archive', '/sitemap.xml', '/robots.txt',
        ]
        
        discovered = []
        
        for path in common_paths:
            url = urljoin(self.base_url, path)
            try:
                response = await crawler.page.goto(url, timeout=5000)
                if response and response.status == 200:
                    discovered.append(url)
            except:
                pass
        
        return discovered
    
    async def _discover_from_robots(self, crawler) -> List[str]:
        """Discover disallowed paths from robots.txt."""
        from urllib.parse import urljoin
        
        robots_url = urljoin(self.base_url, '/robots.txt')
        urls = []
        
        try:
            await crawler.navigate(robots_url)
            content = await crawler.page.content()
            
            for line in content.split('\n'):
                if line.strip().startswith('Disallow:'):
                    path = line.split(':', 1)[1].strip()
                    if path and path != '/':
                        url = urljoin(self.base_url, path)
                        urls.append(url)
        
        except Exception as e:
            logger.warning(f"Error parsing robots.txt: {e}")
        
        return urls
    
    async def run_all_modes(self, cloner, crawler, progress_callback=None) -> Dict[str, Any]:
        """Run all visibility modes sequentially."""
        results = {}
        
        # Surface
        self.set_mode(VisibilityMode.SURFACE)
        results[VisibilityMode.SURFACE] = await self.execute_surface_clone(
            cloner, progress_callback
        )
        
        # Deep
        self.set_mode(VisibilityMode.DEEP)
        results[VisibilityMode.DEEP] = await self.execute_deep_clone(
            crawler, cloner, progress_callback
        )
        
        # Invisible
        self.set_mode(VisibilityMode.INVISIBLE)
        results[VisibilityMode.INVISIBLE] = await self.execute_invisible_clone(
            crawler, progress_callback
        )
        
        # Shadow
        self.set_mode(VisibilityMode.SHADOW)
        results[VisibilityMode.SHADOW] = await self.execute_shadow_clone(
            crawler, cloner, progress_callback
        )
        
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all discovered URLs by mode."""
        return {
            mode: len(urls) for mode, urls in self.discovered_urls.items()
        }
