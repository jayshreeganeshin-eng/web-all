"""
web-all: Universal Website Cloner & Crawler
============================================
A comprehensive tool for cloning, crawling, and downloading websites including hidden content.

Features:
- Full website cloning with asset mirroring
- Infinite scroll handling
- Hidden content discovery (clicks, hovers, forms)
- Sitemap and robots.txt parsing
- Images, text, and video extraction
- REST API and Web GUI
- Single-command installation
- Tor/.onion support
- Multi-device emulation
"""

__version__ = "1.0.0"
__author__ = "web-all Team"
__all__ = [
    "cloner",
    "invisible",
    "advanced",
    "api",
    "tor_device",
    "cli",
    "WebsiteCloner",
    "InvisibleContentHandler",
    "VideoDownloader",
    "ArchiveManager",
    "FTPUploader",
    "MobileEmulator",
    "AuthManager",
    "TorManager",
    "DeviceOptimizer",
]

from .advanced import (
    ArchiveManager,
    AuthManager,
    FTPUploader,
    MobileEmulator,
    VideoDownloader,
)
from .cloner import WebsiteCloner
from .invisible import InvisibleContentHandler
from .tor_device import DeviceOptimizer, TorManager
