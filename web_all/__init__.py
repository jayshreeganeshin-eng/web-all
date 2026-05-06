"""
web-all: Universal Website Cloner & Crawler with AI-Powered SEO
Supports clearnet, .onion (Tor), dynamic content, full site mirroring,
AI-powered SEO analysis, auto content generation, and REST API.
"""

__version__ = "3.0.0"
__author__ = "web-all Team"

from .core.cloner import SiteCloner
from .core.invisible import InvisibleContentEngine
from .utils.ai_engine import AIEngine
from .services.seo_service import SEOService
from .api.server import start_api
from .database import init_db, get_db
from .cli import main as cli_main
from .utils.zip_utils import (
    create_zip_archive,
    extract_zip_archive,
    get_directory_size,
    format_size
)

__all__ = [
    # Core
    "SiteCloner",
    "InvisibleContentEngine", 
    "AIEngine",
    "SEOService",
    
    # API
    "app",
    "create_app",
    "start_api",
    
    # Database
    "init_db",
    "get_db",
    
    # CLI
    "cli_main",
    
    # Utilities
    "create_zip_archive",
    "extract_zip_archive",
    "get_directory_size",
    "format_size"
]
