"""
Tier 2, Feature 6: Browser Cluster Management

Pool of browser instances for parallel processing.
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class BrowserInstance:
    """Represents a browser instance in the pool."""
    instance_id: str
    status: str = "idle"
    current_url: Optional[str] = None
    created_at: float = 0.0
    last_used: float = 0.0


class BrowserClusterManager:
    """
    Browser Cluster Manager
    
    Manages a pool of browser instances for parallel crawling.
    """
    
    def __init__(self, max_browsers: int = 10):
        self.max_browsers = max_browsers
        self.browsers: Dict[str, BrowserInstance] = {}
        
    async def initialize(self) -> bool:
        await asyncio.sleep(0.1)
        return True
    
    async def create_browser(self) -> BrowserInstance:
        if len(self.browsers) >= self.max_browsers:
            raise Exception("Maximum browser limit reached")
        
        instance_id = f"browser_{len(self.browsers)}"
        browser = BrowserInstance(
            instance_id=instance_id,
            created_at=asyncio.get_event_loop().time()
        )
        self.browsers[instance_id] = browser
        return browser
    
    async def get_available_browser(self) -> Optional[BrowserInstance]:
        for browser in self.browsers.values():
            if browser.status == "idle":
                browser.status = "busy"
                browser.last_used = asyncio.get_event_loop().time()
                return browser
        return None
    
    async def release_browser(self, instance_id: str) -> bool:
        browser = self.browsers.get(instance_id)
        if browser:
            browser.status = "idle"
            browser.current_url = None
            return True
        return False
    
    async def get_stats(self) -> Dict:
        total = len(self.browsers)
        busy = sum(1 for b in self.browsers.values() if b.status == "busy")
        return {
            "total": total,
            "available": total - busy,
            "busy": busy,
            "max": self.max_browsers
        }
