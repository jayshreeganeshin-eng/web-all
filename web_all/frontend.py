"""Frontend routes for the WebAll MPA Dashboard"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()

# Setup templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)


@router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("pages/dashboard.html", {
        "request": request,
        "active_page": "dashboard"
    })


@router.get("/projects", response_class=HTMLResponse)
async def projects_page(request: Request):
    """Projects management page"""
    return templates.TemplateResponse("pages/projects.html", {
        "request": request,
        "active_page": "projects"
    })


@router.get("/tasks", response_class=HTMLResponse)
async def tasks_page(request: Request):
    """Tasks management page"""
    return templates.TemplateResponse("pages/tasks.html", {
        "request": request,
        "active_page": "tasks"
    }, status_code=404)  # Return 404 until tasks page is created


@router.get("/seo", response_class=HTMLResponse)
async def seo_page(request: Request):
    """Auto SEO page"""
    return templates.TemplateResponse("pages/seo.html", {
        "request": request,
        "active_page": "seo"
    })


@router.get("/content", response_class=HTMLResponse)
async def content_page(request: Request):
    """Content generator page"""
    return templates.TemplateResponse("pages/content.html", {
        "request": request,
        "active_page": "content"
    }, status_code=404)  # Return 404 until content page is created


@router.get("/clone", response_class=HTMLResponse)
async def clone_page(request: Request):
    """Site cloner page"""
    return templates.TemplateResponse("pages/clone.html", {
        "request": request,
        "active_page": "clone"
    }, status_code=404)  # Return 404 until clone page is created


@router.get("/users", response_class=HTMLResponse)
async def users_page(request: Request):
    """Users management page"""
    return templates.TemplateResponse("pages/users.html", {
        "request": request,
        "active_page": "users"
    })


@router.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    """Admin panel page"""
    return templates.TemplateResponse("pages/admin.html", {
        "request": request,
        "active_page": "admin"
    })


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Settings page"""
    return templates.TemplateResponse("pages/settings.html", {
        "request": request,
        "active_page": "settings"
    }, status_code=404)  # Return 404 until settings page is created
