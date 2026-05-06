"""
Configuration settings for web-all v5.
Centralized configuration management with environment variable support.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass, field


@dataclass
class CrawlerConfig:
    """Crawler configuration settings."""
    base_url: str = ""
    output_dir: str = "./output"
    depth: int = 5
    concurrency: int = 10
    delay: float = 1.0
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    respect_robots: bool = True
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    timeout: int = 30
    retry_count: int = 3
    headless: bool = True
    stealth_mode: bool = True
    fingerprint_randomize: bool = True
    humanize_traffic: bool = True


@dataclass
class AIConfig:
    """AI/ML configuration settings."""
    provider: str = "anthropic"  # anthropic, openai, ollama
    model: str = "claude-3-7-sonnet-20241022"
    api_key: Optional[str] = None
    vision_enabled: bool = True
    context_window: int = 200000
    temperature: float = 0.7
    max_tokens: int = 4096
    fallback_model: str = "llama-3.1-70b"
    local_model_path: Optional[str] = None


@dataclass
class BackendConfig:
    """Backend service configuration."""
    framework: str = "fastapi"  # fastapi, nextjs_api
    host: str = "0.0.0.0"
    port: int = 8000
    database_url: str = "postgresql://weball:weball@localhost:5432/weball"
    redis_url: str = "redis://localhost:6379"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    asset_bucket: str = "web-all-assets"


@dataclass
class FrontendConfig:
    """Frontend generation configuration."""
    framework: str = "nextjs"  # nextjs, react, vue
    version: str = "16"
    app_router: bool = True
    server_components: bool = True
    tailwind_version: str = "4"
    ui_library: str = "shadcn"  # shadcn, mui, chakra
    typescript: bool = True
    image_optimization: bool = True
    css_minification: bool = True
    lazy_loading: bool = True


@dataclass
class DeploymentConfig:
    """Deployment configuration."""
    platforms: List[str] = field(default_factory=lambda: ["vercel", "netlify", "docker"])
    auto_deploy: bool = False
    docker_registry: str = "docker.io"
    kubernetes_enabled: bool = False
    helm_chart_path: Optional[str] = None


@dataclass
class PluginConfig:
    """Plugin system configuration."""
    enabled: bool = True
    marketplace_url: str = "https://plugins.web-all.dev"
    wasm_sandbox: bool = True
    bundled_plugins: List[str] = field(default_factory=lambda: [
        "seo_analyzer",
        "gdpr_detector",
        "storybook_exporter",
        "cypress_generator",
    ])


@dataclass
class SecurityConfig:
    """Security and ethics configuration."""
    allowed_domains: List[str] = field(default_factory=list)
    blocked_domains: List[str] = field(default_factory=lambda: [
        "banking", "finance", "payment"  # Block sensitive domains by default
    ])
    rate_limit_per_minute: int = 60
    max_concurrent_jobs: int = 10
    require_auth: bool = False
    jwt_secret: Optional[str] = None
    content_replacement_required: bool = True
    include_generator_tag: bool = True


@dataclass
class WebAllConfig:
    """Main configuration container."""
    crawler: CrawlerConfig = field(default_factory=CrawlerConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    backend: BackendConfig = field(default_factory=BackendConfig)
    frontend: FrontendConfig = field(default_factory=FrontendConfig)
    deployment: DeploymentConfig = field(default_factory=DeploymentConfig)
    plugins: PluginConfig = field(default_factory=PluginConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # Project settings
    project_name: str = "web-all"
    version: str = "5.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> "WebAllConfig":
        """Load configuration from environment variables."""
        config = cls()
        
        # Crawler config
        config.crawler.base_url = os.getenv("WEBALL_BASE_URL", "")
        config.crawler.output_dir = os.getenv("WEBALL_OUTPUT_DIR", "./output")
        config.crawler.depth = int(os.getenv("WEBALL_DEPTH", "5"))
        config.crawler.concurrency = int(os.getenv("WEBALL_CONCURRENCY", "10"))
        config.crawler.delay = float(os.getenv("WEBALL_DELAY", "1.0"))
        config.crawler.stealth_mode = os.getenv("WEBALL_STEALTH", "true").lower() == "true"
        
        # AI config
        config.ai.provider = os.getenv("WEBALL_AI_PROVIDER", "anthropic")
        config.ai.model = os.getenv("WEBALL_AI_MODEL", "claude-3-7-sonnet-20241022")
        config.ai.api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
        config.ai.vision_enabled = os.getenv("WEBALL_VISION", "true").lower() == "true"
        
        # Backend config
        config.backend.host = os.getenv("WEBALL_HOST", "0.0.0.0")
        config.backend.port = int(os.getenv("WEBALL_PORT", "8000"))
        config.backend.database_url = os.getenv("DATABASE_URL", config.backend.database_url)
        config.backend.redis_url = os.getenv("REDIS_URL", config.backend.redis_url)
        
        # Security
        config.security.require_auth = os.getenv("WEBALL_AUTH", "false").lower() == "true"
        config.security.jwt_secret = os.getenv("WEBALL_JWT_SECRET")
        config.debug = os.getenv("WEBALL_DEBUG", "false").lower() == "true"
        config.log_level = os.getenv("WEBALL_LOG_LEVEL", "INFO")
        
        return config
    
    def save(self, path: str) -> None:
        """Save configuration to JSON file."""
        import json
        from dataclasses import asdict
        
        config_dict = asdict(self)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> "WebAllConfig":
        """Load configuration from JSON file."""
        import json
        from dataclasses import fields
        
        with open(path, 'r') as f:
            config_dict = json.load(f)
        
        config = cls()
        
        # Recursively set nested config classes
        for field_name, field_obj in fields(config).items():
            if field_name in config_dict:
                value = config_dict[field_name]
                if isinstance(value, dict):
                    nested_class = getattr(config.__annotations__[field_name].__args__[0], '__origin__', None)
                    if nested_class:
                        nested_obj = field_obj.default_factory()
                        for nested_field in fields(nested_obj):
                            if nested_field.name in value:
                                setattr(nested_obj, nested_field.name, value[nested_field.name])
                        setattr(config, field_name, nested_obj)
                else:
                    setattr(config, field_name, value)
        
        return config


# Default global configuration instance
default_config = WebAllConfig()


def get_config() -> WebAllConfig:
    """Get the current configuration, loading from env if available."""
    return WebAllConfig.from_env()
