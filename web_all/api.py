"""
FastAPI backend for web-all.
Provides REST API and serves the web GUI.
"""

import asyncio
import json
import uuid
from pathlib import Path
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import uvicorn


class CloneJob(BaseModel):
    url: str
    mode: str = "clone"
    output: str = "./output"
    depth: int = 5
    concurrency: int = 5
    delay: float = 1.0
    discover_invisible: bool = False


class JobStatus(BaseModel):
    job_id: str
    status: str  # pending, running, completed, failed
    progress: int = 0
    message: str = ""
    output_path: Optional[str] = None


# Global job storage (in production, use Redis/database)
jobs: Dict[str, dict] = {}

app = FastAPI(title="web-all API", version="1.0.0")


@app.post("/api/v1/jobs")
async def create_job(job: CloneJob):
    """Create a new cloning job."""
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "progress": 0,
        "message": "Job queued",
        "params": job.dict(),
        "output_path": None,
    }
    
    # Start job in background
    asyncio.create_task(run_job(job_id, job))
    
    return {"job_id": job_id, "status": "pending"}


@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job status."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = jobs[job_id]
    return JobStatus(**job_data)


@app.get("/api/v1/download/{job_id}")
async def download_result(job_id: str):
    """Download job result as ZIP."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = jobs[job_id]
    if job_data["status"] != "completed" or not job_data["output_path"]:
        raise HTTPException(status_code=400, detail="Job not completed")
    
    # TODO: Create ZIP and return
    return {"message": "Download coming soon"}


async def run_job(job_id: str, job: CloneJob):
    """Run the actual cloning job."""
    try:
        jobs[job_id]["status"] = "running"
        jobs[job_id]["message"] = "Starting clone..."
        
        from .cloner import WebsiteCloner
        
        cloner = WebsiteCloner(
            base_url=job.url,
            output_dir=job.output,
            depth=job.depth,
            concurrency=job.concurrency,
            delay=job.delay,
        )
        
        await cloner.clone_site()
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["message"] = "Completed"
        jobs[job_id]["output_path"] = job.output
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["message"] = str(e)


def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the FastAPI server."""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
