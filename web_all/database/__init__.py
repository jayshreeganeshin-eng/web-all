"""
Database configuration and session management for web_all.
Supports SQLite for development and PostgreSQL for production.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./web_all.db"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Session:
    """Dependency for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    from web_all.models import User, SiteProject, SEOAnalysis, ContentGeneration, AuditLog
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")


def create_tables():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
