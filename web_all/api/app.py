"""
Main FastAPI application for web_all.
Includes all routes, middleware, and frontend serving.
"""
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
import os
from pathlib import Path

from web_all.database import init_db, get_db
from web_all.api.routes import (
    auth_router, projects_router, seo_router, 
    content_router, admin_router
)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="web_all",
        description="All-in-one website cloning, SEO analysis, and AI content generation platform",
        version="3.0.0"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routers
    app.include_router(auth_router)
    app.include_router(projects_router)
    app.include_router(seo_router)
    app.include_router(content_router)
    app.include_router(admin_router)
    
    # Setup static files and templates
    base_dir = Path(__file__).parent.parent
    static_dir = base_dir / "frontend" / "static"
    templates_dir = base_dir / "frontend" / "templates"
    
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    templates = Jinja2Templates(directory=str(templates_dir)) if templates_dir.exists() else None
    
    # Initialize database on startup
    @app.on_event("startup")
    async def startup_event():
        init_db()
        print("🚀 web_all API server started!")
        print("📊 Dashboard: http://localhost:8000/")
        print("🔧 API Docs: http://localhost:8000/docs")
    
    # Root endpoint - serve dashboard
    @app.get("/", response_class=HTMLResponse)
    async def root(request: Request):
        if templates:
            return templates.TemplateResponse("public/dashboard.html", {
                "request": request,
                "title": "web_all Dashboard"
            })
        return HTMLResponse("<h1>web_all - Website Analysis & AI Platform</h1><p>Visit /docs for API documentation</p>")
    
    # User dashboard
    @app.get("/dashboard")
    async def user_dashboard(request: Request):
        if templates:
            return templates.TemplateResponse("user/dashboard.html", {
                "request": request,
                "title": "User Dashboard"
            })
        return HTMLResponse("<h1>User Dashboard</h1>")
    
    # Admin panel
    @app.get("/admin")
    async def admin_panel(request: Request):
        if templates:
            return templates.TemplateResponse("admin/dashboard.html", {
                "request": request,
                "title": "Admin Panel"
            })
        return HTMLResponse("<h1>Admin Panel</h1>")
    
    # Health check
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": "3.0.0"}
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
