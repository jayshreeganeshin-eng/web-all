"""
Configuration management for web-all.
Handles user preferences, default settings, and configuration files.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field, asdict


@dataclass
class CloneConfig:
    """Configuration for website cloning."""
    depth: int = 5
    concurrency: int = 5
    delay: float = 1.0
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    respect_robots: bool = True
    discover_invisible: bool = False
    include_patterns: list = field(default_factory=list)
    exclude_patterns: list = field(default_factory=list)
    
    
@dataclass
class DownloadConfig:
    """Configuration for downloads."""
    output_dir: str = "./output"
    create_zip: bool = False
    upload_ftp: bool = False
    ftp_host: str = ""
    ftp_user: str = ""
    ftp_password: str = ""
    
    
@dataclass
class BrowserConfig:
    """Configuration for browser emulation."""
    headless: bool = True
    device: str = "desktop"
    viewport_width: int = 1920
    viewport_height: int = 1080
    timeout: int = 30000
    
    
@dataclass
class AppConfig:
    """Main application configuration."""
    clone: CloneConfig = field(default_factory=CloneConfig)
    download: DownloadConfig = field(default_factory=DownloadConfig)
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    log_level: str = "INFO"
    log_file: str = "./logs/web_all.log"
    

class ConfigManager:
    """Manage application configuration."""
    
    DEFAULT_CONFIG_FILE = Path.home() / ".web_all" / "config.json"
    
    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or self.DEFAULT_CONFIG_FILE
        self.config = AppConfig()
        
    def load(self) -> AppConfig:
        """Load configuration from file."""
        if not self.config_file.exists():
            return self.config
            
        try:
            data = json.loads(self.config_file.read_text(encoding='utf-8'))
            
            # Update config with saved values
            if 'clone' in data:
                for key, value in data['clone'].items():
                    if hasattr(self.config.clone, key):
                        setattr(self.config.clone, key, value)
                        
            if 'download' in data:
                for key, value in data['download'].items():
                    if hasattr(self.config.download, key):
                        setattr(self.config.download, key, value)
                        
            if 'browser' in data:
                for key, value in data['browser'].items():
                    if hasattr(self.config.browser, key):
                        setattr(self.config.browser, key, value)
                        
            if 'log_level' in data:
                self.config.log_level = data['log_level']
                
            if 'log_file' in data:
                self.config.log_file = data['log_file']
                
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Error loading config: {e}")
            
        return self.config
        
    def save(self, config: Optional[AppConfig] = None) -> None:
        """Save configuration to file."""
        if config:
            self.config = config
            
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = asdict(self.config)
        self.config_file.write_text(
            json.dumps(data, indent=2),
            encoding='utf-8'
        )
        
    def get(self) -> AppConfig:
        """Get current configuration."""
        return self.config
        
    def update_clone(self, **kwargs) -> None:
        """Update clone configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config.clone, key):
                setattr(self.config.clone, key, value)
                
    def update_download(self, **kwargs) -> None:
        """Update download configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config.download, key):
                setattr(self.config.download, key, value)
                
    def update_browser(self, **kwargs) -> None:
        """Update browser configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config.browser, key):
                setattr(self.config.browser, key, value)
                
    def reset(self) -> AppConfig:
        """Reset to default configuration."""
        self.config = AppConfig()
        return self.config


# Global configuration instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
        _config_manager.load()
    return _config_manager


def get_config() -> AppConfig:
    """Get the current application configuration."""
    return get_config_manager().get()


def save_config(config: AppConfig) -> None:
    """Save configuration to file."""
    get_config_manager().save(config)
