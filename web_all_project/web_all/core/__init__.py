"""
web-all core package.
Contains the main cloning and invisible content discovery engines.
"""

from .cloner import SiteCloner
from .invisible import InvisibleContentEngine

__all__ = ["SiteCloner", "InvisibleContentEngine"]
