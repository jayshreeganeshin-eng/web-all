"""
web-all: Universal Website Cloner & Crawler
Supports clearnet, .onion (Tor), dynamic content, and full site mirroring.
"""

__version__ = "3.0.0"
__author__ = "web-all Team"

from .core.cloner import SiteCloner
from .core.invisible import InvisibleContentEngine
from .api.server import start_api

__all__ = [
    "SiteCloner",
    "InvisibleContentEngine", 
    "start_api"
]
