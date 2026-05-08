"""
web-all: Universal Website Cloner & Crawler
Supports clearnet, .onion (Tor), dynamic content, and full site mirroring.
"""

__version__ = "4.0.0"
__author__ = "web-all Team"

from .api.server import start_api
from .cli import main as cli_main
from .core.cloner import SiteCloner
from .core.invisible import InvisibleContentEngine

__all__ = ["SiteCloner", "InvisibleContentEngine", "start_api", "cli_main"]
