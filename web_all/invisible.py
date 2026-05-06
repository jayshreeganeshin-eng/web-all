"""
Invisible content handler for web-all.
Discovers and downloads hidden content via interaction, sitemaps, and path guessing.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional, Set
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright


class InvisibleContentHandler:
    """Handles discovery and extraction of invisible/hidden content."""

    def __init__(self, base_url: str, headless: bool = True):
        self.base_url = base_url
        self.headless = headless
        self.domain = urlparse(base_url).netloc
        self.discovered_urls: Set[str] = set()

    async def expand_hidden_elements(self, url: str, output_html: Optional[Path] = None) -> str:
        """
        Load page in headless browser, interact with elements to reveal hidden content.
        Returns the fully expanded HTML.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()

            await page.goto(url, wait_until="networkidle")

            # Scroll to bottom multiple times to trigger lazy loading
            for _ in range(5):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1000)

            # Click common toggle/expand elements
            selectors = [
                'button[aria-expanded="false"]',
                ".accordion-toggle",
                ".collapse-toggle",
                '[data-toggle="collapse"]',
                ".load-more",
                "details > summary",
            ]

            for selector in selectors:
                elements = await page.query_selector_all(selector)
                for elem in elements:
                    try:
                        await elem.click(timeout=2000)
                        await page.wait_for_timeout(500)
                    except Exception:  # noqa: BLE001
                        pass

            # Hover over navigation items
            nav_items = await page.query_selector_all("nav a, .menu-item")
            for item in nav_items[:10]:  # Limit to avoid timeout
                try:
                    await item.hover(timeout=2000)
                    await page.wait_for_timeout(300)
                except Exception:  # noqa: BLE001
                    pass

            # Get final HTML
            html = await page.content()

            if output_html:
                output_html.write_text(html, encoding="utf-8")

            await browser.close()
            return html

    async def discover_from_sitemap(self) -> List[str]:
        """Parse sitemap.xml to discover URLs."""
        sitemap_url = urljoin(self.base_url, "/sitemap.xml")
        urls = []

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                page = await browser.new_page()

                response = await page.goto(sitemap_url)
                if response and response.status == 200:
                    content = await page.content()

                    # Parse XML
                    try:
                        root = ET.fromstring(content.encode("utf-8"))
                        # Handle namespace
                        ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

                        for loc in root.findall(".//ns:loc", ns):
                            url = loc.text
                            if urlparse(url).netloc == self.domain:
                                urls.append(url)
                                self.discovered_urls.add(url)
                    except ET.ParseError:
                        # Try without namespace
                        try:
                            root = ET.fromstring(
                                content.encode("utf-8").replace(
                                    b'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"', b""
                                )
                            )
                            for loc in root.findall(".//loc"):
                                url = loc.text
                                if urlparse(url).netloc == self.domain:
                                    urls.append(url)
                                    self.discovered_urls.add(url)
                        except Exception:  # noqa: BLE001
                            pass

                await browser.close()
        except Exception as e:
            print(f"Error parsing sitemap: {e}")

        return urls

    async def guess_paths(self) -> List[str]:
        """Try common paths to discover hidden pages."""
        common_paths = [
            "/admin",
            "/wp-admin",
            "/login",
            "/signin",
            "/sitemap.xml",
            "/robots.txt",
            "/api",
            "/api/v1",
            "/graphql",
            "/blog",
            "/news",
            "/articles",
            "/products",
            "/services",
            "/about",
            "/contact",
            "/search",
            "/archive",
        ]

        discovered = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()

            for path in common_paths:
                url = urljoin(self.base_url, path)
                try:
                    response = await page.goto(url, timeout=5000)
                    if response and response.status == 200:
                        if urlparse(url).netloc == self.domain:
                            discovered.append(url)
                            self.discovered_urls.add(url)
                except Exception:  # noqa: BLE001
                    pass

            await browser.close()

        return discovered

    async def discover_all(self) -> Set[str]:
        """Run all discovery methods."""
        print("Discovering from sitemap...")
        await self.discover_from_sitemap()

        print("Guessing common paths...")
        await self.guess_paths()

        print(f"Total discovered URLs: {len(self.discovered_urls)}")
        return self.discovered_urls
