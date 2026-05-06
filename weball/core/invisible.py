"""
Invisible content discovery engine.
Handles clicks, hovers, form submissions, and dynamic loading.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Playwright required: pip install playwright")
    raise

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InvisibleContentEngine:
    """Discovers and captures hidden/dynamic content."""
    
    def __init__(
        self,
        use_tor: bool = False,
        tor_proxy: str = "http://127.0.0.1:9050",
        timeout: int = 30000
    ):
        self.use_tor = use_tor
        self.tor_proxy = tor_proxy
        self.timeout = timeout
        
    async def expand_all_content(
        self,
        url: str,
        scroll_iterations: int = 5,
        click_selectors: Optional[List[str]] = None,
        hover_selectors: Optional[List[str]] = None
    ) -> str:
        """Load page and expand all hidden content through interactions."""
        
        if click_selectors is None:
            click_selectors = [
                'button',
                '[role="button"]',
                '.toggle',
                '.expand',
                '.accordion-title',
                '.load-more',
                '[aria-expanded="false"]',
                'details > summary'
            ]
        
        if hover_selectors is None:
            hover_selectors = [
                '.dropdown',
                '.menu-item',
                '[data-hover]',
                'nav li'
            ]
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            context_args = {}
            if self.use_tor:
                context_args["proxy"] = {"server": self.tor_proxy}
            
            context = await browser.new_context(**context_args)
            page = await context.new_page()
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=self.timeout)
                
                # Scroll multiple times
                for i in range(scroll_iterations):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(1)
                    
                    # Check if we reached bottom
                    reached_bottom = await page.evaluate("""
                        () => {
                            const scrolled = window.innerHeight + window.scrollY >= document.body.offsetHeight;
                            return scrolled;
                        }
                    """)
                    
                    if reached_bottom:
                        logger.info(f"Reached bottom after {i+1} scrolls")
                        break
                
                # Click expandable elements
                for selector in click_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        for elem in elements[:10]:  # Limit clicks
                            await elem.click(timeout=2000)
                            await asyncio.sleep(0.5)
                    except Exception:
                        continue
                
                # Hover over elements
                for selector in hover_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        for elem in elements[:5]:
                            await elem.hover(timeout=2000)
                            await asyncio.sleep(0.3)
                    except Exception:
                        continue
                
                # Final wait for any remaining content
                await page.wait_for_timeout(2000)
                
                html = await page.content()
                logger.info("Successfully expanded all hidden content")
                return html
                
            finally:
                await browser.close()
    
    async def submit_form_and_capture(
        self,
        url: str,
        form_selector: str = "form",
        input_values: Optional[Dict[str, str]] = None,
        submit_selector: str = 'button[type="submit"]'
    ) -> str:
        """Fill and submit a form, then capture the result."""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=self.timeout)
                
                # Fill form fields
                if input_values:
                    for selector, value in input_values.items():
                        try:
                            await page.fill(selector, value)
                        except Exception:
                            logger.warning(f"Could not fill {selector}")
                
                # Submit form
                try:
                    await page.click(submit_selector)
                    await page.wait_for_load_state("networkidle")
                except Exception:
                    # Try pressing Enter on the last input
                    if input_values:
                        last_selector = list(input_values.keys())[-1]
                        await page.press(last_selector, "Enter")
                        await page.wait_for_load_state("networkidle")
                
                html = await page.content()
                return html
                
            finally:
                await browser.close()
    
    async def discover_sitemap_urls(self, base_url: str) -> List[str]:
        """Discover URLs from sitemap.xml."""
        from urllib.parse import urljoin
        import requests
        from bs4 import BeautifulSoup
        
        urls = []
        sitemap_url = urljoin(base_url, "/sitemap.xml")
        
        try:
            response = requests.get(sitemap_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                
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
        
        requests_log = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            # Set up request listener
            page.on("request", lambda req: requests_log.append({
                "url": req.url,
                "method": req.method,
                "type": req.resource_type
            }))
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=self.timeout)
                await page.wait_for_timeout(3000)  # Extra wait
                
            finally:
                await browser.close()
        
        return requests_log
