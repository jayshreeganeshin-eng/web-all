"""
weball - AI-Powered Universal Website Cloner & Crawler
Production-ready with Frontend, Backend, Admin Panel, and User Management
"""

__version__ = "4.0.0"
__author__ = "weball Team"
__description__ = "AI-Powered Universal Website Cloner with Tor Support, Auto-Detection, and Automation"

from .core.cloner import SiteCloner
from .core.invisible import InvisibleContentEngine
from .utils.ai_engine import AIEngine, get_available_providers
from .api.server import start_api, app

__all__ = [
    "SiteCloner",
    "InvisibleContentEngine",
    "AIEngine",
    "get_available_providers",
    "start_api",
    "app"
]
