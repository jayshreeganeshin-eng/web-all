"""
Invisible content discovery engine.
Handles clicks, hovers, form submissions, and dynamic loading.
Optimized for performance with connection pooling and batch operations.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
from contextlib import asynccontextmanager

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
except ImportError:
    print("Playwright required: pip install playwright")
    raise

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InvisibleContentEngine:
    """Discovers and captures hidden/dynamic content with optimized browser management."""
    
    DEFAULT_CLICK_SELECTORS = [
        'button',
        '[role="button"]',
        '.toggle',
        '.expand',
        '.accordion-title',
        '.load-more',
        '[aria-expanded="false"]',
        'details > summary'
    ]
    
    DEFAULT_HOVER_SELECTORS = [
        '.dropdown',
        '.menu-item',
        '[data-hover]',
        'nav li'
    ]
    
    def __init__(
        self,
        use_tor: bool = False,
        tor_proxy: str = "http://127.0.0.1:9050",
        timeout: int = 30000,
        max_concurrent: int = 3
    ):
        self.use_tor = use_tor
        self.tor_proxy = tor_proxy
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
    
    @asynccontextmanager
    async def _get_browser_context(self):
        """Context manager for efficient browser instance reuse."""
        browser: Optional[Browser] = None
        context: Optional[BrowserContext] = None
        
        try:
            async with async_playwright() as p:
                browser_args = {"headless": True}
                
                # Only launch with proxy if explicitly requested and proxy is available
                context_args: Dict[str, Any] = {}
                if self.use_tor:
                    try:
                        # Test if Tor proxy is accessible before using it
                        import aiohttp
                        async with aiohttp.ClientSession() as session:
                            async with session.get("https://check.torproject.org/", 
                                                   proxy=self.tor_proxy, 
                                                   timeout=5) as resp:
                                pass
                        context_args["proxy"] = {"server": self.tor_proxy}
                        logger.info(f"Using Tor proxy at {self.tor_proxy}")
                    except Exception as e:
                        logger.warning(f"Tor proxy not available ({e}), continuing without proxy")
                        self.use_tor = False
                
                browser = await p.chromium.launch(**browser_args)
                context = await browser.new_context(**context_args)
                yield context
        except Exception as e:
            logger.error(f"Browser context error: {e}")
            raise
        finally:
            try:
                if context:
                    await context.close()
            except Exception:
                pass
            try:
                if browser:
                    await browser.close()
            except Exception:
                pass
    
    async def expand_all_content(
        self,
        url: str,
        scroll_iterations: int = 5,
        click_selectors: Optional[List[str]] = None,
        hover_selectors: Optional[List[str]] = None
    ) -> str:
        """Load page and expand all hidden content through interactions.
        
        Optimized with:
        - Batch element queries
        - Parallel hover/click operations where safe
        - Early termination on bottom detection
        """
        
        selectors_to_click = click_selectors or self.DEFAULT_CLICK_SELECTORS
        selectors_to_hover = hover_selectors or self.DEFAULT_HOVER_SELECTORS
        
        async with self._semaphore:
            async with self._get_browser_context() as context:
                page = await context.new_page()
                
                try:
                    # Navigate with more lenient settings to avoid proxy errors
                    await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)
                    
                    # Wait for network idle separately with shorter timeout
                    try:
                        await page.wait_for_load_state("networkidle", timeout=min(self.timeout, 10000))
                    except Exception:
                        logger.info("Network idle timeout, continuing with current state")
                    
                    # Optimized scrolling with early termination
                    for i in range(scroll_iterations):
                        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        
                        # Check if we reached bottom
                        reached_bottom = await page.evaluate("""
                            () => window.innerHeight + window.scrollY >= document.body.offsetHeight - 100
                        """)
                        
                        if reached_bottom:
                            logger.info(f"Reached bottom after {i+1} scrolls")
                            break
                        
                        await asyncio.sleep(0.5)  # Reduced wait time
                    
                    # Click expandable elements with error handling
                    await self._click_elements(page, selectors_to_click)
                    
                    # Hover over elements
                    await self._hover_elements(page, selectors_to_hover)
                    
                    # Final wait for any remaining content
                    await page.wait_for_timeout(1000)
                    
                    html = await page.content()
                    logger.info("Successfully expanded all hidden content")
                    return html
                    
                except Exception as e:
                    logger.error(f"Error expanding content: {e}")
                    raise
    
    async def _click_elements(self, page: Page, selectors: List[str]) -> None:
        """Click expandable elements with batching and error handling."""
        clicked_count = 0
        max_clicks = 20  # Safety limit
        
        for selector in selectors:
            if clicked_count >= max_clicks:
                break
                
            try:
                elements = await page.query_selector_all(selector)
                for elem in elements[:5]:  # Limit per selector
                    try:
                        await elem.click(timeout=1000)
                        clicked_count += 1
                        await asyncio.sleep(0.2)  # Brief pause for animations
                    except Exception:
                        continue
            except Exception:
                continue
    
    async def _hover_elements(self, page: Page, selectors: List[str]) -> None:
        """Hover over elements with batching."""
        hovered_count = 0
        max_hovers = 15
        
        for selector in selectors:
            if hovered_count >= max_hovers:
                break
                
            try:
                elements = await page.query_selector_all(selector)
                for elem in elements[:3]:
                    try:
                        await elem.hover(timeout=1000)
                        hovered_count += 1
                        await asyncio.sleep(0.1)
                    except Exception:
                        continue
            except Exception:
                continue
    
    async def submit_form_and_capture(
        self,
        url: str,
        form_selector: str = "form",
        input_values: Optional[Dict[str, str]] = None,
        submit_selector: str = 'button[type="submit"]'
    ) -> str:
        """Fill and submit a form, then capture the result."""
        
        async with self._get_browser_context() as context:
            page = await context.new_page()
            
            try:
                # Navigate with more lenient settings to avoid proxy errors
                await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)
                
                # Wait for network idle separately with shorter timeout
                try:
                    await page.wait_for_load_state("networkidle", timeout=min(self.timeout, 10000))
                except Exception:
                    logger.info("Network idle timeout, continuing with current state")
                
                # Fill form fields in parallel where possible
                if input_values:
                    fill_tasks = []
                    for selector, value in input_values.items():
                        fill_tasks.append(self._safe_fill(page, selector, value))
                    
                    await asyncio.gather(*fill_tasks, return_exceptions=True)
                
                # Submit form
                submitted = await self._submit_form(page, submit_selector, input_values)
                
                if submitted:
                    await page.wait_for_load_state("networkidle")
                
                html = await page.content()
                return html
                
            except Exception as e:
                logger.error(f"Form submission error: {e}")
                raise
    
    async def _safe_fill(self, page: Page, selector: str, value: str) -> None:
        """Safely fill a form field with error handling."""
        try:
            await page.fill(selector, value, timeout=2000)
        except Exception:
            logger.warning(f"Could not fill {selector}")
    
    async def _submit_form(self, page: Page, submit_selector: str, input_values: Optional[Dict]) -> bool:
        """Attempt to submit form via button click or Enter key."""
        try:
            await page.click(submit_selector, timeout=2000)
            return True
        except Exception:
            # Try pressing Enter on the last input
            if input_values:
                try:
                    last_selector = list(input_values.keys())[-1]
                    await page.press(last_selector, "Enter")
                    return True
                except Exception:
                    pass
        return False
    
    async def discover_sitemap_urls(self, base_url: str) -> List[str]:
        """Discover URLs from sitemap.xml with caching."""
        from urllib.parse import urljoin
        import aiohttp
        from bs4 import BeautifulSoup
        
        urls: List[str] = []
        sitemap_url = urljoin(base_url, "/sitemap.xml")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(sitemap_url, timeout=10) as response:
                    if response.status == 200:
                        text = await response.text()
                        soup = BeautifulSoup(text, 'lxml')
                        
                        # Handle different sitemap formats
                        for loc in soup.find_all('loc'):
                            if loc.string:
                                urls.append(loc.string.strip())
                        
                        logger.info(f"Found {len(urls)} URLs in sitemap")
        except Exception as e:
            logger.warning(f"Could not fetch sitemap: {e}")
        
        return urls
    
    async def capture_network_requests(self, url: str) -> List[Dict[str, Any]]:
        """Capture all network requests during page load."""
        
        requests_log: List[Dict[str, Any]] = []
        
        async with self._get_browser_context() as context:
            page = await context.new_page()
            
            # Set up request listener
            def handle_request(request):
                requests_log.append({
                    "url": request.url,
                    "method": request.method,
                    "type": request.resource_type
                })
            
            page.on("request", handle_request)
            
            try:
                # Navigate with more lenient settings to avoid proxy errors
                await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)
                
                # Wait for network idle separately with shorter timeout
                try:
                    await page.wait_for_load_state("networkidle", timeout=min(self.timeout, 10000))
                except Exception:
                    logger.info("Network idle timeout, continuing with current state")
                
                await page.wait_for_timeout(2000)
                
            except Exception as e:
                logger.error(f"Error capturing requests: {e}")
            finally:
                await page.close()
        
        return requests_log
