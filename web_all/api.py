"""
FastAPI backend for web-all.
Provides REST API and serves the web GUI.
"""

import asyncio
import json
import uuid
import zipfile
import io
from pathlib import Path
from typing import Dict, Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
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
    urls: Optional[List[str]] = None  # For batch processing


class JobStatus(BaseModel):
    job_id: str
    status: str  # pending, running, completed, failed
    progress: int = 0
    message: str = ""
    output_path: Optional[str] = None


# Global job storage (in production, use Redis/database)
jobs: Dict[str, dict] = {}

app = FastAPI(title="web-all API", version="1.0.0")

# Mount GUI static files
gui_path = Path(__file__).parent / "gui"
if gui_path.exists():
    app.mount("/gui", StaticFiles(directory=str(gui_path), html=True), name="gui")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main GUI."""
    gui_file = Path(__file__).parent / "gui" / "index.html"
    if gui_file.exists():
        return HTMLResponse(content=gui_file.read_text(encoding="utf-8"))
    raise HTTPException(status_code=404, detail="GUI not found")


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


@app.get("/api/v1/jobs")
async def list_jobs():
    """List all jobs."""
    return {
        "jobs": [
            {
                "job_id": j["job_id"],
                "status": j["status"],
                "progress": j["progress"],
                "url": j["params"].get("url"),
                "mode": j["params"].get("mode"),
            }
            for j in jobs.values()
        ]
    }


@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job status."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = jobs[job_id]
    return JobStatus(**job_data)


@app.delete("/api/v1/jobs/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if jobs[job_id]["status"] in ["pending", "running"]:
        jobs[job_id]["status"] = "cancelled"
        jobs[job_id]["message"] = "Job cancelled by user"
        return {"message": "Job cancelled"}
    
    raise HTTPException(status_code=400, detail="Job cannot be cancelled")


@app.get("/api/v1/download/{job_id}")
async def download_result(job_id: str):
    """Download job result as ZIP."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = jobs[job_id]
    if job_data["status"] != "completed" or not job_data["output_path"]:
        raise HTTPException(status_code=400, detail="Job not completed")
    
    output_path = Path(job_data["output_path"])
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Output directory not found")
    
    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in output_path.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(output_path)
                zipf.write(file_path, arcname)
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=web-all-{job_id}.zip"}
    )


@app.get("/api/v1/export/{job_id}/{format}")
async def export_result(job_id: str, format: str):
    """Export job results in different formats (json, csv)."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = jobs[job_id]
    if job_data["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")
    
    output_path = Path(job_data["output_path"])
    
    if format.lower() == "json":
        # Export metadata about downloaded files
        files_info = []
        for file_path in output_path.rglob('*'):
            if file_path.is_file():
                files_info.append({
                    "path": str(file_path.relative_to(output_path)),
                    "size": file_path.stat().st_size,
                })
        
        return StreamingResponse(
            io.StringIO(json.dumps(files_info, indent=2)),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=export-{job_id}.json"}
        )
    elif format.lower() == "csv":
        # Export as CSV
        import csv
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["path", "size"])
        
        for file_path in output_path.rglob('*'):
            if file_path.is_file():
                writer.writerow([
                    str(file_path.relative_to(output_path)),
                    file_path.stat().st_size
                ])
        
        return StreamingResponse(
            io.StringIO(output.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=export-{job_id}.csv"}
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")


async def run_job(job_id: str, job: CloneJob):
    """Run the actual cloning job."""
    try:
        jobs[job_id]["status"] = "running"
        jobs[job_id]["message"] = "Starting clone..."
        
        if job.mode == "batch" and job.urls:
            # Batch processing mode
            from .cloner import WebsiteCloner
            
            total_urls = len(job.urls)
            for i, url in enumerate(job.urls):
                jobs[job_id]["progress"] = int((i / total_urls) * 100)
                jobs[job_id]["message"] = f"Processing {i+1}/{total_urls}: {url}"
                
                output_dir = Path(job.output) / f"site_{i}"
                cloner = WebsiteCloner(
                    base_url=url,
                    output_dir=str(output_dir),
                    depth=job.depth,
                    concurrency=job.concurrency,
                    delay=job.delay,
                )
                await cloner.clone_site()
            
            jobs[job_id]["progress"] = 100
        else:
            # Single URL mode
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
        import traceback
        print(f"Job {job_id} failed: {traceback.format_exc()}")


def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the FastAPI server."""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
