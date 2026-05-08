"""
web-all v4.0: Universal Website Cloner & Crawler - GOD LEVEL EDITION
Supports clearnet, .onion (Tor), dynamic content, and full site mirroring.
Features 7 Tiers with 21 God Level Features including Neural AI, Multi-Modal Analysis,
Distributed Crawling, and Enterprise Security.
"""

__version__ = "4.0.0"
__author__ = "web-all Team"
__tier_count__ = 7
__feature_count__ = 21

from .core.cloner import SiteCloner
from .core.invisible import InvisibleContentEngine
from .api.server import start_api
from .cli import main as cli_main

# God Level Features v4.0 - All 7 Tiers
from .god_level import (
    # Tier 1: Divine Intelligence
    NeuralContentEngine,
    MultiModalAIEngine,
    SemanticSearchEngine,
    # Tier 2: Supernatural Performance
    DistributedCrawler,
    IntelligentCacheLayer,
    BrowserClusterManager,
    # Tier 3: Shape-Shifting Capabilities
    AuthenticationHandler,
    JavaScriptExecutionEngine,
    EvasionEngine,
    # Tier 4: Universal Connectivity
    MultiProtocolSupport,
    CloudIntegration,
    MultiFormatExporter,
    # Tier 5: Autonomous Operation
    ScheduledCrawler,
    WorkflowAutomation,
    NaturalLanguageInterface,
    # Tier 6: Analytics & Insights
    AnalyticsDashboard,
    SEOAnalyzer,
    ContentQualityScorer,
    # Tier 7: Enterprise Security
    AccessControlSystem,
    ComplianceTools,
    TeamCollaboration,
)

__all__ = [
    # Core v3.0
    "SiteCloner",
    "InvisibleContentEngine", 
    "start_api",
    "cli_main",
    # God Level v4.0 - Tier 1
    "NeuralContentEngine",
    "MultiModalAIEngine",
    "SemanticSearchEngine",
    # God Level v4.0 - Tier 2
    "DistributedCrawler",
    "IntelligentCacheLayer",
    "BrowserClusterManager",
    # God Level v4.0 - Tier 3
    "AuthenticationHandler",
    "JavaScriptExecutionEngine",
    "EvasionEngine",
    # God Level v4.0 - Tier 4
    "MultiProtocolSupport",
    "CloudIntegration",
    "MultiFormatExporter",
    # God Level v4.0 - Tier 5
    "ScheduledCrawler",
    "WorkflowAutomation",
    "NaturalLanguageInterface",
    # God Level v4.0 - Tier 6
    "AnalyticsDashboard",
    "SEOAnalyzer",
    "ContentQualityScorer",
    # God Level v4.0 - Tier 7
    "AccessControlSystem",
    "ComplianceTools",
    "TeamCollaboration",
]
