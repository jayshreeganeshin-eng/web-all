"""
API Routes for web_all FastAPI application.
Includes authentication, projects, SEO analysis, and content generation endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
import hashlib

from web_all.database import get_db
from web_all.models import User, SiteProject, SEOAnalysis, ContentGeneration, AuditLog
from web_all.services import SEOService


# Router instances
auth_router = APIRouter(prefix="/api/auth", tags=["Authentication"])
projects_router = APIRouter(prefix="/api/projects", tags=["Projects"])
seo_router = APIRouter(prefix="/api/seo", tags=["SEO Analysis"])
content_router = APIRouter(prefix="/api/content", tags=["Content Generation"])
admin_router = APIRouter(prefix="/api/admin", tags=["Admin"])


# Pydantic models for request/response
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    name: str
    url: str
    description: Optional[str] = None
    clone_mode: str = "static"
    use_tor: bool = False


class ProjectResponse(BaseModel):
    id: int
    name: str
    url: str
    description: Optional[str]
    status: str
    clone_mode: str
    use_tor: bool
    created_at: datetime
    owner_id: Optional[int]
    
    class Config:
        from_attributes = True


class SEOAnalysisRequest(BaseModel):
    url: str
    project_id: Optional[int] = None


class SEOAnalysisResponse(BaseModel):
    id: int
    url: str
    status: str
    ai_score: Optional[float]
    metrics: dict
    ai_recommendations: list
    created_at: datetime
    
    class Config:
        from_attributes = True


class ContentGenerationRequest(BaseModel):
    topic: str
    content_type: str = "blog_post"
    keywords: Optional[List[str]] = None
    target_audience: Optional[str] = None
    tone: str = "professional"
    project_id: Optional[int] = None


class ContentGenerationResponse(BaseModel):
    id: int
    topic: str
    content_type: str
    generated_content: Optional[str]
    status: str
    word_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Helper functions
def hash_password(password: str) -> str:
    """Hash password using SHA-256 (use bcrypt in production)."""
    return hashlib.sha256(password.encode()).hexdigest()


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Get current user from session (simplified for demo)."""
    # In production, use JWT tokens or session cookies
    user_id = request.session.get("user_id") if hasattr(request, "session") else None
    if not user_id:
        # For demo, return first admin user or create one
        user = db.query(User).filter(User.is_admin == True).first()
        if not user:
            user = User(
                username="admin",
                email="admin@weball.local",
                hashed_password=hash_password("admin123"),
                is_admin=True,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def log_audit(db: Session, user: User, action: str, resource_type: str = None, 
              resource_id: int = None, details: dict = None):
    """Log user action to audit trail."""
    audit = AuditLog(
        user_id=user.id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details
    )
    db.add(audit)
    db.commit()


# Authentication routes
@auth_router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user exists
    existing = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    log_audit(db, user, "register")
    return user


@auth_router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


# Projects routes
@projects_router.post("/", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db), 
                   current_user: User = Depends(get_current_user)):
    """Create a new site project."""
    proj = SiteProject(
        name=project.name,
        url=project.url,
        description=project.description,
        clone_mode=project.clone_mode,
        use_tor=project.use_tor,
        owner_id=current_user.id
    )
    db.add(proj)
    db.commit()
    db.refresh(proj)
    
    log_audit(db, current_user, "create_project", "project", proj.id)
    return proj


@projects_router.get("/", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db), 
                  current_user: User = Depends(get_current_user)):
    """List all projects for current user."""
    if current_user.is_admin:
        projects = db.query(SiteProject).all()
    else:
        projects = db.query(SiteProject).filter(SiteProject.owner_id == current_user.id).all()
    return projects


@projects_router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get project by ID."""
    project = db.query(SiteProject).filter(SiteProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# SEO Analysis routes
@seo_router.post("/analyze", response_model=SEOAnalysisResponse)
async def analyze_seo(request: SEOAnalysisRequest, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    """Perform SEO analysis on a URL."""
    seo_service = SEOService()
    
    # Create analysis record
    analysis = SEOAnalysis(
        project_id=request.project_id,
        user_id=current_user.id,
        url=request.url,
        status="analyzing"
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    try:
        # Perform analysis
        result = await seo_service.analyze_url(request.url)
        
        # Update analysis record
        if result["status"] == "completed":
            metrics = result.get("metrics", {})
            ai_analysis = result.get("ai_analysis", {})
            
            analysis.title_tag = metrics.get("title_tag")
            analysis.title_length = metrics.get("title_length")
            analysis.meta_description = metrics.get("meta_description")
            analysis.meta_description_length = metrics.get("meta_description_length")
            analysis.h1_count = metrics.get("h1_count", 0)
            analysis.h2_count = metrics.get("h2_count", 0)
            analysis.h3_count = metrics.get("h3_count", 0)
            analysis.image_count = metrics.get("image_count", 0)
            analysis.images_without_alt = metrics.get("images_without_alt", 0)
            analysis.word_count = metrics.get("word_count", 0)
            
            analysis.ai_score = ai_analysis.get("score")
            analysis.ai_recommendations = ai_analysis.get("recommendations", [])
            analysis.ai_suggested_title = ai_analysis.get("suggested_title")
            analysis.ai_suggested_description = ai_analysis.get("suggested_description")
            analysis.ai_keywords = ai_analysis.get("keywords", [])
            analysis.status = "completed"
        else:
            analysis.status = "failed"
            analysis.error_message = result.get("error", "Unknown error")
            
        db.commit()
        db.refresh(analysis)
        
        log_audit(db, current_user, "analyze_seo", "seo_analysis", analysis.id)
        
    except Exception as e:
        analysis.status = "failed"
        analysis.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
    return analysis


@seo_router.get("/{analysis_id}", response_model=SEOAnalysisResponse)
def get_seo_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """Get SEO analysis by ID."""
    analysis = db.query(SEOAnalysis).filter(SEOAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


# Content Generation routes
@content_router.post("/generate", response_model=ContentGenerationResponse)
async def generate_content(request: ContentGenerationRequest, 
                           db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    """Generate SEO-optimized content using AI."""
    seo_service = SEOService()
    
    # Create content generation record
    content_gen = ContentGeneration(
        project_id=request.project_id,
        user_id=current_user.id,
        content_type=request.content_type,
        topic=request.topic,
        keywords=request.keywords or [],
        target_audience=request.target_audience,
        tone=request.tone,
        status="generating"
    )
    db.add(content_gen)
    db.commit()
    db.refresh(content_gen)
    
    try:
        # Generate content
        content = await seo_service.generate_seo_content(
            topic=request.topic,
            keywords=request.keywords or [],
            content_type=request.content_type,
            tone=request.tone
        )
        
        # Update record
        content_gen.generated_content = content
        content_gen.word_count = len(content.split())
        content_gen.status = "completed"
        
        db.commit()
        db.refresh(content_gen)
        
        log_audit(db, current_user, "generate_content", "content", content_gen.id)
        
    except Exception as e:
        content_gen.status = "failed"
        content_gen.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")
    
    return content_gen


@content_router.get("/{content_id}", response_model=ContentGenerationResponse)
def get_content(content_id: int, db: Session = Depends(get_db)):
    """Get generated content by ID."""
    content = db.query(ContentGeneration).filter(ContentGeneration.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content


# Admin routes
@admin_router.get("/users", response_model=List[UserResponse])
def list_all_users(db: Session = Depends(get_db), 
                   current_user: User = Depends(get_current_user)):
    """List all users (admin only)."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    users = db.query(User).all()
    return users


@admin_router.get("/audit-logs")
def get_audit_logs(db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    """Get audit logs (admin only)."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()
    return logs
