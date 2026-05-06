"""
Test suite for web-all project
"""

import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_all import SiteCloner, InvisibleContentEngine


class TestSiteCloner:
    """Tests for SiteCloner class"""

    def test_init(self):
        """Test SiteCloner initialization"""
        cloner = SiteCloner(output_dir="./test_output", depth=2)
        assert "test_output" in str(cloner.output_dir)
        assert cloner.depth == 2
        assert cloner.concurrency == 3

    def test_normalize_url(self):
        """Test URL normalization"""
        cloner = SiteCloner()
        normalized = cloner._normalize_url("https://example.com/page/")
        assert "example.com/page" in normalized

    def test_is_same_domain(self):
        """Test domain checking"""
        cloner = SiteCloner()
        # Test with internal URL (same domain)
        assert cloner._is_internal_url("https://example.com/page", "example.com")
        # Test with external URL (different domain)
        assert not cloner._is_internal_url("https://other.com/page", "example.com")


class TestInvisibleContentEngine:
    """Tests for InvisibleContentEngine class"""

    def test_init(self):
        """Test InvisibleContentEngine initialization"""
        engine = InvisibleContentEngine()
        assert engine is not None


class TestCLI:
    """Tests for CLI functionality"""

    def test_clone_command(self):
        """Test clone command execution"""
        import subprocess
        result = subprocess.run(
            ["python", "cli.py", "clone", "https://example.com", "-o", "./test_cli_output"],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0 or "complete" in result.stdout.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
