"""
web-all v4.2.0: Universal Website Cloner & Crawler with Worldwide Features
Supports clearnet, .onion (Tor), dynamic content, multi-language, and full site mirroring.
Production-ready with enhanced AI integration and worldwide website support.
"""

__version__ = "4.2.0"
__author__ = "web-all Team"

from .api.server import start_api
from .cli import main as cli_main
from .core.cloner import SiteCloner
from .core.invisible import InvisibleContentEngine
from .utils.ai_engine import AIEngine, get_available_providers
from .utils.zip_utils import create_zip_archive, extract_zip_archive

__all__ = [
    "SiteCloner",
    "InvisibleContentEngine",
    "AIEngine",
    "start_api",
    "cli_main",
    "get_available_providers",
    "create_zip_archive",
    "extract_zip_archive",
]
