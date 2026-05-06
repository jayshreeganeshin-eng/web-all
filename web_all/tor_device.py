"""
web-all: Advanced Tor & Multi-Device Support Module
Handles .onion routing, device emulation, and responsive crawling.
"""

import os
import socket
import subprocess
import time
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from dataclasses import dataclass

@dataclass
class DeviceProfile:
    name: str
    user_agent: str
    viewport_width: int
    viewport_height: int
    device_scale_factor: float
    is_mobile: bool
    has_touch: bool

# Pre-defined Device Profiles
DEVICE_PROFILES = {
    "desktop": DeviceProfile(
        name="Desktop", user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport_width=1920, viewport_height=1080, device_scale_factor=1, is_mobile=False, has_touch=False
    ),
    "iphone12": DeviceProfile(
        name="iPhone 12", user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
        viewport_width=390, viewport_height=844, device_scale_factor=3, is_mobile=True, has_touch=True
    ),
    "pixel5": DeviceProfile(
        name="Pixel 5", user_agent="Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        viewport_width=393, viewport_height=851, device_scale_factor=2.75, is_mobile=True, has_touch=True
    ),
    "ipad": DeviceProfile(
        name="iPad Pro", user_agent="Mozilla/5.0 (iPad; CPU OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
        viewport_width=834, viewport_height=1112, device_scale_factor=2, is_mobile=True, has_touch=True
    )
}

class TorManager:
    """Manages Tor connection and proxy configuration."""

    TOR_SOCKS_PORT_MAC = 9150  # Tor Browser default on Mac
    TOR_SOCKS_PORT_LINUX = 9050  # Tor Daemon default on Linux
    TOR_SOCKS_PORT_WIN = 9150  # Tor Browser default on Windows

    def __init__(self):
        self.proxy_server = None
        self.is_onion_mode = False

    def detect_tor(self) -> Optional[int]:
        """Detects running Tor instance and returns port."""
        ports_to_check = [self.TOR_SOCKS_PORT_MAC, self.TOR_SOCKS_PORT_LINUX, self.TOR_SOCKS_PORT_WIN]

        for port in ports_to_check:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()
                if result == 0:
                    print(f"✅ Tor detected on port {port}")
                    return port
            except Exception:
                continue
        return None

    def configure_for_onion(self, url: str) -> Dict[str, Any]:
        """Returns proxy config if URL is .onion"""
        if not url.endswith('.onion'):
            return {}

        self.is_onion_mode = True
        port = self.detect_tor()

        if not port:
            raise ConnectionError(
                "❌ Tor is not running! To crawl .onion sites:\n"
                "1. Install Tor Browser (https://www.torproject.org)\n"
                "2. Start Tor Browser and keep it open\n"
                "3. OR install tor daemon: 'sudo apt install tor' (Linux) or 'brew install tor' (Mac)\n"
                "4. Run this command again."
            )

        self.proxy_server = f"socks5://127.0.0.1:{port}"
        print(f"🧅 Routing traffic through Tor (Port {port})")

        return {
            "proxy": {
                "server": self.proxy_server,
                "anonymize": True
            },
            "ignore_https_errors": True  # Common in onion sites with self-signed certs
        }

class DeviceOptimizer:
    """Handles multi-device rendering and optimization."""

    def __init__(self, device_name: str = "desktop"):
        self.profile = DEVICE_PROFILES.get(device_name.lower(), DEVICE_PROFILES["desktop"])

    async def apply_to_context(self, context: BrowserContext):
        """Applies device settings to the browser context."""
        # Playwright context options
        await context.set_extra_http_headers({
            "User-Agent": self.profile.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        })

        # Note: Viewport is usually set on page creation, but we can resize
        # For comprehensive testing, we might want to capture multiple views
        return self.profile

    async def responsive_capture(self, page: Page, url: str):
        """
        Loads the page in multiple viewports to trigger all responsive elements
        (e.g., mobile menus, lazy loads that only fire on small screens).
        """
        print(f"📱 Optimizing for {self.profile.name}...")

        # Set initial viewport
        await page.set_viewport_size({
            "width": self.profile.viewport_width,
            "height": self.profile.viewport_height
        })

        # Load page
        await page.goto(url, wait_until="networkidle", timeout=60000)

        # If it's a mobile device, simulate touch interactions to open menus
        if self.profile.is_mobile:
            await self._trigger_mobile_elements(page)

        return page

    async def _trigger_mobile_elements(self, page: Page):
        """Clicks common mobile menu triggers."""
        mobile_selectors = [
            ".menu-toggle", ".hamburger", ".nav-icon",
            "[aria-label='Menu']", ".mobile-nav-btn", "#drawer-toggle"
        ]

        for selector in mobile_selectors:
            try:
                element = page.locator(selector)
                if await element.count() > 0:
                    await element.first.click(timeout=2000)
                    await page.wait_for_timeout(1000) # Wait for animation
                    print(f"   -> Triggered mobile element: {selector}")
            except Exception:
                pass # Element not found or not visible, skip

async def create_tor_browser_session(playwright, tor_manager: TorManager, device_optimizer: DeviceOptimizer, headless: bool = True):
    """Creates a browser session configured for Tor and specific device."""

    browser_args = [
        "--disable-blink-features=AutomationControlled",
        "--no-sandbox",
        "--disable-dev-shm-usage"
    ]

    # Launch browser
    browser = await playwright.chromium.launch(
        headless=headless,
        args=browser_args
    )

    # Prepare context options
    context_options = {
        "viewport": {
            "width": device_optimizer.profile.viewport_width,
            "height": device_optimizer.profile.viewport_height
        },
        "device_scale_factor": device_optimizer.profile.device_scale_factor,
        "is_mobile": device_optimizer.profile.is_mobile,
        "has_touch": device_optimizer.profile.has_touch,
        "user_agent": device_optimizer.profile.user_agent
    }

    # Add Tor proxy if needed
    if tor_manager.is_onion_mode:
        context_options.update(tor_manager.configure_for_onion("")) # Config already stored in manager

    context = await browser.new_context(**context_options)
    return browser, context

# Helper to check if URL is onion
def is_onion_url(url: str) -> bool:
    return url.endswith('.onion') or '.onion/' in url
