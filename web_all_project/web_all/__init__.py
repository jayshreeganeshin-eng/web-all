"""
web-all: AI-Powered Universal Website Cloner & Crawler

A production-ready tool for downloading entire websites including hidden content,
videos, images, and text with support for Tor/.onion sites.
"""

__version__ = "4.0.0"
__author__ = "web-all Team"
__email__ = "team@web-all.dev"
__license__ = "MIT"

from .core.cloner import SiteCloner
from .core.invisible import InvisibleContentEngine
from .api.server import start_api
from .cli import main as cli_main

__all__ = [
    "SiteCloner",
    "InvisibleContentEngine",
    "start_api",
    "cli_main"
]
