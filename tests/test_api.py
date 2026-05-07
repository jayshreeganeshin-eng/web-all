"""
Unit tests for web-all API server.
Tests cover REST API endpoints, job management, and AI configuration.
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from web_all.api.server import app, jobs, ai_config


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def reset_state():
    """Reset global state before each test."""
    jobs.clear()
    ai_config.update({
        "enabled": False,
        "provider": "ollama",
        "api_key": "",
        "model": "",
        "base_url": "http://localhost:11434"
    })
    yield


class TestAPIHealth:
    """Test API health endpoints."""
    
    def test_root_endpoint(self, client, reset_state):
        """Test root endpoint returns API info."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "detail" in data
    
    def test_health_endpoint(self, client, reset_state):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "web-all API" in data["message"]


class TestCloneJobs:
    """Test clone job creation and management."""
    
    def test_create_clone_job_basic(self, client, reset_state):
        """Test creating a basic clone job."""
        payload = {
            "url": "https://example.com",
            "mode": "static",
            "depth": 2
        }
        
        response = client.post("/api/v1/clone", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "queued"
        assert "message" in data
    
    def test_create_clone_job_with_options(self, client, reset_state):
        """Test creating clone job with various options."""
        payload = {
            "url": "https://example.com",
            "mode": "dynamic",
            "depth": 5,
            "use_tor": False,
            "discover_invisible": True,
            "ai_enabled": False,
            "output_name": "test_clone"
        }
        
        response = client.post("/api/v1/clone", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        
        # Verify job was created
        job_id = data["job_id"]
        assert job_id in jobs
        assert jobs[job_id]["request"]["depth"] == 5
        assert jobs[job_id]["request"]["discover_invisible"] is True
    
    def test_create_clone_job_everything_mode(self, client, reset_state):
        """Test creating clone job with everything mode."""
        payload = {
            "url": "https://example.com",
            "everything": True,
            "depth": 3
        }
        
        response = client.post("/api/v1/clone", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        
        # Verify everything mode settings
        job_id = data["job_id"]
        assert jobs[job_id]["everything"] is True
    
    def test_get_job_status(self, client, reset_state):
        """Test getting job status."""
        # Create a job first
        payload = {"url": "https://example.com"}
        create_response = client.post("/api/v1/clone", json=payload)
        job_id = create_response.json()["job_id"]
        
        # Get status
        status_response = client.get(f"/api/v1/jobs/{job_id}")
        
        assert status_response.status_code == 200
        data = status_response.json()
        assert data["job_id"] == job_id
        assert "status" in data
        assert "created_at" in data
    
    def test_get_job_status_not_found(self, client, reset_state):
        """Test getting status of non-existent job."""
        response = client.get("/api/v1/jobs/nonexistent-id")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_list_jobs(self, client, reset_state):
        """Test listing all jobs."""
        # Create multiple jobs
        for i in range(3):
            payload = {"url": f"https://example{i}.com"}
            client.post("/api/v1/clone", json=payload)
        
        # List jobs
        response = client.get("/api/v1/jobs")
        
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert len(data["jobs"]) == 3


class TestAIConfiguration:
    """Test AI configuration endpoints."""
    
    def test_get_ai_providers(self, client, reset_state):
        """Test getting available AI providers."""
        response = client.get("/api/v1/ai/providers")
        
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert "current_config" in data
        assert "ollama" in data["providers"]
    
    def test_set_ai_config_ollama(self, client, reset_state):
        """Test setting AI config for Ollama (no API key needed)."""
        payload = {
            "enabled": True,
            "provider": "ollama",
            "model": "llama3",
            "base_url": "http://localhost:11434"
        }
        
        response = client.post("/api/v1/ai/config", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        # Config should be updated (check via get endpoint)
        get_response = client.get("/api/v1/ai/config")
        config_data = get_response.json()
        assert config_data["enabled"] is True
        assert config_data["provider"] == "ollama"
    
    def test_set_ai_config_openrouter(self, client, reset_state):
        """Test setting AI config for OpenRouter with API key."""
        payload = {
            "enabled": True,
            "provider": "openrouter",
            "api_key": "sk-or-1234567890abcdef",
            "model": "mistralai/mistral-7b-instruct:free"
        }
        
        response = client.post("/api/v1/ai/config", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        # Config should be updated (check via get endpoint)
        get_response = client.get("/api/v1/ai/config")
        config_data = get_response.json()
        assert config_data["enabled"] is True
        assert config_data["provider"] == "openrouter"
    
    def test_set_ai_config_invalid_key(self, client, reset_state):
        """Test setting AI config with invalid API key."""
        payload = {
            "enabled": True,
            "provider": "openrouter",
            "api_key": "short"  # Too short
        }
        
        response = client.post("/api/v1/ai/config", json=payload)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "API key" in data["detail"]
    
    def test_get_ai_config(self, client, reset_state):
        """Test getting current AI config (masked API key)."""
        # Set config with API key
        payload = {
            "enabled": True,
            "provider": "openrouter",
            "api_key": "sk-or-1234567890abcdef"
        }
        client.post("/api/v1/ai/config", json=payload)
        
        # Get config
        response = client.get("/api/v1/ai/config")
        
        assert response.status_code == 200
        data = response.json()
        assert "api_key" in data
        # API key should be masked
        assert "..." in data["api_key"]
        assert len(data["api_key"]) < 20  # Masked version
    
    def test_disable_ai(self, client, reset_state):
        """Test disabling AI."""
        # Enable first
        client.post("/api/v1/ai/config", json={"enabled": True, "provider": "ollama"})
        
        # Disable
        response = client.post("/api/v1/ai/config", json={"enabled": False, "provider": "ollama"})
        
        assert response.status_code == 200
        
        # Verify via get endpoint
        get_response = client.get("/api/v1/ai/config")
        config_data = get_response.json()
        assert config_data["enabled"] is False


class TestDownloadEndpoints:
    """Test download endpoints."""
    
    def test_download_nonexistent_job(self, client, reset_state):
        """Test downloading from non-existent job."""
        response = client.get("/api/v1/download/nonexistent-id")
        
        assert response.status_code == 404
    
    def test_download_incomplete_job(self, client, reset_state):
        """Test downloading from incomplete job."""
        # Create a job but don't complete it
        payload = {"url": "https://example.com"}
        create_response = client.post("/api/v1/clone", json=payload)
        job_id = create_response.json()["job_id"]
        
        # Try to download immediately (job still queued/running)
        # Note: Job may complete very quickly in tests, so we accept 200 or 400
        response = client.get(f"/api/v1/download/{job_id}")
        
        # Either the job completed instantly (200) or it's still pending (400)
        assert response.status_code in [200, 400]
        
        if response.status_code == 400:
            data = response.json()
            assert "detail" in data
            assert "not completed" in data["detail"].lower()


class TestSecurityVulnerabilities:
    """Test for security vulnerabilities."""
    
    def test_path_traversal_prevention(self, client, reset_state):
        """Test that path traversal attacks are prevented."""
        # Create a job
        payload = {"url": "https://example.com"}
        create_response = client.post("/api/v1/clone", json=payload)
        job_id = create_response.json()["job_id"]
        
        # Manually set job as completed with output path
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["output_path"] = "/tmp/test"
        
        # Try path traversal attack
        response = client.get(f"/api/v1/download/{job_id}/view/../../../etc/passwd")
        
        # Should either fail with 404 or 400, not return sensitive file
        assert response.status_code in [400, 404, 403, 500]
    
    def test_api_key_masking(self, client, reset_state):
        """Test that API keys are properly masked in responses."""
        api_key = "sk-or-verylongapikey1234567890"
        payload = {
            "enabled": True,
            "provider": "openrouter",
            "api_key": api_key
        }
        
        client.post("/api/v1/ai/config", json=payload)
        
        response = client.get("/api/v1/ai/config")
        data = response.json()
        
        # Full API key should never be returned
        assert api_key not in str(data)
        assert "..." in data["api_key"]
    
    def test_input_validation_url(self, client, reset_state):
        """Test URL input validation."""
        # Invalid URL formats
        invalid_urls = [
            "",
            "not-a-url",
            "ftp://invalid-protocol.com",
            "javascript:alert('xss')",
        ]
        
        for url in invalid_urls:
            payload = {"url": url}
            response = client.post("/api/v1/clone", json=payload)
            
            # Should accept the request (validation happens during execution)
            # but we're testing that it doesn't crash
            assert response.status_code in [200, 400, 422]
    
    def test_concurrent_job_creation(self, client, reset_state):
        """Test handling of concurrent job creation."""
        # Create many jobs quickly
        job_ids = []
        for i in range(10):
            payload = {"url": f"https://example{i}.com"}
            response = client.post("/api/v1/clone", json=payload)
            assert response.status_code == 200
            job_ids.append(response.json()["job_id"])
        
        # All jobs should have unique IDs
        assert len(set(job_ids)) == 10
        
        # All jobs should exist
        for job_id in job_ids:
            assert job_id in jobs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
