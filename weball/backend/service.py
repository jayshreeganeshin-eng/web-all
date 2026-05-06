"""
Backend Service - Core business logic and API integration
Handles cloning jobs, user sessions, and data management
"""

import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from fastapi import BackgroundTasks

from ..core.cloner import SiteCloner
from ..core.invisible import InvisibleContentEngine
from ..utils.ai_engine import AIEngine


class BackendService:
    """Main backend service for weball application."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.output_dir = Path(self.config.get("output_dir", "./output"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # AI Configuration
        self.ai_config = {
            "enabled": True,  # Auto-enabled by default
            "provider": "ollama",  # Free local AI
            "api_key": "",
            "model": "llama3",
            "base_url": "http://localhost:11434"
        }
    
    async def create_clone_job(
        self,
        url: str,
        mode: str = "static",
        depth: int = 2,
        use_tor: bool = False,
        discover_invisible: bool = False,
        ai_enabled: bool = True,
        output_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new website cloning job."""
        job_id = str(uuid.uuid4())
        
        self.jobs[job_id] = {
            "id": job_id,
            "url": url,
            "mode": mode,
            "depth": depth,
            "use_tor": use_tor,
            "discover_invisible": discover_invisible,
            "ai_enabled": ai_enabled,
            "status": "queued",
            "created_at": datetime.now().isoformat(),
            "progress": 0
        }
        
        return {"job_id": job_id, "status": "queued"}
    
    async def run_clone_job(self, job_id: str, background_tasks: BackgroundTasks):
        """Execute a cloning job in the background."""
        if job_id not in self.jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.jobs[job_id]
        job["status"] = "running"
        job["started_at"] = datetime.now().isoformat()
        
        try:
            output_name = job.get("output_name") or f"clone_{job_id[:8]}"
            output_path = self.output_dir / output_name
            
            # Initialize AI engine if enabled
            ai_engine = None
            if job.get("ai_enabled") and self.ai_config.get("enabled"):
                ai_engine = AIEngine(self.ai_config)
                job["ai_status"] = "AI enabled"
            
            # Initialize cloner
            cloner = SiteCloner(
                output_dir=str(output_path),
                depth=job["depth"],
                use_tor=job["use_tor"]
            )
            
            # Discover invisible content if requested
            if job.get("discover_invisible"):
                engine = InvisibleContentEngine(use_tor=job["use_tor"])
                expanded_html = await engine.expand_all_content(job["url"])
                (output_path / "expanded.html").write_text(expanded_html)
            
            # Run cloning
            manifest = await cloner.clone_site(job["url"], mode=job["mode"])
            
            # Run AI analysis if enabled
            if ai_engine:
                try:
                    index_html = output_path / "index.html"
                    if index_html.exists():
                        html_content = index_html.read_text(encoding='utf-8')
                        await ai_engine.analyze_and_enhance(html_content, job["url"], output_path)
                        job["ai_completed"] = True
                except Exception as ai_error:
                    job["ai_error"] = str(ai_error)
            
            # Mark job as completed
            job.update({
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "manifest": manifest,
                "output_path": str(output_path),
                "progress": 100
            })
            
        except Exception as e:
            job.update({
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            })
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a cloning job."""
        if job_id not in self.jobs:
            return None
        
        job = self.jobs[job_id]
        response = {
            "job_id": job_id,
            "status": job["status"],
            "created_at": job["created_at"],
            "progress": job.get("progress", 0)
        }
        
        if "started_at" in job:
            response["started_at"] = job["started_at"]
        if "completed_at" in job:
            response["completed_at"] = job["completed_at"]
        if "manifest" in job:
            response["manifest"] = job["manifest"]
        if "error" in job:
            response["error"] = job["error"]
        if "output_path" in job:
            response["download_url"] = f"/api/v1/download/{job_id}"
        
        return response
    
    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all jobs."""
        return [
            {
                "job_id": job_id,
                "url": job["url"],
                "status": job["status"],
                "created_at": job["created_at"],
                "ai_enabled": job.get("ai_enabled", False)
            }
            for job_id, job in self.jobs.items()
        ]
    
    def configure_ai(self, provider: str, api_key: str = "", model: str = "", base_url: str = ""):
        """Configure AI settings."""
        self.ai_config["provider"] = provider
        if api_key:
            self.ai_config["api_key"] = api_key
        if model:
            self.ai_config["model"] = model
        if base_url:
            self.ai_config["base_url"] = base_url
        self.ai_config["enabled"] = True
    
    def disable_ai(self):
        """Disable AI features."""
        self.ai_config["enabled"] = False


# Global backend instance
backend_service = BackendService()
