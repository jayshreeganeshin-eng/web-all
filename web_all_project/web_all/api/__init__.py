"""
web-all API package.
Contains the FastAPI REST server.
"""

from .server import start_api, app

__all__ = ["start_api", "app"]
