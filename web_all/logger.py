"""
Logging configuration for web-all.
Provides structured logging with file and console output.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logger(
    name: str = "web_all",
    log_file: Optional[str] = None,
    level: int = logging.INFO,
) -> logging.Logger:
    """
    Set up a logger with console and optional file output.
    
    Args:
        name: Logger name
        log_file: Optional path to log file
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# Global logger instance
logger = setup_logger()


def get_logger(name: str = "web_all") -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


class JobLogger:
    """Logger specifically for tracking job progress."""
    
    def __init__(self, job_id: str, log_dir: str = "./logs"):
        self.job_id = job_id
        self.log_file = Path(log_dir) / f"job_{job_id}.log"
        self.logger = setup_logger(f"job_{job_id}", str(self.log_file))
        
    def info(self, message: str):
        self.logger.info(message)
        
    def error(self, message: str):
        self.logger.error(message)
        
    def warning(self, message: str):
        self.logger.warning(message)
        
    def debug(self, message: str):
        self.logger.debug(message)
        
    def progress(self, current: int, total: int, message: str = ""):
        """Log progress percentage."""
        percent = (current / total * 100) if total > 0 else 0
        self.logger.info(f"Progress: {percent:.1f}% - {message}")
        
    def get_logs(self) -> str:
        """Read all logs from file."""
        if self.log_file.exists():
            return self.log_file.read_text(encoding='utf-8')
        return ""
