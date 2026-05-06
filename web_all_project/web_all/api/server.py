"""
FastAPI REST API server for web-all.
Provides endpoints for cloning jobs, status tracking, and file downloads.
"""

import os
import json
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ..core.cloner import SiteCloner
from ..core.invisible import InvisibleContentEngine

app = FastAPI(title="web-all API", version="2.0.0")

# Job storage
jobs: Dict[str, Dict[str, Any]] = {}

# Output directory
OUTPUT_DIR = Path("./output")
OUTPUT_DIR.mkdir(exist_ok=True)


class CloneRequest(BaseModel):
    url: str
    mode: str = "static"
    depth: int = 2
    use_tor: bool = False
    discover_invisible: bool = False
    output_name: Optional[str] = None


async def run_clone_job(job_id: str, request: CloneRequest):
    """Background task to run cloning job."""
    try:
        jobs[job_id]["status"] = "running"
        jobs[job_id]["started_at"] = datetime.now().isoformat()
        
        output_name = request.output_name or f"clone_{job_id[:8]}"
        output_path = OUTPUT_DIR / output_name
        
        cloner = SiteCloner(
            output_dir=str(output_path),
            depth=request.depth,
            use_tor=request.use_tor
        )
        
        if request.discover_invisible:
            engine = InvisibleContentEngine(use_tor=request.use_tor)
            # First expand content, then clone
            expanded_html = await engine.expand_all_content(request.url)
            # Save expanded page
            (output_path / "expanded.html").write_text(expanded_html)
        
        manifest = await cloner.clone_site(request.url, mode=request.mode)
        
        jobs[job_id].update({
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "manifest": manifest,
            "output_path": str(output_path)
        })
        
    except Exception as e:
        jobs[job_id].update({
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        })


@app.get("/")
async def root():
    """API health check."""
    return {"message": "web-all API is running", "version": "2.0.0"}


@app.post("/api/v1/clone")
async def create_clone_job(request: CloneRequest, background_tasks: BackgroundTasks):
    """Create a new cloning job."""
    job_id = str(uuid.uuid4())
    
    jobs[job_id] = {
        "id": job_id,
        "request": request.dict(),
        "status": "queued",
        "created_at": datetime.now().isoformat()
    }
    
    background_tasks.add_task(run_clone_job, job_id, request)
    
    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Job created successfully"
    }


@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get status of a cloning job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    response = {
        "job_id": job_id,
        "status": job["status"],
        "created_at": job["created_at"]
    }
    
    if "started_at" in job:
        response["started_at"] = job["started_at"]
    
    if "completed_at" in job:
        response["completed_at"] = job["completed_at"]
    
    if "manifest" in job:
        response["manifest"] = job["manifest"]
    
    if "error" in job:
        response["error"] = job["error"]
    
    if job["status"] == "completed" and "output_path" in job:
        response["download_url"] = f"/api/v1/download/{job_id}"
    
    return response


@app.get("/api/v1/download/{job_id}")
async def download_job_output(job_id: str):
    """Download the cloned site as a ZIP (future) or access directory."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")
    
    output_path = Path(job.get("output_path", ""))
    
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Output not found")
    
    # Return index.html if exists
    index_file = output_path / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file), media_type="text/html")
    
    # Otherwise return manifest
    manifest_file = output_path / "manifest.json"
    if manifest_file.exists():
        return FileResponse(str(manifest_file), media_type="application/json")
    
    raise HTTPException(status_code=404, detail="No downloadable content found")


@app.get("/api/v1/jobs")
async def list_jobs():
    """List all jobs."""
    return {
        "jobs": [
            {
                "job_id": job_id,
                "status": job["status"],
                "url": job["request"]["url"],
                "created_at": job["created_at"]
            }
            for job_id, job in jobs.items()
        ]
    }


def start_api(host: str = "0.0.0.0", port: int = 8000, gui_dir: Optional[str] = None):
    """Start the API server with optional GUI serving."""
    import uvicorn
    
    # Mount GUI if directory provided
    if gui_dir and os.path.exists(gui_dir):
        app.mount("/", StaticFiles(directory=gui_dir, html=True), name="gui")
    
    print(f"Starting web-all API on http://{host}:{port}")
    if gui_dir:
        print(f"Serving GUI from {gui_dir}")
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_api()
