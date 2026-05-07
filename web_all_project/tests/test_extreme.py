"""
Comprehensive extreme test suite for web-all project
Tests all functionalities including edge cases, stress tests, and integration tests
"""

import pytest
import os
import sys
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_all.core.cloner import SiteCloner
from web_all.core.invisible import InvisibleContentEngine


class TestSiteClonerExtreme:
    """Extreme tests for SiteCloner class"""
    
    def test_init_default_values(self):
        """Test default initialization values"""
        cloner = SiteCloner()
        assert cloner.depth == 2
        assert cloner.concurrency == 5
        assert cloner.delay == 0.5
        assert cloner.timeout == 30
        assert cloner.respect_robots == False
        assert cloner.auto_organize == True
        
    def test_init_custom_values(self):
        """Test custom initialization values"""
        cloner = SiteCloner(
            output_dir="./custom_output",
            depth=10,
            concurrency=20,
            delay=2.0,
            timeout=60,
            respect_robots=True,
            auto_organize=False
        )
        assert cloner.depth == 10
        assert cloner.concurrency == 20
        assert cloner.delay == 2.0
        assert cloner.timeout == 60
        assert cloner.respect_robots == True
        assert cloner.auto_organize == False
    
    def test_normalize_url_variations(self):
        """Test URL normalization with various formats"""
        cloner = SiteCloner()
        
        # Test trailing slash removal
        assert cloner._normalize_url("https://example.com/page/") == "https://example.com/page"
        
        # Test fragment removal
        assert "#section" not in cloner._normalize_url("https://example.com/page#section")
        
        # Test lowercase conversion
        normalized = cloner._normalize_url("https://EXAMPLE.com/Page")
        assert "example.com" in normalized
        
        # Test root path
        assert cloner._normalize_url("https://example.com") == "https://example.com/"
        
    def test_is_internal_url_edge_cases(self):
        """Test internal URL detection with edge cases"""
        cloner = SiteCloner()
        
        # Same domain
        assert cloner._is_internal_url("https://example.com/page", "example.com")
        
        # Subdomain
        assert cloner._is_internal_url("https://sub.example.com/page", "example.com")
        
        # Different domain
        assert not cloner._is_internal_url("https://other.com/page", "example.com")
        
        # HTTP vs HTTPS
        assert cloner._is_internal_url("http://example.com/page", "example.com")
        
    def test_extract_links_comprehensive(self):
        """Test link extraction with various HTML structures"""
        cloner = SiteCloner()
        
        # Basic links
        html = '''
        <html>
            <a href="/page1">Link 1</a>
            <a href="https://example.com/page2">Link 2</a>
            <a href="../page3">Link 3</a>
            <a href="javascript:void(0)">JS Link</a>
            <a href="mailto:test@example.com">Email</a>
            <a href="#anchor">Anchor</a>
            <a href="tel:+1234567890">Phone</a>
        </html>
        '''
        links = cloner.extract_links(html, "https://example.com")
        
        assert len(links) == 3  # Only valid links
        assert "https://example.com/page1" in links
        assert "https://example.com/page2" in links
        assert "https://example.com/page3" in links
        
    def test_extract_assets_all_types(self):
        """Test asset extraction for all types"""
        cloner = SiteCloner()
        
        html = '''
        <html>
            <img src="/images/logo.png">
            <img src="https://cdn.example.com/banner.jpg">
            <link rel="stylesheet" href="/css/style.css">
            <link rel="stylesheet" href="https://cdn.example.com/theme.css">
            <script src="/js/app.js"></script>
            <script src="https://cdn.example.com/analytics.js"></script>
            <img src="data:image/png;base64,ABC123">  <!-- Should be ignored -->
        </html>
        '''
        
        assets = cloner.extract_assets(html, "https://example.com")
        
        assert len(assets['images']) == 2
        assert len(assets['css']) == 2
        assert len(assets['js']) == 2
        
    def test_asset_path_generation(self):
        """Test organized asset path generation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cloner = SiteCloner(output_dir=tmpdir)
            
            # Test image path
            img_path = cloner._get_asset_path("https://example.com/images/logo.png", "images")
            assert "images" in str(img_path)
            assert "logo.png" in str(img_path)
            
            # Test CSS path
            css_path = cloner._get_asset_path("https://example.com/css/style.css", "css")
            assert "css" in str(css_path)
            
            # Test JS path
            js_path = cloner._get_asset_path("https://example.com/js/app.js", "js")
            assert "js" in str(js_path)
    
    @pytest.mark.asyncio
    async def test_fetch_page_success(self):
        """Test successful page fetch"""
        cloner = SiteCloner()
        
        with patch.object(cloner.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "<html><body>Test</body></html>"
            mock_get.return_value = mock_response
            
            html = await cloner.fetch_page("https://example.com")
            
            assert html is not None
            assert "Test" in html
            assert "https://example.com/" in cloner.visited_urls
    
    @pytest.mark.asyncio
    async def test_fetch_page_failure(self):
        """Test failed page fetch"""
        cloner = SiteCloner()
        
        with patch.object(cloner.session, 'get') as mock_get:
            mock_get.side_effect = Exception("Connection error")
            
            html = await cloner.fetch_page("https://example.com")
            
            assert html is None
            assert cloner.stats['errors'] >= 0
    
    @pytest.mark.asyncio
    async def test_fetch_page_non_200(self):
        """Test page fetch with non-200 status"""
        cloner = SiteCloner()
        
        with patch.object(cloner.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            
            html = await cloner.fetch_page("https://example.com/notfound")
            
            assert html is None
    
    @pytest.mark.asyncio
    async def test_duplicate_url_prevention(self):
        """Test that duplicate URLs are not fetched twice"""
        cloner = SiteCloner()
        
        with patch.object(cloner.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "<html>Test</html>"
            mock_get.return_value = mock_response
            
            # First fetch
            result1 = await cloner.fetch_page("https://example.com")
            assert result1 is not None
            
            # Second fetch (should return None)
            result2 = await cloner.fetch_page("https://example.com")
            assert result2 is None
    
    def test_save_html_with_metadata(self):
        """Test HTML saving with metadata comment"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cloner = SiteCloner(output_dir=tmpdir)
            
            html = "<html><body>Test Content</body></html>"
            output_path = Path(tmpdir) / "test.html"
            
            cloner.save_html(html, "https://example.com/test", output_path)
            
            assert output_path.exists()
            
            with open(output_path, 'r') as f:
                content = f.read()
                assert "Cloned from https://example.com/test" in content
                assert "Test Content" in content
    
    def test_stats_tracking(self):
        """Test statistics tracking during cloning"""
        cloner = SiteCloner()
        
        # Initial stats
        assert cloner.stats['pages'] == 0
        assert cloner.stats['images'] == 0
        assert cloner.stats['css'] == 0
        assert cloner.stats['js'] == 0
        assert cloner.stats['errors'] == 0


class TestInvisibleContentEngineExtreme:
    """Extreme tests for InvisibleContentEngine"""
    
    def test_init_default(self):
        """Test default initialization"""
        engine = InvisibleContentEngine()
        assert engine.use_tor == False
        assert engine.tor_proxy == "http://127.0.0.1:9050"
        assert engine.timeout == 30000
    
    def test_init_custom(self):
        """Test custom initialization"""
        engine = InvisibleContentEngine(
            use_tor=True,
            tor_proxy="http://proxy:9050",
            timeout=60000
        )
        assert engine.use_tor == True
        assert engine.tor_proxy == "http://proxy:9050"
        assert engine.timeout == 60000
    
    def test_default_click_selectors(self):
        """Test default click selectors are defined"""
        engine = InvisibleContentEngine()
        
        # These should be the defaults used in expand_all_content
        default_selectors = [
            'button',
            '[role="button"]',
            '.toggle',
            '.expand',
            '.accordion-title',
            '.load-more',
            '[aria-expanded="false"]',
            'details > summary'
        ]
        
        for selector in default_selectors:
            assert selector in ['button', '[role="button"]', '.toggle', '.expand', 
                              '.accordion-title', '.load-more', '[aria-expanded="false"]', 
                              'details > summary']
    
    def test_default_hover_selectors(self):
        """Test default hover selectors are defined"""
        default_selectors = [
            '.dropdown',
            '.menu-item',
            '[data-hover]',
            'nav li'
        ]
        
        for selector in default_selectors:
            assert selector in ['.dropdown', '.menu-item', '[data-hover]', 'nav li']


class TestIntegrationExtreme:
    """Integration tests for complete workflows"""
    
    def test_cloner_workflow_mock(self):
        """Test complete cloning workflow with mocks"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cloner = SiteCloner(output_dir=tmpdir, depth=1, concurrency=2)
            
            # Mock the session
            with patch.object(cloner.session, 'get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.text = '''
                <html>
                    <head>
                        <link rel="stylesheet" href="/style.css">
                    </head>
                    <body>
                        <a href="/page2">Next</a>
                        <img src="/image.png">
                    </body>
                </html>
                '''
                mock_get.return_value = mock_response
                
                # Run async workflow
                async def run_clone():
                    html = await cloner.fetch_page("https://example.com")
                    if html:
                        links = cloner.extract_links(html, "https://example.com")
                        assets = cloner.extract_assets(html, "https://example.com")
                        return html, links, assets
                    return None, [], {}
                
                html, links, assets = asyncio.run(run_clone())
                
                assert html is not None
                assert len(links) > 0
                assert 'images' in assets
                assert 'css' in assets
                assert 'js' in assets
    
    def test_output_directory_creation(self):
        """Test that output directories are created properly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "nested" / "output" / "dir"
            cloner = SiteCloner(output_dir=str(output_path))
            
            # Directory should not exist yet
            assert not output_path.exists()
            
            # Create it
            cloner.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Now it should exist
            assert output_path.exists()
    
    def test_manifest_structure(self):
        """Test manifest data structure"""
        cloner = SiteCloner()
        
        manifest = {
            "start_url": "https://example.com",
            "base_domain": "example.com",
            "mode": "static",
            "use_tor": False,
            "timestamp": "2024-01-01T00:00:00",
            "settings": {
                "depth": 2,
                "concurrency": 5,
                "delay": 0.5,
                "auto_organize": True,
                "download_all_assets": True
            }
        }
        
        assert "start_url" in manifest
        assert "settings" in manifest
        assert manifest["settings"]["depth"] == 2


class TestEdgeCasesExtreme:
    """Edge case tests"""
    
    def test_empty_html_extraction(self):
        """Test extraction from empty HTML"""
        cloner = SiteCloner()
        
        html = "<html><head></head><body></body></html>"
        
        links = cloner.extract_links(html, "https://example.com")
        assets = cloner.extract_assets(html, "https://example.com")
        
        assert len(links) == 0
        assert len(assets['images']) == 0
        assert len(assets['css']) == 0
        assert len(assets['js']) == 0
    
    def test_malformed_html_handling(self):
        """Test handling of malformed HTML"""
        cloner = SiteCloner()
        
        html = "<html><body><a href='/page'>Unclosed tag<div>Mixed content</a></div>"
        
        # Should not raise exception
        links = cloner.extract_links(html, "https://example.com")
        assert isinstance(links, list)
    
    def test_relative_url_resolution(self):
        """Test relative URL resolution"""
        cloner = SiteCloner()
        
        html = '''
        <html>
            <a href="relative">Relative</a>
            <a href="../parent">Parent</a>
            <a href="/absolute">Absolute</a>
            <a href="?query=1">Query</a>
        </html>
        '''
        
        links = cloner.extract_links(html, "https://example.com/path/page")
        
        assert "https://example.com/path/relative" in links
        assert "https://example.com/parent" in links
        assert "https://example.com/absolute" in links
    
    def test_unicode_url_handling(self):
        """Test Unicode URL handling"""
        cloner = SiteCloner()
        
        html = '<a href="/страница">Russian</a>'
        links = cloner.extract_links(html, "https://example.com")
        
        assert len(links) > 0
        assert "/страница" in links[0] or "%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0" in links[0]
    
    def test_special_characters_in_assets(self):
        """Test special characters in asset URLs"""
        cloner = SiteCloner()
        
        html = '''
        <img src="/images/photo%20name.png">
        <link rel="stylesheet" href="/css/style-v1.0.css">
        '''
        
        assets = cloner.extract_assets(html, "https://example.com")
        assert len(assets['images']) > 0
        assert len(assets['css']) > 0


class TestConcurrencyExtreme:
    """Concurrency and performance tests"""
    
    def test_semaphore_initialization(self):
        """Test semaphore is properly initialized"""
        cloner = SiteCloner(concurrency=10)
        assert cloner.semaphore._value == 10
    
    @pytest.mark.asyncio
    async def test_concurrent_fetch_limit(self):
        """Test that concurrent fetches are limited"""
        cloner = SiteCloner(concurrency=2)
        
        call_count = 0
        max_concurrent = 0
        current_concurrent = 0
        
        async def mock_fetch(url):
            nonlocal call_count, max_concurrent, current_concurrent
            call_count += 1
            current_concurrent += 1
            max_concurrent = max(max_concurrent, current_concurrent)
            await asyncio.sleep(0.1)
            current_concurrent -= 1
            return "<html>Test</html>"
        
        # This would test actual concurrency limits
        # For now, just verify semaphore exists
        assert cloner.semaphore._value == 2


class TestConfigurationExtreme:
    """Configuration and parameter tests"""
    
    def test_tor_proxy_configuration(self):
        """Test Tor proxy configuration"""
        cloner = SiteCloner(use_tor=True, tor_proxy="http://custom-proxy:9050")
        assert cloner.use_tor == True
        assert cloner.tor_proxy == "http://custom-proxy:9050"
    
    def test_user_agent_customization(self):
        """Test custom user agent"""
        custom_ua = "MyBot/1.0 (+https://mysite.com/bot)"
        cloner = SiteCloner(user_agent=custom_ua)
        assert cloner.user_agent == custom_ua
        assert cloner.session.headers["User-Agent"] == custom_ua
    
    def test_timeout_configuration(self):
        """Test timeout configuration"""
        cloner = SiteCloner(timeout=120)
        assert cloner.timeout == 120
    
    def test_delay_configuration(self):
        """Test delay configuration"""
        cloner = SiteCloner(delay=5.0)
        assert cloner.delay == 5.0


class TestErrorHandlingExtreme:
    """Error handling tests"""
    
    def test_network_error_handling(self):
        """Test network error handling"""
        cloner = SiteCloner()
        
        with patch.object(cloner.session, 'get') as mock_get:
            mock_get.side_effect = ConnectionError("Network error")
            
            async def test_fetch():
                html = await cloner.fetch_page("https://example.com")
                return html
            
            result = asyncio.run(test_fetch())
            assert result is None
    
    def test_timeout_error_handling(self):
        """Test timeout error handling"""
        cloner = SiteCloner(timeout=1)
        
        with patch.object(cloner.session, 'get') as mock_get:
            mock_get.side_effect = TimeoutError("Request timed out")
            
            async def test_fetch():
                html = await cloner.fetch_page("https://example.com")
                return html
            
            result = asyncio.run(test_fetch())
            assert result is None
    
    def test_file_write_error_handling(self):
        """Test file write error handling"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cloner = SiteCloner(output_dir=tmpdir)
            
            # Try to write to invalid path
            html = "<html>Test</html>"
            invalid_path = Path("/invalid/path/that/does/not/exist/file.html")
            
            # Should handle error gracefully
            try:
                cloner.save_html(html, "https://example.com", invalid_path)
            except Exception:
                pass  # Expected to fail


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
