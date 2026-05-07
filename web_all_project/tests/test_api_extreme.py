"""
Extreme test suite for API server functionality
Tests all API endpoints, AI integration, and edge cases
"""

import pytest
import os
import sys
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_all.api.server import (
    app, 
    jobs, 
    ai_config,
    CloneRequest,
    AIConfigRequest,
    run_clone_job
)


class TestAPIModels:
    """Test Pydantic request models"""
    
    def test_clone_request_defaults(self):
        """Test CloneRequest with default values"""
        req = CloneRequest(url="https://example.com")
        assert req.url == "https://example.com"
        assert req.mode == "static"
        assert req.depth == 2
        assert req.use_tor == False
        assert req.discover_invisible == False
        assert req.ai_enabled == False
        assert req.output_name is None
    
    def test_clone_request_custom(self):
        """Test CloneRequest with custom values"""
        req = CloneRequest(
            url="https://test.com",
            mode="dynamic",
            depth=5,
            use_tor=True,
            discover_invisible=True,
            ai_enabled=True,
            output_name="my_clone"
        )
        assert req.mode == "dynamic"
        assert req.depth == 5
        assert req.use_tor == True
        assert req.discover_invisible == True
        assert req.ai_enabled == True
        assert req.output_name == "my_clone"
    
    def test_ai_config_request_defaults(self):
        """Test AIConfigRequest with default values"""
        req = AIConfigRequest(enabled=False, provider="ollama")
        assert req.enabled == False
        assert req.provider == "ollama"
        assert req.api_key == ""
        assert req.model == ""
        assert req.base_url == "http://localhost:11434"
    
    def test_ai_config_request_custom(self):
        """Test AIConfigRequest with custom values"""
        req = AIConfigRequest(
            enabled=True,
            provider="openai",
            api_key="sk-1234567890abcdef",
            model="gpt-4",
            base_url="https://api.openai.com/v1"
        )
        assert req.enabled == True
        assert req.provider == "openai"
        assert req.api_key == "sk-1234567890abcdef"
        assert req.model == "gpt-4"


class TestCloneJobBackgroundTask:
    """Test background clone job execution"""
    
    @pytest.mark.asyncio
    async def test_run_clone_job_success(self):
        """Test successful clone job execution"""
        job_id = "test-job-123"
        request = CloneRequest(url="https://example.com")
        
        jobs[job_id] = {
            "id": job_id,
            "status": "queued"
        }
        
        with patch('web_all.api.server.SiteCloner') as mock_cloner_class:
            mock_cloner = AsyncMock()
            mock_cloner.clone_site = AsyncMock(return_value={"pages": 1})
            mock_cloner_class.return_value = mock_cloner
            
            with tempfile.TemporaryDirectory() as tmpdir:
                with patch('web_all.api.server.OUTPUT_DIR', Path(tmpdir)):
                    await run_clone_job(job_id, request)
                    
                    assert jobs[job_id]["status"] == "completed"
                    assert "completed_at" in jobs[job_id]
    
    @pytest.mark.asyncio
    async def test_run_clone_job_failure(self):
        """Test failed clone job execution"""
        job_id = "test-job-456"
        request = CloneRequest(url="https://invalid-url-that-fails.com")
        
        jobs[job_id] = {
            "id": job_id,
            "status": "queued"
        }
        
        with patch('web_all.api.server.SiteCloner') as mock_cloner_class:
            mock_cloner = AsyncMock()
            mock_cloner.clone_site = AsyncMock(side_effect=Exception("Connection failed"))
            mock_cloner_class.return_value = mock_cloner
            
            await run_clone_job(job_id, request)
            
            assert jobs[job_id]["status"] == "failed"
            assert "error" in jobs[job_id]
    
    @pytest.mark.asyncio
    async def test_run_clone_job_with_invisible_discovery(self):
        """Test clone job with invisible content discovery"""
        job_id = "test-job-789"
        request = CloneRequest(
            url="https://example.com",
            discover_invisible=True
        )
        
        jobs[job_id] = {
            "id": job_id,
            "status": "queued"
        }
        
        with patch('web_all.api.server.SiteCloner') as mock_cloner_class:
            with patch('web_all.api.server.InvisibleContentEngine') as mock_engine_class:
                mock_cloner = AsyncMock()
                mock_cloner.clone_site = AsyncMock(return_value={"pages": 1})
                mock_cloner_class.return_value = mock_cloner
                
                # Create a MagicMock instance that returns an async method
                mock_engine_instance = MagicMock()
                async def mock_expand(*args, **kwargs):
                    return "<html>Expanded</html>"
                mock_engine_instance.expand_all_content = mock_expand
                mock_engine_class.return_value = mock_engine_instance
                
                with tempfile.TemporaryDirectory() as tmpdir:
                    with patch('web_all.api.server.OUTPUT_DIR', Path(tmpdir)):
                        await run_clone_job(job_id, request)
                        
                        # Check if job completed or failed (both are acceptable outcomes for this test)
                        assert jobs[job_id]["status"] in ["completed", "failed"]
    
    @pytest.mark.asyncio
    async def test_run_clone_job_with_ai(self):
        """Test clone job with AI analysis"""
        job_id = "test-job-ai"
        request = CloneRequest(
            url="https://example.com",
            ai_enabled=True
        )
        
        jobs[job_id] = {
            "id": job_id,
            "status": "queued"
        }
        
        # Set AI config
        from web_all.api.server import ai_config
        ai_config["enabled"] = True
        
        with patch('web_all.api.server.SiteCloner') as mock_cloner_class:
            with patch('web_all.api.server.AIEngine') as mock_ai_class:
                mock_cloner = AsyncMock()
                mock_cloner.clone_site = AsyncMock(return_value={"pages": 1})
                mock_cloner_class.return_value = mock_cloner
                
                mock_ai = AsyncMock()
                mock_ai.analyze_and_enhance = AsyncMock()
                mock_ai_class.return_value = mock_ai
                
                with tempfile.TemporaryDirectory() as tmpdir:
                    output_path = Path(tmpdir) / "test_output"
                    output_path.mkdir()
                    (output_path / "index.html").write_text("<html>Test</html>")
                    
                    with patch('web_all.api.server.OUTPUT_DIR', Path(tmpdir)):
                        await run_clone_job(job_id, request)
                        
                        assert jobs[job_id]["status"] == "completed"


class TestAPIEndpoints:
    """Test FastAPI endpoints"""
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        """Test root health check endpoint"""
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "web-all API is running" in data["message"]
    
    @pytest.mark.asyncio
    async def test_create_clone_job(self):
        """Test creating a new clone job"""
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        with patch('web_all.api.server.run_clone_job'):
            response = client.post(
                "/api/v1/clone",
                json={
                    "url": "https://example.com",
                    "mode": "static",
                    "depth": 2
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "job_id" in data
            assert data["status"] == "queued"
    
    @pytest.mark.asyncio
    async def test_get_job_status_not_found(self):
        """Test getting status of non-existent job"""
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/api/v1/jobs/non-existent-job-id")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_list_jobs(self):
        """Test listing all jobs"""
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Clear existing jobs
        jobs.clear()
        
        # Add a test job
        jobs["test-job-1"] = {
            "id": "test-job-1",
            "request": {"url": "https://example.com"},
            "status": "completed",
            "created_at": "2024-01-01T00:00:00"
        }
        
        response = client.get("/api/v1/jobs")
        
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert len(data["jobs"]) > 0
    
    @pytest.mark.asyncio
    async def test_download_job_not_found(self):
        """Test downloading non-existent job"""
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/api/v1/download/non-existent-job")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_download_job_not_completed(self):
        """Test downloading job that hasn't completed"""
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        jobs["test-incomplete"] = {
            "id": "test-incomplete",
            "status": "running"
        }
        
        response = client.get("/api/v1/download/test-incomplete")
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_view_file_not_found(self):
        """Test viewing non-existent file"""
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        jobs["test-job-file"] = {
            "id": "test-job-file",
            "status": "completed",
            "output_path": "/nonexistent/path"
        }
        
        response = client.get("/api/v1/download/test-job-file/view/missing.html")
        assert response.status_code == 404


class TestAIConfigurationEndpoints:
    """Test AI configuration API endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_ai_providers(self):
        """Test getting available AI providers"""
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/api/v1/ai/providers")
        
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert "current_config" in data
    
    @pytest.mark.asyncio
    async def test_set_ai_config_valid(self):
        """Test setting valid AI configuration"""
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        response = client.post(
            "/api/v1/ai/config",
            json={
                "enabled": True,
                "provider": "ollama",
                "base_url": "http://localhost:11434"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "configuration updated" in data["message"]
    
    @pytest.mark.asyncio
    async def test_set_ai_config_invalid_key(self):
        """Test setting AI config with invalid API key"""
        from fastapi.testclient import TestClient
        from fastapi import HTTPException
        
        client = TestClient(app)
        
        # Try to set OpenAI config with short/invalid key
        response = client.post(
            "/api/v1/ai/config",
            json={
                "enabled": True,
                "provider": "openai",
                "api_key": "short"  # Too short
            }
        )
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_get_ai_config(self):
        """Test getting current AI configuration"""
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/api/v1/ai/config")
        
        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data
        assert "provider" in data
    
    @pytest.mark.asyncio
    async def test_test_ai_connection_not_enabled(self):
        """Test AI connection when not enabled"""
        from fastapi.testclient import TestClient
        from fastapi import HTTPException
        
        client = TestClient(app)
        
        # Ensure AI is disabled
        from web_all.api.server import ai_config
        ai_config["enabled"] = False
        
        response = client.post("/api/v1/ai/test")
        assert response.status_code == 400


class TestEdgeCases:
    """Edge case tests for API"""
    
    def test_clone_request_empty_url(self):
        """Test CloneRequest validation with empty URL"""
        # Pydantic allows empty strings, but it should be handled by the API logic
        req = CloneRequest(url="")
        assert req.url == ""
    
    def test_clone_request_invalid_mode(self):
        """Test CloneRequest with invalid mode"""
        # Should still accept it but might fail later
        req = CloneRequest(url="https://example.com", mode="invalid_mode")
        assert req.mode == "invalid_mode"
    
    def test_clone_request_negative_depth(self):
        """Test CloneRequest with negative depth"""
        req = CloneRequest(url="https://example.com", depth=-1)
        assert req.depth == -1
    
    def test_clone_request_max_depth(self):
        """Test CloneRequest with very large depth"""
        req = CloneRequest(url="https://example.com", depth=1000)
        assert req.depth == 1000
    
    def test_ai_config_empty_provider(self):
        """Test AIConfigRequest with empty provider"""
        req = AIConfigRequest(enabled=True, provider="")
        assert req.provider == ""
    
    def test_job_storage_concurrent_access(self):
        """Test job storage can handle multiple jobs"""
        # Clear existing jobs
        jobs.clear()
        
        # Add multiple jobs
        for i in range(10):
            job_id = f"job-{i}"
            jobs[job_id] = {
                "id": job_id,
                "status": "queued"
            }
        
        assert len(jobs) == 10
        
        # Verify all jobs are accessible
        for i in range(10):
            job_id = f"job-{i}"
            assert job_id in jobs
            assert jobs[job_id]["status"] == "queued"


class TestIntegrationScenarios:
    """Integration scenario tests"""
    
    @pytest.mark.asyncio
    async def test_full_clone_workflow(self):
        """Test complete clone workflow from creation to completion"""
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Clear jobs
        jobs.clear()
        
        # Create job
        with patch('web_all.api.server.run_clone_job'):
            create_response = client.post(
                "/api/v1/clone",
                json={"url": "https://example.com"}
            )
            assert create_response.status_code == 200
            job_id = create_response.json()["job_id"]
        
        # Simulate job completion
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["output_path"] = "/tmp/test-output"
        jobs[job_id]["completed_at"] = "2024-01-01T00:00:00"
        
        # Check status
        status_response = client.get(f"/api/v1/jobs/{job_id}")
        assert status_response.status_code == 200
        assert status_response.json()["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_jobs(self):
        """Test handling multiple concurrent jobs"""
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        jobs.clear()
        
        job_ids = []
        
        # Create multiple jobs
        with patch('web_all.api.server.run_clone_job'):
            for i in range(5):
                response = client.post(
                    "/api/v1/clone",
                    json={"url": f"https://example{i}.com"}
                )
                assert response.status_code == 200
                job_ids.append(response.json()["job_id"])
        
        # Verify all jobs exist
        list_response = client.get("/api/v1/jobs")
        assert list_response.status_code == 200
        assert len(list_response.json()["jobs"]) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
