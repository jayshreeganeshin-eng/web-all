"""
FastAPI REST API server for web-all v4.0.
Provides endpoints for cloning jobs, status tracking, AI configuration, user authentication, and admin panel.
"""

import os
import json
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Header, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ..core.cloner import SiteCloner
from ..core.invisible import InvisibleContentEngine
from ..utils.ai_engine import AIEngine, get_available_providers, validate_api_key
from ..utils.zip_utils import create_zip_archive
from ..utils.auth import AuthManager, UserRole

app = FastAPI(title="web-all API", version="4.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize authentication manager
auth_manager = AuthManager()

# Job storage
jobs: Dict[str, Dict[str, Any]] = {}

# AI Configuration storage (in-memory, can be persisted)
ai_config: Dict[str, Any] = {
    "enabled": False,
    "provider": "ollama",
    "api_key": "",
    "model": "",
    "base_url": "http://localhost:11434"
}

# Output directory
OUTPUT_DIR = Path("./output")
OUTPUT_DIR.mkdir(exist_ok=True)


# Dependency to get current user from token
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Extract and verify JWT token from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.split(" ")[1]
    user_info = auth_manager.verify_token(token)
    return user_info


async def require_auth(authorization: Optional[str] = Header(None)):
    """Require authentication for endpoint."""
    user = await get_current_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


async def require_admin(authorization: Optional[str] = Header(None)):
    """Require admin role for endpoint."""
    user = await get_current_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    if user["role"] not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


class CloneRequest(BaseModel):
    url: str
    mode: str = "static"
    depth: int = 2
    use_tor: bool = False
    discover_invisible: bool = False
    ai_enabled: bool = False
    output_name: Optional[str] = None


class AIConfigRequest(BaseModel):
    enabled: bool
    provider: str
    api_key: Optional[str] = ""
    model: Optional[str] = ""
    base_url: Optional[str] = "http://localhost:11434"


class UserRegisterRequest(BaseModel):
    username: str
    password: str
    email: str


class UserLoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


async def run_clone_job(job_id: str, request: CloneRequest, user_id: Optional[str] = None):
    """Background task to run cloning job."""
    try:
        jobs[job_id]["status"] = "running"
        jobs[job_id]["started_at"] = datetime.now().isoformat()
        if user_id:
            jobs[job_id]["user_id"] = user_id
        
        output_name = request.output_name or f"clone_{job_id[:8]}"
        output_path = OUTPUT_DIR / output_name
        
        # Initialize AI engine if enabled
        ai_engine = None
        if request.ai_enabled and ai_config.get("enabled"):
            ai_engine = AIEngine(ai_config)
            jobs[job_id]["ai_status"] = "AI enabled"
        
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
        
        # Run AI analysis if enabled
        if ai_engine:
            try:
                index_html = output_path / "index.html"
                if index_html.exists():
                    html_content = index_html.read_text(encoding='utf-8')
                    await ai_engine.analyze_and_enhance(html_content, request.url, output_path)
                    jobs[job_id]["ai_completed"] = True
            except Exception as ai_error:
                jobs[job_id]["ai_error"] = str(ai_error)
        
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
async def create_clone_job(
    request: CloneRequest, 
    background_tasks: BackgroundTasks,
    user: Optional[dict] = Depends(get_current_user)
):
    """Create a new cloning job."""
    job_id = str(uuid.uuid4())
    
    user_id = user["user_id"] if user else None
    
    jobs[job_id] = {
        "id": job_id,
        "request": request.dict(),
        "status": "queued",
        "created_at": datetime.now().isoformat(),
        "user_id": user_id,
        "username": user["username"] if user else "anonymous"
    }
    
    background_tasks.add_task(run_clone_job, job_id, request, user_id)
    
    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Job created successfully"
    }


# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/api/v1/auth/register")
async def register_user(data: UserRegisterRequest):
    """Register a new user."""
    # Check if username already exists
    existing_user = auth_manager.create_user(
        username=data.username,
        password=data.password,
        email=data.email,
        role=UserRole.USER.value
    )
    
    if not existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    return {
        "message": "User registered successfully",
        "user": {
            "id": existing_user.id,
            "username": existing_user.username,
            "email": existing_user.email,
            "role": existing_user.role
        }
    }


@app.post("/api/v1/auth/login")
async def login_user(data: UserLoginRequest):
    """Login and get JWT token."""
    result = auth_manager.authenticate(data.username, data.password)
    
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "message": "Login successful",
        "token": result["token"],
        "user": result["user"]
    }


@app.get("/api/v1/auth/me")
async def get_current_user_info(user: dict = Depends(require_auth)):
    """Get current user information."""
    return {"user": user}


@app.post("/api/v1/auth/change-password")
async def change_password(
    data: ChangePasswordRequest,
    user: dict = Depends(require_auth)
):
    """Change user password."""
    success = auth_manager.change_password(
        user["user_id"],
        data.old_password,
        data.new_password
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to change password")
    
    return {"message": "Password changed successfully"}


@app.post("/api/v1/auth/logout")
async def logout_user():
    """Logout (client should discard token)."""
    return {"message": "Logged out successfully"}


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
            str(zip_path),
            media_type="application/zip",
            filename=f"{output_path.name}.zip"
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
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type based on extension
    media_types = {
        '.html': 'text/html',
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.json': 'application/json',
        '.txt': 'text/plain',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.svg': 'image/svg+xml',
        '.pdf': 'application/pdf',
    }
    
    ext = file_path.suffix.lower()
    media_type = media_types.get(ext, 'application/octet-stream')
    
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
                "ai_completed": job.get("ai_completed", False)
            }
            for job_id, job in jobs.items()
        ]
    }


@app.get("/api/v1/ai/providers")
async def get_ai_providers():
    """Get available AI providers."""
    return {
        "providers": get_available_providers(),
        "current_config": ai_config
    }


@app.post("/api/v1/ai/config")
async def set_ai_config(config: AIConfigRequest):
    """Configure AI settings."""
    global ai_config
    
    # Validate API key if required
    if config.enabled and config.provider != "ollama":
        if not config.api_key or len(config.api_key) < 10:
            raise HTTPException(status_code=400, detail="Valid API key required for this provider")
    
    ai_config = {
        "enabled": config.enabled,
        "provider": config.provider,
        "api_key": config.api_key or "",
        "model": config.model or "",
        "base_url": config.base_url or "http://localhost:11434"
    }
    
    return {
        "message": "AI configuration updated successfully",
        "config": ai_config
    }


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
            "sample_response": response[:200] if response else "No response generated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI test failed: {str(e)}")


# ==================== ADMIN PANEL ENDPOINTS ====================

@app.get("/api/v1/admin/users")
async def list_all_users(admin: dict = Depends(require_admin)):
    """List all users (admin only)."""
    return {"users": auth_manager.list_users()}


@app.get("/api/v1/admin/users/{user_id}")
async def get_user_details(user_id: str, admin: dict = Depends(require_admin)):
    """Get user details (admin only)."""
    user = auth_manager.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at,
            "last_login": user.last_login,
            "is_active": user.is_active
        }
    }


@app.post("/api/v1/admin/users/{user_id}/toggle-active")
async def toggle_user_active(user_id: str, admin: dict = Depends(require_admin)):
    """Toggle user active status (admin only)."""
    user = auth_manager.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    auth_manager.update_user(user_id, is_active=not user.is_active)
    return {"message": f"User {'activated' if not user.is_active else 'deactivated'}"}


@app.delete("/api/v1/admin/users/{user_id}")
async def delete_user(user_id: str, admin: dict = Depends(require_admin)):
    """Delete user (admin only)."""
    if user_id == admin["user_id"]:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    success = auth_manager.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}


@app.get("/api/v1/admin/jobs")
async def list_all_jobs(admin: dict = Depends(require_admin)):
    """List all jobs across all users (admin only)."""
    return {
        "jobs": [
            {
                "job_id": job_id,
                "status": job["status"],
                "url": job["request"]["url"],
                "created_at": job["created_at"],
                "username": job.get("username", "anonymous"),
                "user_id": job.get("user_id"),
                "ai_enabled": job.get("ai_status", "") != "",
                "ai_completed": job.get("ai_completed", False)
            }
            for job_id, job in jobs.items()
        ]
    }


@app.get("/api/v1/admin/stats")
async def get_system_stats(admin: dict = Depends(require_admin)):
    """Get system statistics (admin only)."""
    total_users = len(auth_manager.users)
    total_jobs = len(jobs)
    completed_jobs = sum(1 for j in jobs.values() if j["status"] == "completed")
    failed_jobs = sum(1 for j in jobs.values() if j["status"] == "failed")
    running_jobs = sum(1 for j in jobs.values() if j["status"] == "running")
    
    return {
        "total_users": total_users,
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "running_jobs": running_jobs,
        "ai_enabled": ai_config.get("enabled", False),
        "ai_provider": ai_config.get("provider", "none")
    }


@app.post("/api/v1/admin/create-user")
async def admin_create_user(
    data: UserRegisterRequest,
    role: str = UserRole.USER.value,
    admin: dict = Depends(require_admin)
):
    """Create a new user (admin only)."""
    existing_user = auth_manager.create_user(
        username=data.username,
        password=data.password,
        email=data.email,
        role=role
    )
    
    if not existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    return {
        "message": "User created successfully",
        "user": {
            "id": existing_user.id,
            "username": existing_user.username,
            "email": existing_user.email,
            "role": existing_user.role
        }
    }


def start_api(host: str = "0.0.0.0", port: int = 8000, gui_dir: Optional[str] = None):
    """Start the API server with optional GUI serving."""
    import uvicorn
    
    # Mount GUI if directory provided
    if gui_dir and os.path.exists(gui_dir):
        app.mount("/", StaticFiles(directory=gui_dir, html=True), name="gui")
    
    print(f"Starting web-all API v4.0 on http://{host}:{port}")
    print(f"   API Docs: http://{host}:{port}/docs")
    if gui_dir:
        print(f"   Serving GUI from {gui_dir}")
    print(f"\nDefault admin credentials:")
    print(f"   Username: admin")
    print(f"   Password: admin123")
    print(f"   ⚠️  Change password immediately after first login!")
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_api()
