"""
FastAPI REST API server for web-all.
Provides endpoints for cloning jobs, status tracking, AI configuration, and file downloads.
"""

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ..core.cloner import SiteCloner
from ..core.invisible import InvisibleContentEngine
from ..utils.ai_engine import AIEngine, get_available_providers
from ..utils.zip_utils import create_zip_archive

app = FastAPI(
    title="web-all API v4.5.0",
    version="4.5.0",
    description="Worldwide Website Cloner with Multi-Language Support & AI",
)

# GUI directory used for serving the frontend at /
GUI_DIR: Optional[str] = None

# Job storage
jobs: Dict[str, Dict[str, Any]] = {}

# AI Configuration storage (in-memory, can be persisted)
ai_config: Dict[str, Any] = {
    "enabled": False,
    "provider": "ollama",
    "api_key": "",
    "model": "",
    "base_url": "http://localhost:11434",
}

# Output directory
OUTPUT_DIR = Path("./output")
OUTPUT_DIR.mkdir(exist_ok=True)


def validate_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("Invalid URL: must be http:// or https://")
    return url


class CloneRequest(BaseModel):
    url: str
    mode: str = "static"
    depth: int = 2
    use_tor: bool = False
    discover_invisible: bool = False
    ai_enabled: bool = False
    everything: bool = False
    max_pages: int = 1000
    output_name: Optional[str] = None


class AIConfigRequest(BaseModel):
    enabled: bool
    provider: str
    api_key: Optional[str] = ""
    model: Optional[str] = ""
    base_url: Optional[str] = "http://localhost:11434"


async def run_clone_job(job_id: str, request: CloneRequest):
    """Background task to run cloning job."""
    try:
        jobs[job_id]["status"] = "running"
        jobs[job_id]["started_at"] = datetime.now().isoformat()

        output_name = request.output_name or f"clone_{job_id[:8]}"
        output_path = OUTPUT_DIR / output_name

        # Initialize AI engine if enabled
        ai_engine = None
        if request.ai_enabled and ai_config.get("enabled"):
            ai_engine = AIEngine(ai_config)
            jobs[job_id]["ai_status"] = "AI enabled"

        if request.mode == "everything" or request.everything:
            jobs[job_id]["everything"] = True
            request = request.copy(
                update={
                    "discover_invisible": True,
                    "mode": "dynamic",
                    "depth": max(request.depth, 5),
                    "ai_enabled": True,
                }
            )

        if request.mode == "deep-crawl":
            request = request.copy(
                update={
                    "discover_invisible": True,
                    "mode": "dynamic",
                    "depth": max(request.depth, 5),
                }
            )

        cloner = SiteCloner(
            output_dir=str(output_path),
            depth=request.depth,
            use_tor=request.use_tor,
            max_pages=request.max_pages,
        )

        if request.discover_invisible and request.mode in ["static", "dynamic"]:
            engine = InvisibleContentEngine(use_tor=request.use_tor)
            # First expand content, then clone
            expanded_html = await engine.expand_all_content(request.url)
            (output_path / "expanded.html").write_text(expanded_html)

        if request.mode == "images":
            html = await cloner.fetch_page(request.url)
            if not html:
                raise Exception("Failed to fetch page for image download")
            assets = cloner.extract_assets(html, request.url)
            image_urls = assets.get("images", [])
            for image_url in image_urls:
                cloner.save_asset(image_url, "images")
            manifest = {
                "mode": "images",
                "image_count": cloner.stats["images"],
                "source_url": request.url,
            }
        elif request.mode == "text":
            html = await cloner.fetch_page(request.url)
            if not html:
                raise Exception("Failed to fetch page for text extraction")
            from urllib.parse import urlparse

            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "lxml")
            for tag in soup(["script", "style"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
            output_path.mkdir(parents=True, exist_ok=True)
            parsed = urlparse(request.url)
            out_file = output_path / f"{parsed.netloc.replace('.', '_')}.txt"
            out_file.write_text(text, encoding="utf-8")
            manifest = {"mode": "text", "source_url": request.url, "characters": len(text)}
        else:
            manifest = await cloner.clone_site(request.url, mode=request.mode)

        # Run AI analysis if enabled
        if ai_engine:
            try:
                index_html = output_path / "index.html"
                if index_html.exists():
                    html_content = index_html.read_text(encoding="utf-8")
                    await ai_engine.analyze_and_enhance(html_content, request.url, output_path)
                    jobs[job_id]["ai_completed"] = True
            except Exception as ai_error:
                jobs[job_id]["ai_error"] = str(ai_error)

        jobs[job_id].update(
            {
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "manifest": manifest,
                "output_path": str(output_path),
            }
        )

    except Exception as e:
        jobs[job_id].update(
            {"status": "failed", "error": str(e), "failed_at": datetime.now().isoformat()}
        )


@app.get("/")
async def root():
    """Serve the GUI when available, otherwise show API health."""
    if GUI_DIR and Path(GUI_DIR).exists():
        index_file = Path(GUI_DIR) / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file), media_type="text/html")

    return {
        "message": "web-all v4.5.0 API is running",
        "version": "4.5.0",
        "features": [
            "Worldwide website cloning",
            "Multi-language support (11 languages)",
            "Tor/.onion support",
            "AI integration (5 providers)",
            "Hidden content discovery",
            "Auto-organize assets",
            "ZIP export"
        ]
    }


@app.get("/api/v1/health")
async def api_health():
    """API health check endpoint."""
    return {
        "message": "web-all v4.5.0 API is running",
        "version": "4.5.0",
        "status": "healthy"
    }


@app.post("/api/v1/clone")
async def create_clone_job(request: CloneRequest, background_tasks: BackgroundTasks):
    """Create a new cloning job."""
    if request.max_pages < 1:
        raise HTTPException(status_code=400, detail="max_pages must be at least 1")

    try:
        validate_url(request.url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "id": job_id,
        "request": request.model_dump(),
        "status": "queued",
        "created_at": datetime.now().isoformat(),
    }

    background_tasks.add_task(run_clone_job, job_id, request)

    return {"job_id": job_id, "status": "queued", "message": "Job created successfully"}


@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get status of a cloning job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    response = {"job_id": job_id, "status": job["status"], "created_at": job["created_at"]}

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
    """Download the cloned site as a ZIP file or access individual files."""
    import tempfile

    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")

    output_path = Path(job.get("output_path", ""))

    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Output not found")

    # Create ZIP archive for download
    try:
        temp_dir = tempfile.mkdtemp()
        zip_path = Path(temp_dir) / f"{output_path.name}.zip"
        create_zip_archive(str(output_path), str(zip_path))

        return FileResponse(
            str(zip_path), media_type="application/zip", filename=f"{output_path.name}.zip"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create ZIP: {str(e)}")


@app.get("/api/v1/download/{job_id}/view/{filename:path}")
async def view_file(job_id: str, filename: str):
    """View a specific file from the cloned site."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")

    output_path = Path(job.get("output_path", ""))
    file_path = output_path / filename
    resolved_output = output_path.resolve()
    resolved_file = file_path.resolve()
    if not str(resolved_file).startswith(str(resolved_output)):
        raise HTTPException(status_code=400, detail="Invalid filename")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Determine media type based on extension
    media_types = {
        ".html": "text/html",
        ".css": "text/css",
        ".js": "application/javascript",
        ".json": "application/json",
        ".txt": "text/plain",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".pdf": "application/pdf",
    }

    ext = file_path.suffix.lower()
    media_type = media_types.get(ext, "application/octet-stream")

    return FileResponse(str(file_path), media_type=media_type)


@app.get("/api/v1/jobs")
async def list_jobs():
    """List all jobs."""
    return {
        "jobs": [
            {
                "job_id": job_id,
                "status": job["status"],
                "url": job["request"]["url"],
                "created_at": job["created_at"],
                "ai_enabled": job.get("ai_status", "") != "",
                "ai_completed": job.get("ai_completed", False),
            }
            for job_id, job in jobs.items()
        ]
    }


@app.get("/api/v1/ai/providers")
async def get_ai_providers():
    """Get available AI providers."""
    return {"providers": get_available_providers(), "current_config": ai_config}


@app.post("/api/v1/ai/config")
async def set_ai_config(config: AIConfigRequest):
    """Configure AI settings."""
    global ai_config

    # Validate API key if required
    if config.enabled and config.provider != "ollama":
        if not config.api_key or len(config.api_key) < 10:
            raise HTTPException(status_code=400, detail="Valid API key required for this provider")

    # Additional validation for NVIDIA
    if config.enabled and config.provider == "nvidia":
        if not config.api_key or len(config.api_key) < 10:
            raise HTTPException(
                status_code=400, detail="Valid NVIDIA API key required (get from build.nvidia.com)"
            )

    ai_config = {
        "enabled": config.enabled,
        "provider": config.provider,
        "api_key": config.api_key or "",
        "model": config.model or "",
        "base_url": config.base_url or "http://localhost:11434",
    }

    return {"message": "AI configuration updated successfully", "config": ai_config}


@app.get("/api/v1/ai/config")
async def get_ai_config():
    """Get current AI configuration (without exposing full API key)."""
    safe_config = ai_config.copy()
    if safe_config.get("api_key") and len(safe_config["api_key"]) > 4:
        safe_config["api_key"] = safe_config["api_key"][:4] + "..." + safe_config["api_key"][-4:]
    return safe_config


@app.post("/api/v1/ai/test")
async def test_ai_connection():
    """Test AI connection with a simple prompt."""
    if not ai_config.get("enabled"):
        raise HTTPException(status_code=400, detail="AI is not enabled")

    try:
        engine = AIEngine(ai_config)
        response = await engine.summarize_content("<p>Hello, this is a test.</p>", "test://url")
        return {
            "success": True,
            "message": "AI connection successful",
            "sample_response": response[:200] if response else "No response generated",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI test failed: {str(e)}")


def start_api(host: str = "0.0.0.0", port: int = 8000, gui_dir: Optional[str] = None):
    """Start the API server with optional GUI serving."""
    import uvicorn

    global GUI_DIR
    GUI_DIR = gui_dir

    # Mount GUI if directory provided
    if gui_dir and os.path.exists(gui_dir):
        app.mount("/", StaticFiles(directory=gui_dir, html=True), name="gui")

    print(f"Starting web-all API on http://{host}:{port}")
    if gui_dir:
        print(f"Serving GUI from {gui_dir}")

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_api()
