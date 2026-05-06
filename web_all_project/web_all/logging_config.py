"""
Logging configuration for web-all.
Supports both JSON and text formatting with structlog.
"""

import logging
import sys
from typing import Any, Dict
from pathlib import Path

import structlog
from structlog.types import Processor


def get_logging_config(log_level: str = "INFO", log_format: str = "json") -> Dict[str, Any]:
    """Configure logging based on settings."""
    
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    if log_format == "json":
        # JSON formatting for production
        processors: list[Processor] = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ]
    else:
        # Console-friendly formatting for development
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    if log_format != "json":
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)
    
    return {"level": level, "format": log_format}


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def setup_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """Initialize logging system."""
    get_logging_config(log_level, log_format)
    logger = get_logger("web_all")
    logger.info("Logging initialized", level=log_level, format=log_format)
