"""
Unit tests for web-all website cloner.
Tests cover core functionality, utilities, and API endpoints.
"""

import pytest
import asyncio
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Import modules to test
from web_all.core.cloner import SiteCloner
from web_all.utils.zip_utils import create_zip_archive, extract_zip_archive, format_size, get_directory_size
from web_all.utils.ai_engine import (
    AIEngine, 
    AIProvider, 
    OpenRouterProvider, 
    GroqProvider, 
    HuggingFaceProvider, 
    OllamaProvider,
    get_available_providers,
    validate_api_key
)


class TestSiteCloner:
    """Test cases for SiteCloner class."""
    
    def test_init_default_values(self):
        """Test initialization with default values."""
        cloner = SiteCloner()
        
        assert cloner.depth == 2
        assert cloner.concurrency == 5
        assert cloner.delay == 0.5
        assert cloner.use_tor is False
        assert cloner.output_dir == Path("./output")
        assert cloner.stats["pages"] == 0
    
    def test_init_custom_values(self):
        """Test initialization with custom values."""
        cloner = SiteCloner(
            output_dir="./custom_output",
            depth=5,
            concurrency=10,
            delay=1.0,
            use_tor=True
        )
        
        assert cloner.depth == 5
        assert cloner.concurrency == 10
        assert cloner.delay == 1.0
        assert cloner.use_tor is True
        assert cloner.output_dir == Path("./custom_output")
    
    def test_normalize_url(self):
        """Test URL normalization."""
        cloner = SiteCloner()
        
        # Test basic normalization - lowercase domain
        url1 = "https://Example.com/page/"
        normalized1 = cloner._normalize_url(url1)
        assert "example.com" in normalized1
        assert normalized1.endswith("/page")
        
        # Test with query parameters - sorted for consistency
        url2 = "https://example.com/page?param=value"
        normalized2 = cloner._normalize_url(url2)
        assert "?param=value" in normalized2
        
        # Test query parameter sorting (b&a should become a&b)
        url3 = "https://example.com/page?z=1&a=2"
        normalized3 = cloner._normalize_url(url3)
        assert "?a=2&z=1" in normalized3  # Sorted alphabetically
        
        # Test deduplication - different order same params
        url4 = "https://example.com/page?a=2&z=1"
        normalized4 = cloner._normalize_url(url4)
        assert normalized3 == normalized4  # Should be identical
    
    def test_is_internal_url(self):
        """Test internal URL detection."""
        cloner = SiteCloner()
        base_domain = "example.com"
        
        assert cloner._is_internal_url("https://example.com/page", base_domain) is True
        assert cloner._is_internal_url("https://sub.example.com/page", base_domain) is True
        assert cloner._is_internal_url("https://other.com/page", base_domain) is False
    
    def test_should_follow_link_internal(self):
        """Test link following logic for internal links."""
        cloner = SiteCloner()
        cloner.follow_external = False
        cloner.include_subdomains = True
        base_domain = "example.com"
        
        # Should follow internal links
        assert cloner._should_follow_link("https://example.com/page", base_domain) is True
        assert cloner._should_follow_link("https://sub.example.com/page", base_domain) is True
        
        # Should not follow external links
        assert cloner._should_follow_link("https://other.com/page", base_domain) is False
    
    def test_should_follow_link_external(self):
        """Test link following logic when external links are allowed."""
        cloner = SiteCloner()
        cloner.follow_external = True
        base_domain = "example.com"
        
        # Should follow all links when follow_external is True
        assert cloner._should_follow_link("https://other.com/page", base_domain) is True
    
    def test_get_local_html_path_basic(self):
        """Test local HTML path generation for basic URLs."""
        cloner = SiteCloner(output_dir="./test_output")
        
        path = cloner._get_local_html_path("https://example.com/")
        assert "example_com" in str(path)
        assert path.name == "index.html"
    
    def test_get_local_html_path_with_query(self):
        """Test local HTML path generation with query parameters."""
        cloner = SiteCloner(output_dir="./test_output")
        
        path = cloner._get_local_html_path("https://example.com/page?id=123")
        assert "example_com" in str(path)
        assert ".html" in path.name
    
    def test_extract_links(self):
        """Test link extraction from HTML."""
        cloner = SiteCloner()
        
        html = """
        <html>
            <body>
                <a href="/page1">Link 1</a>
                <a href="https://example.com/page2">Link 2</a>
                <a href="javascript:void(0)">JS Link</a>
                <a href="mailto:test@example.com">Email</a>
            </body>
        </html>
        """
        
        links = cloner.extract_links(html, "https://example.com")
        
        assert len(links) == 2  # Only valid links
        assert "https://example.com/page1" in links
        assert "https://example.com/page2" in links
    
    def test_extract_assets(self):
        """Test asset extraction from HTML."""
        cloner = SiteCloner()
        
        html = """
        <html>
            <head>
                <link rel="stylesheet" href="/style.css">
                <script src="/app.js"></script>
            </head>
            <body>
                <img src="/image.png">
                <img src="data:image/png;base64,abc">
            </body>
        </html>
        """
        
        assets = cloner.extract_assets(html, "https://example.com")
        
        assert len(assets["images"]) == 1  # Exclude data URIs
        assert len(assets["css"]) == 1
        assert len(assets["js"]) == 1


class TestZipUtils:
    """Test cases for ZIP utility functions."""
    
    def test_format_size_bytes(self):
        """Test size formatting for bytes."""
        assert format_size(100) == "100.00 B"
        assert format_size(999) == "999.00 B"
    
    def test_format_size_kilobytes(self):
        """Test size formatting for kilobytes."""
        assert format_size(1024) == "1.00 KB"
        assert format_size(2048) == "2.00 KB"
    
    def test_format_size_megabytes(self):
        """Test size formatting for megabytes."""
        assert format_size(1024 * 1024) == "1.00 MB"
        assert format_size(2 * 1024 * 1024) == "2.00 MB"
    
    def test_format_size_gigabytes(self):
        """Test size formatting for gigabytes."""
        assert format_size(1024 * 1024 * 1024) == "1.00 GB"
    
    def test_create_and_extract_zip(self):
        """Test creating and extracting ZIP archives."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source directory with files
            source_dir = Path(tmpdir) / "source"
            source_dir.mkdir()
            
            test_file = source_dir / "test.txt"
            test_file.write_text("Hello, World!")
            
            # Create ZIP
            zip_path = Path(tmpdir) / "test.zip"
            result_path = create_zip_archive(str(source_dir), str(zip_path))
            
            assert Path(result_path).exists()
            assert result_path.endswith(".zip")
            
            # Extract ZIP
            extract_dir = Path(tmpdir) / "extracted"
            extract_result = extract_zip_archive(str(zip_path), str(extract_dir))
            
            assert Path(extract_result).exists()
            extracted_file = extract_dir / "source" / "test.txt"
            assert extracted_file.exists()
            assert extracted_file.read_text() == "Hello, World!"
    
    def test_get_directory_size(self):
        """Test directory size calculation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("x" * 1000)  # 1000 bytes
            
            size = get_directory_size(tmpdir)
            assert size >= 1000
    
    def test_create_zip_nonexistent_directory(self):
        """Test error handling for non-existent directory."""
        with pytest.raises(FileNotFoundError):
            create_zip_archive("/nonexistent/path")


class TestAIEngine:
    """Test cases for AI Engine."""
    
    def test_get_available_providers(self):
        """Test listing available AI providers."""
        providers = get_available_providers()
        
        assert "ollama" in providers
        assert "openrouter" in providers
        assert "groq" in providers
        assert "huggingface" in providers
    
    def test_validate_api_key_ollama(self):
        """Test API key validation for Ollama (no key needed)."""
        assert validate_api_key("ollama", "") is True
        assert validate_api_key("ollama", "any-string") is True
    
    def test_validate_api_key_invalid(self):
        """Test API key validation for other providers with invalid keys."""
        assert validate_api_key("openrouter", "") is False
        assert validate_api_key("openrouter", "short") is False
        assert validate_api_key("groq", None) is False
    
    def test_validate_api_key_valid(self):
        """Test API key validation for other providers with valid keys."""
        assert validate_api_key("openrouter", "sk-or-1234567890abcdef") is True
        assert validate_api_key("groq", "gsk_1234567890abcdef") is True
    
    def test_ai_engine_init_disabled(self):
        """Test AI Engine initialization when disabled."""
        engine = AIEngine({"enabled": False})
        
        assert engine.enabled is False
        assert engine.provider is None
    
    def test_ai_engine_init_ollama(self):
        """Test AI Engine initialization with Ollama."""
        engine = AIEngine({
            "enabled": True,
            "provider": "ollama",
            "base_url": "http://localhost:11434",
            "model": "llama3"
        })
        
        assert engine.enabled is True
        assert engine.provider_name == "ollama"
        assert isinstance(engine.provider, OllamaProvider)
    
    def test_ai_engine_init_openrouter(self):
        """Test AI Engine initialization with OpenRouter."""
        engine = AIEngine({
            "enabled": True,
            "provider": "openrouter",
            "api_key": "test-key-1234567890"
        })
        
        assert engine.enabled is True
        assert isinstance(engine.provider, OpenRouterProvider)
    
    def test_ai_engine_init_groq(self):
        """Test AI Engine initialization with Groq."""
        engine = AIEngine({
            "enabled": True,
            "provider": "groq",
            "api_key": "test-key-1234567890"
        })
        
        assert engine.enabled is True
        assert isinstance(engine.provider, GroqProvider)
    
    def test_ai_engine_init_huggingface(self):
        """Test AI Engine initialization with HuggingFace."""
        engine = AIEngine({
            "enabled": True,
            "provider": "huggingface",
            "api_key": "test-key-1234567890"
        })
        
        assert engine.enabled is True
        assert isinstance(engine.provider, HuggingFaceProvider)
    
    @pytest.mark.asyncio
    async def test_summarize_content_disabled(self):
        """Test content summarization when AI is disabled."""
        engine = AIEngine({"enabled": False})
        
        result = await engine.summarize_content("<p>Test content</p>", "https://example.com")
        assert result == ""
    
    @pytest.mark.asyncio
    async def test_extract_structured_data_disabled(self):
        """Test structured data extraction when AI is disabled."""
        engine = AIEngine({"enabled": False})
        
        result = await engine.extract_structured_data("<p>Test content</p>", "https://example.com")
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_auto_tag_content_disabled(self):
        """Test auto-tagging when AI is disabled."""
        engine = AIEngine({"enabled": False})
        
        result = await engine.auto_tag_content("<p>Test content</p>", "https://example.com")
        assert result == []
    
    @pytest.mark.asyncio
    async def test_filter_irrelevant_content_fallback(self):
        """Test content filtering with fallback (AI disabled)."""
        engine = AIEngine({"enabled": False})
        
        html = """
        <html>
            <nav>Navigation</nav>
            <article>Main Content</article>
            <footer>Footer</footer>
            <script>alert('test');</script>
            <style>.test { color: red; }</style>
        </html>
        """
        
        result = await engine.filter_irrelevant_content(html)
        
        # Fallback should remove nav, footer, script, style tags
        assert "<nav>" not in result
        assert "<footer>" not in result
        assert "<script>" not in result
        assert "<style>" not in result
        assert "Main Content" in result
    
    @pytest.mark.asyncio
    async def test_analyze_and_enhance_disabled(self):
        """Test full analysis pipeline when AI is disabled."""
        engine = AIEngine({"enabled": False})
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            results = await engine.analyze_and_enhance(
                "<p>Test content</p>",
                "https://example.com",
                output_dir
            )
            
            assert results["summary"] == ""
            assert results["structured_data"] == {}
            assert results["tags"] == []


class TestProviders:
    """Test cases for individual AI providers."""
    
    def test_openrouter_provider_init(self):
        """Test OpenRouter provider initialization."""
        provider = OpenRouterProvider("test-api-key")
        
        assert provider.api_key == "test-api-key"
        assert "openrouter.ai" in provider.base_url
    
    def test_groq_provider_init(self):
        """Test Groq provider initialization."""
        provider = GroqProvider("test-api-key")
        
        assert provider.api_key == "test-api-key"
        assert "api.groq.com" in provider.base_url
    
    def test_huggingface_provider_init(self):
        """Test HuggingFace provider initialization."""
        provider = HuggingFaceProvider("test-api-key", "mistralai/Mistral-7B-Instruct-v0.2")
        
        assert provider.api_key == "test-api-key"
        assert provider.model == "mistralai/Mistral-7B-Instruct-v0.2"
    
    def test_ollama_provider_init(self):
        """Test Ollama provider initialization."""
        provider = OllamaProvider("http://localhost:11434", "llama3")
        
        assert provider.api_key is None
        assert provider.base_url == "http://localhost:11434"
        assert provider.model == "llama3"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
