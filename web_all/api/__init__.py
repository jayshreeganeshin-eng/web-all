"""
web-all API package.
Provides FastAPI REST server for website cloning operations.
"""

from .server import app, start_api

__all__ = [
    "app",
    "start_api",
]
