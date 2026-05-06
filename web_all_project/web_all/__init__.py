"""
web-all v4.0: Universal Website Cloner & Crawler
With User Authentication, Admin Panel, and Advanced Features
Supports clearnet, .onion (Tor), dynamic content, and full site mirroring.
"""

__version__ = "4.0.0"
__author__ = "web-all Team"

from .core.cloner import SiteCloner
from .core.invisible import InvisibleContentEngine
from .utils.ai_engine import AIEngine, get_available_providers
from .api.server import app, start_api

__all__ = [
    "SiteCloner",
    "InvisibleContentEngine", 
    "AIEngine",
    "get_available_providers",
    "app",
    "start_api"
]
