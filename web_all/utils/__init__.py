"""
web-all utilities package.
Provides AI engine, ZIP utilities, and helper functions.
"""

from .ai_engine import AIEngine, get_available_providers, validate_api_key
from .zip_utils import create_zip_archive, extract_zip_archive, format_size, get_directory_size

__all__ = [
    "AIEngine",
    "get_available_providers",
    "validate_api_key",
    "create_zip_archive",
    "extract_zip_archive",
    "format_size",
    "get_directory_size",
]
