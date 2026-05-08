"""
Comprehensive logging system for web-all repository.
Captures all errors, warnings, and operational logs with production-ready features.
"""

import os
import sys
import json
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import threading


class LogCapture:
    """Centralized log capture for the entire web-all application."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.log_dir = Path(__file__).parent.parent / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Main application log file
        self.main_log_file = self.log_dir / "web_all.log"
        # Error-specific log file
        self.error_log_file = self.log_dir / "errors.log"
        # Cloner-specific log file
        self.cloner_log_file = self.log_dir / "cloner.log"
        # API-specific log file
        self.api_log_file = self.log_dir / "api.log"
        
        # Set up main logger
        self.logger = logging.getLogger("web_all")
        self.logger.setLevel(logging.DEBUG)
        
        # Set up error logger
        self.error_logger = logging.getLogger("web_all_errors")
        self.error_logger.setLevel(logging.ERROR)
        
        # Set up cloner logger
        self.cloner_logger = logging.getLogger("web_all_cloner")
        self.cloner_logger.setLevel(logging.DEBUG)
        
        # Set up API logger
        self.api_logger = logging.getLogger("web_all_api")
        self.api_logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        self.error_logger.handlers.clear()
        self.cloner_logger.handlers.clear()
        self.api_logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # Main log file handler with rotation (10MB max, 5 backups)
        main_file_handler = RotatingFileHandler(
            self.main_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        main_file_handler.setLevel(logging.DEBUG)
        main_file_handler.setFormatter(detailed_formatter)
        
        # Error log file handler with rotation
        error_file_handler = RotatingFileHandler(
            self.error_log_file,
            maxBytes=10*1024*1024,
            backupCount=10,
            encoding='utf-8'
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(detailed_formatter)
        
        # Cloner log file handler
        cloner_file_handler = RotatingFileHandler(
            self.cloner_log_file,
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        cloner_file_handler.setLevel(logging.DEBUG)
        cloner_file_handler.setFormatter(detailed_formatter)
        
        # API log file handler
        api_file_handler = RotatingFileHandler(
            self.api_log_file,
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        api_file_handler.setLevel(logging.DEBUG)
        api_file_handler.setFormatter(detailed_formatter)
        
        # Add handlers to loggers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(main_file_handler)
        self.logger.addHandler(error_file_handler)
        
        self.error_logger.addHandler(error_file_handler)
        self.error_logger.addHandler(console_handler)
        
        self.cloner_logger.addHandler(cloner_file_handler)
        self.cloner_logger.addHandler(console_handler)
        
        self.api_logger.addHandler(api_file_handler)
        self.api_logger.addHandler(console_handler)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
        self.error_logger.propagate = False
        self.cloner_logger.propagate = False
        self.api_logger.propagate = False
        
        # Error tracking
        self.error_count = 0
        self.warning_count = 0
        self.error_history: List[Dict[str, Any]] = []
        self.max_error_history = 1000
        
    def get_logger(self, name: str = "web_all") -> logging.Logger:
        """Get a logger by name."""
        if name == "cloner":
            return self.cloner_logger
        elif name == "api":
            return self.api_logger
        elif name == "errors":
            return self.error_logger
        return self.logger
    
    def log_error(self, message: str, exception: Optional[Exception] = None, 
                  context: Optional[Dict[str, Any]] = None, 
                  logger_name: str = "web_all"):
        """Log an error with full context and stack trace."""
        logger = self.get_logger(logger_name)
        
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "level": "ERROR",
            "logger": logger_name
        }
        
        if exception:
            error_entry["exception_type"] = type(exception).__name__
            error_entry["exception_message"] = str(exception)
            error_entry["stack_trace"] = traceback.format_exc()
            logger.error(f"{message} - {type(exception).__name__}: {exception}\n{traceback.format_exc()}")
        else:
            logger.error(message)
        
        if context:
            error_entry["context"] = context
            logger.debug(f"Error context: {json.dumps(context, indent=2, default=str)}")
        
        # Track error
        self.error_count += 1
        self.error_history.append(error_entry)
        
        # Limit history size
        if len(self.error_history) > self.max_error_history:
            self.error_history = self.error_history[-self.max_error_history:]
        
        return error_entry
    
    def log_warning(self, message: str, context: Optional[Dict[str, Any]] = None,
                   logger_name: str = "web_all"):
        """Log a warning with context."""
        logger = self.get_logger(logger_name)
        
        warning_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "level": "WARNING",
            "logger": logger_name
        }
        
        if context:
            warning_entry["context"] = context
            logger.warning(f"{message} - Context: {json.dumps(context, default=str)}")
        else:
            logger.warning(message)
        
        self.warning_count += 1
        return warning_entry
    
    def log_info(self, message: str, context: Optional[Dict[str, Any]] = None,
                logger_name: str = "web_all"):
        """Log an info message."""
        logger = self.get_logger(logger_name)
        
        if context:
            logger.info(f"{message} - Context: {json.dumps(context, default=str)}")
        else:
            logger.info(message)
    
    def log_debug(self, message: str, context: Optional[Dict[str, Any]] = None,
                 logger_name: str = "web_all"):
        """Log a debug message."""
        logger = self.get_logger(logger_name)
        
        if context:
            logger.debug(f"{message} - Context: {json.dumps(context, default=str)}")
        else:
            logger.debug(message)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of all captured errors."""
        return {
            "total_errors": self.error_count,
            "total_warnings": self.warning_count,
            "recent_errors": self.error_history[-50:],
            "log_files": {
                "main": str(self.main_log_file),
                "errors": str(self.error_log_file),
                "cloner": str(self.cloner_log_file),
                "api": str(self.api_log_file)
            }
        }
    
    def export_errors_to_json(self, output_path: Optional[str] = None) -> str:
        """Export all errors to a JSON file."""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(self.log_dir / f"errors_export_{timestamp}.json")
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "summary": self.get_error_summary(),
            "all_errors": self.error_history
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
        
        return output_path
    
    def clear_logs(self):
        """Clear all log files (use with caution)."""
        for log_file in [self.main_log_file, self.error_log_file, 
                        self.cloner_log_file, self.api_log_file]:
            if log_file.exists():
                log_file.unlink()
        
        self.error_count = 0
        self.warning_count = 0
        self.error_history.clear()


# Global instance
log_capture = LogCapture()


def get_logger(name: str = "web_all") -> logging.Logger:
    """Convenience function to get a logger."""
    return log_capture.get_logger(name)


def log_error(message: str, exception: Optional[Exception] = None,
              context: Optional[Dict[str, Any]] = None,
              logger_name: str = "web_all"):
    """Convenience function to log an error."""
    return log_capture.log_error(message, exception, context, logger_name)


def log_warning(message: str, context: Optional[Dict[str, Any]] = None,
               logger_name: str = "web_all"):
    """Convenience function to log a warning."""
    return log_capture.log_warning(message, context, logger_name)


def log_info(message: str, context: Optional[Dict[str, Any]] = None,
            logger_name: str = "web_all"):
    """Convenience function to log an info message."""
    return log_capture.log_info(message, context, logger_name)


def log_debug(message: str, context: Optional[Dict[str, Any]] = None,
             logger_name: str = "web_all"):
    """Convenience function to log a debug message."""
    return log_capture.log_debug(message, context, logger_name)


# Initialize default logging for backward compatibility
def setup_default_logging():
    """Set up default logging for modules that use standard logging."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
            RotatingFileHandler(
                LogCapture().main_log_file,
                maxBytes=10*1024*1024,
                backupCount=5,
                encoding='utf-8'
            )
        ]
    )


# Auto-initialize
setup_default_logging()
