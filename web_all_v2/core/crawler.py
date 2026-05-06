"""
Async crawler with Playwright for JavaScript-heavy sites.
Handles infinite scroll, SPAs, and dynamic content loading.
"""

import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from urllib.parse import urlparse
from playwright.async_api import async_playwright, Page, Browser
import logging

logger = logging.getLogger(__name__)


class AsyncCrawler:
    """
    Advanced crawler using Playwright for JavaScript-rendered content.
    
    Features:
    - Infinite scroll handling
    - Dynamic content loading
    - Network request interception
    - Screenshot capture
    - HAR export
    """
    
    def __init__(
        self,
        base_url: str,
        headless: bool = True,
        stealth_mode: bool = True,
        viewport: Optional[Dict[str, int]] = None,
        user_agent: Optional[str] = None,
        proxy: Optional[str] = None,
    ):
        self.base_url = base_url
        self.headless = headless
        self.stealth_mode = stealth_mode
        self.viewport = viewport or {"width": 1920, "height": 1080}
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.proxy = proxy
        
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.network_requests: List[Dict[str, Any]] = []
        self.console_logs: List[str] = []
    
    async def start(self):
        """Initialize browser and page."""
        playwright = await async_playwright().start()
        
        browser_args = {
            "headless": self.headless,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ]
        }
        
        if self.proxy:
            browser_args["proxy"] = {"server": self.proxy}
        
        self.browser = await playwright.chromium.launch(**browser_args)
        
        context = await self.browser.new_context(
            viewport=self.viewport,
            user_agent=self.user_agent,
            device_scale_factor=1,
        )
        
        self.page = await context.new_page()
        
        # Inject stealth scripts
        if self.stealth_mode:
            await self._inject_stealth_scripts()
        
        # Set up request interception
        await self.page.route("**/*", self._handle_request)
        
        # Capture console logs
        self.page.on("console", lambda msg: self.console_logs.append(msg.text))
        
        logger.info("Browser initialized")
    
    async def _inject_stealth_scripts(self):
        """Inject scripts to avoid detection."""
        await self.page.add_init_script("""
            // Override the navigator.webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
    
    async def _handle_request(self, route):
        """Handle network requests and log them."""
        request = route.request
        self.network_requests.append({
            "url": request.url,
            "method": request.method,
            "type": request.resource_type,
            "headers": dict(request.headers),
        })
        await route.continue_()
    
    async def navigate(self, url: str, wait_until: str = "networkidle"):
        """Navigate to a URL and wait for content to load."""
        if not self.page:
            await self.start()
        
        response = await self.page.goto(url, wait_until=wait_until)
        return response
    
    async def scroll_to_bottom(self, iterations: int = 5, delay: float = 1.0):
        """Scroll to bottom multiple times to trigger lazy loading."""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        for i in range(iterations):
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(delay)
            
            # Check if we've reached the bottom
            scrolled = await self.page.evaluate("""
                () => {
                    const scrollTop = window.scrollY;
                    const windowHeight = window.innerHeight;
                    const bodyHeight = document.body.scrollHeight;
                    return scrollTop + windowHeight >= bodyHeight;
                }
            """)
            
            if scrolled:
                break
        
        logger.info(f"Scrolled to bottom after {i + 1} iterations")
    
    async def click_elements(self, selectors: List[str], timeout: int = 2000):
        """Click elements matching selectors to reveal hidden content."""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        clicked_count = 0
        
        for selector in selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                for element in elements:
                    try:
                        await element.click(timeout=timeout)
                        clicked_count += 1
                        await asyncio.sleep(0.3)  # Small delay between clicks
                    except:
                        pass
            except Exception as e:
                logger.warning(f"Error clicking {selector}: {e}")
        
        logger.info(f"Clicked {clicked_count} elements")
        return clicked_count
    
    async def hover_elements(self, selectors: List[str], timeout: int = 2000):
        """Hover over elements to reveal dropdowns and tooltips."""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        hovered_count = 0
        
        for selector in selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                for element in elements[:10]:  # Limit to avoid timeout
                    try:
                        await element.hover(timeout=timeout)
                        hovered_count += 1
                        await asyncio.sleep(0.3)
                    except:
                        pass
            except Exception as e:
                logger.warning(f"Error hovering {selector}: {e}")
        
        logger.info(f"Hovered over {hovered_count} elements")
        return hovered_count
    
    async def capture_content(self) -> Dict[str, Any]:
        """Capture full page content including rendered HTML."""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        html = await self.page.content()
        title = await self.page.title()
        
        # Get all images
        images = await self.page.query_selector_all('img')
        image_data = []
        for img in images[:50]:  # Limit to first 50
            try:
                src = await img.get_attribute('src')
                alt = await img.get_attribute('alt')
                image_data.append({"src": src, "alt": alt})
            except:
                pass
        
        # Get all links
        links = await self.page.query_selector_all('a')
        link_data = []
        for link in links[:100]:  # Limit to first 100
            try:
                href = await link.get_attribute('href')
                text = await link.inner_text()
                link_data.append({"href": href, "text": text})
            except:
                pass
        
        return {
            "html": html,
            "title": title,
            "url": self.page.url,
            "images": image_data,
            "links": link_data,
            "network_requests": self.network_requests.copy(),
            "console_logs": self.console_logs.copy(),
        }
    
    async def take_screenshot(self, output_path: str, full_page: bool = True):
        """Take a screenshot of the page."""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        await self.page.screenshot(
            path=output_path,
            full_page=full_page,
        )
        logger.info(f"Screenshot saved to {output_path}")
    
    async def export_har(self, output_path: str):
        """Export network requests as HAR file."""
        import json
        
        har_data = {
            "log": {
                "version": "1.2",
                "creator": {
                    "name": "web-all",
                    "version": "5.0.0"
                },
                "entries": []
            }
        }
        
        for req in self.network_requests:
            entry = {
                "startedDateTime": "",
                "time": 0,
                "request": {
                    "method": req["method"],
                    "url": req["url"],
                    "headers": [{"name": k, "value": v} for k, v in req.get("headers", {}).items()],
                },
                "response": {
                    "status": 200,
                    "statusText": "OK",
                    "headers": [],
                },
            }
            har_data["log"]["entries"].append(entry)
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(har_data, f, indent=2)
        
        logger.info(f"HAR exported to {output_path}")
    
    async def close(self):
        """Close browser and cleanup."""
        if self.browser:
            await self.browser.close()
            logger.info("Browser closed")


async def test_crawler():
    """Test the async crawler."""
    crawler = AsyncCrawler("https://example.com", headless=True)
    
    try:
        await crawler.start()
        await crawler.navigate("https://example.com")
        await crawler.scroll_to_bottom(iterations=3)
        
        content = await crawler.capture_content()
        print(f"Captured {len(content['html'])} bytes of HTML")
        print(f"Found {len(content['images'])} images")
        print(f"Found {len(content['links'])} links")
        
        await crawler.take_screenshot("./test_screenshot.png")
        await crawler.export_har("./test_network.har")
        
    finally:
        await crawler.close()


if __name__ == "__main__":
    asyncio.run(test_crawler())
