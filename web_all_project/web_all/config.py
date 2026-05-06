"""
Configuration management for web-all.
Uses pydantic-settings for environment-based configuration.
"""

from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_prefix="WEB_ALL_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application Settings
    host: str = Field(default="0.0.0.0", description="Host to bind the server")
    port: int = Field(default=8000, ge=1, le=65535, description="Port to bind the server")
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Output Directory
    output_dir: str = Field(default="./output", description="Default output directory")
    
    # Cloning Settings
    default_depth: int = Field(default=2, ge=0, le=10, description="Default crawl depth")
    default_concurrency: int = Field(default=5, ge=1, le=20, description="Default concurrent requests")
    default_delay: float = Field(default=1.0, ge=0, description="Delay between requests in seconds")
    user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        description="User agent string"
    )
    
    # Tor Settings
    tor_proxy: str = Field(default="http://127.0.0.1:9050", description="Tor proxy address")
    tor_enabled: bool = Field(default=False, description="Enable Tor by default")
    
    # AI Settings
    ai_enabled: bool = Field(default=False, description="Enable AI features")
    ai_provider: str = Field(default="ollama", description="AI provider (ollama, openrouter, groq, huggingface)")
    ai_model: str = Field(default="llama3", description="AI model to use")
    ai_base_url: str = Field(default="http://localhost:11434", description="AI service base URL")
    ai_api_key: Optional[str] = Field(default=None, description="AI API key")
    
    # Database Settings
    database_url: str = Field(default="sqlite+aiosqlite:///./web_all.db", description="Database connection URL")
    
    # Redis Settings
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(default=60, ge=1, description="Rate limit requests per minute")
    rate_limit_burst: int = Field(default=10, ge=1, description="Rate limit burst size")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json or text)")
    
    # Prometheus Metrics
    metrics_enabled: bool = Field(default=True, description="Enable Prometheus metrics")
    metrics_port: int = Field(default=9090, ge=1, le=65535, description="Metrics server port")
    
    # Security Limits
    max_depth: int = Field(default=10, ge=1, description="Maximum allowed crawl depth")
    max_concurrency: int = Field(default=20, ge=1, description="Maximum allowed concurrency")
    timeout_seconds: int = Field(default=30, ge=1, description="Request timeout in seconds")
    respect_robots_txt: bool = Field(default=True, description="Respect robots.txt rules")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.debug


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings
