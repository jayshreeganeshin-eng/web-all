"""
Database models for web_all application.
Includes User, SiteProject, SEOAnalysis, ContentGeneration, and AuditLog.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from web_all.database import Base


class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    projects = relationship("SiteProject", back_populates="owner")
    seo_analyses = relationship("SEOAnalysis", back_populates="user")
    content_generations = relationship("ContentGeneration", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class SiteProject(Base):
    """Model for tracked website projects."""
    __tablename__ = "site_projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending, cloning, completed, failed
    clone_mode = Column(String(20), default="static")  # static, dynamic
    use_tor = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    owner = relationship("User", back_populates="projects")
    seo_analyses = relationship("SEOAnalysis", back_populates="project")
    content_generations = relationship("ContentGeneration", back_populates="project")


class SEOAnalysis(Base):
    """Model for SEO analysis results."""
    __tablename__ = "seo_analyses"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("site_projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    url = Column(String(500), nullable=False)
    
    # SEO Metrics
    title_tag = Column(String(255), nullable=True)
    title_length = Column(Integer, nullable=True)
    meta_description = Column(Text, nullable=True)
    meta_description_length = Column(Integer, nullable=True)
    h1_count = Column(Integer, default=0)
    h2_count = Column(Integer, default=0)
    h3_count = Column(Integer, default=0)
    image_count = Column(Integer, default=0)
    images_without_alt = Column(Integer, default=0)
    internal_links = Column(Integer, default=0)
    external_links = Column(Integer, default=0)
    word_count = Column(Integer, default=0)
    
    # AI Analysis
    ai_score = Column(Float, nullable=True)  # 0-100
    ai_recommendations = Column(JSON, nullable=True)
    ai_suggested_title = Column(String(255), nullable=True)
    ai_suggested_description = Column(Text, nullable=True)
    ai_keywords = Column(JSON, nullable=True)
    
    # Status
    status = Column(String(50), default="pending")  # pending, analyzing, completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("SiteProject", back_populates="seo_analyses")
    user = relationship("User", back_populates="seo_analyses")


class ContentGeneration(Base):
    """Model for AI-generated content."""
    __tablename__ = "content_generations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("site_projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Content details
    content_type = Column(String(50), nullable=False)  # blog_post, product_desc, meta_tags, etc.
    topic = Column(String(500), nullable=False)
    keywords = Column(JSON, nullable=True)
    target_audience = Column(String(255), nullable=True)
    tone = Column(String(50), default="professional")  # professional, casual, friendly, formal
    
    # Generated content
    generated_content = Column(Text, nullable=True)
    ai_model_used = Column(String(100), nullable=True)
    word_count = Column(Integer, default=0)
    
    # Status
    status = Column(String(50), default="pending")  # pending, generating, completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("SiteProject", back_populates="content_generations")
    user = relationship("User", back_populates="content_generations")


class AuditLog(Base):
    """Model for tracking user actions."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)  # login, clone_site, analyze_seo, generate_content, etc.
    resource_type = Column(String(50), nullable=True)  # project, seo_analysis, content, etc.
    resource_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
