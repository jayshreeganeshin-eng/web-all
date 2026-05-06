"""
Admin Panel - Management interface for system administration
Provides user management, job monitoring, AI configuration, and system settings
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path


class AdminPanel:
    """Admin panel for system administration."""
    
    def __init__(self, backend_service=None, user_manager=None):
        self.backend_service = backend_service
        self.user_manager = user_manager
        self.settings_file = Path("./data/admin_settings.json")
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load admin settings from file."""
        if self.settings_file.exists():
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        return {
            "max_concurrent_jobs": 5,
            "max_storage_gb": 100,
            "auto_cleanup_days": 30,
            "ai_default_provider": "ollama",
            "allow_registration": True,
            "require_email_verification": False
        }
    
    def _save_settings(self):
        """Save admin settings to file."""
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    # Dashboard Statistics
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics."""
        stats = {
            "total_users": 0,
            "active_users": 0,
            "total_jobs": 0,
            "completed_jobs": 0,
            "failed_jobs": 0,
            "running_jobs": 0,
            "storage_used_mb": 0,
            "ai_usage_count": 0
        }
        
        if self.user_manager:
            users = self.user_manager.list_users()
            stats["total_users"] = len(users)
            stats["active_users"] = sum(1 for u in users if u.get("is_active", True))
        
        if self.backend_service:
            jobs = self.backend_service.list_jobs()
            stats["total_jobs"] = len(jobs)
            stats["completed_jobs"] = sum(1 for j in jobs if j["status"] == "completed")
            stats["failed_jobs"] = sum(1 for j in jobs if j["status"] == "failed")
            stats["running_jobs"] = sum(1 for j in jobs if j["status"] == "running")
            stats["ai_usage_count"] = sum(1 for j in jobs if j.get("ai_enabled", False))
        
        # Calculate storage used
        output_dir = Path("./output")
        if output_dir.exists():
            total_size = sum(f.stat().st_size for f in output_dir.rglob('*') if f.is_file())
            stats["storage_used_mb"] = round(total_size / (1024 * 1024), 2)
        
        return stats
    
    # User Management
    def list_all_users(self) -> List[Dict[str, Any]]:
        """List all users with details."""
        if not self.user_manager:
            return []
        return self.user_manager.list_users()
    
    def create_user(self, username: str, password: str, email: str = "", role: str = "user"):
        """Create a new user."""
        if not self.user_manager:
            raise ValueError("User manager not initialized")
        return self.user_manager.create_user(username, password, email, role)
    
    def update_user(self, username: str, **kwargs):
        """Update user information."""
        if not self.user_manager:
            raise ValueError("User manager not initialized")
        return self.user_manager.update_user(username, **kwargs)
    
    def delete_user(self, username: str):
        """Delete a user."""
        if not self.user_manager:
            raise ValueError("User manager not initialized")
        self.user_manager.delete_user(username)
    
    # Job Management
    def list_all_jobs(self) -> List[Dict[str, Any]]:
        """List all cloning jobs."""
        if not self.backend_service:
            return []
        return self.backend_service.list_jobs()
    
    def get_job_details(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed job information."""
        if not self.backend_service:
            return None
        return self.backend_service.get_job_status(job_id)
    
    # AI Configuration
    def configure_ai(self, provider: str, api_key: str = "", model: str = "", base_url: str = ""):
        """Configure AI settings globally."""
        if not self.backend_service:
            raise ValueError("Backend service not initialized")
        self.backend_service.configure_ai(provider, api_key, model, base_url)
        self.settings["ai_default_provider"] = provider
        self._save_settings()
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get current AI configuration."""
        if self.backend_service:
            return self.backend_service.ai_config
        return {"enabled": False}
    
    # System Settings
    def update_setting(self, key: str, value: Any):
        """Update a system setting."""
        allowed_keys = [
            "max_concurrent_jobs",
            "max_storage_gb",
            "auto_cleanup_days",
            "ai_default_provider",
            "allow_registration",
            "require_email_verification"
        ]
        if key not in allowed_keys:
            raise ValueError(f"Invalid setting key: {key}")
        self.settings[key] = value
        self._save_settings()
    
    def get_settings(self) -> Dict[str, Any]:
        """Get all system settings."""
        return self.settings.copy()
    
    # System Logs (simplified)
    def get_system_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent system logs."""
        # In production, this would read from actual log files
        return [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "System initialized"
            }
        ]
    
    # Cleanup Operations
    def cleanup_old_jobs(self, days: int = 30):
        """Clean up old completed jobs."""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        cleaned = 0
        
        if self.backend_service:
            for job_id, job in list(self.backend_service.jobs.items()):
                if job["status"] == "completed":
                    completed_at = datetime.fromisoformat(job.get("completed_at", ""))
                    if completed_at < cutoff:
                        # Delete output directory
                        output_path = job.get("output_path", "")
                        if output_path:
                            import shutil
                            try:
                                shutil.rmtree(output_path)
                            except:
                                pass
                        del self.backend_service.jobs[job_id]
                        cleaned += 1
        
        return {"cleaned_jobs": cleaned}


# Global admin panel instance
admin_panel = AdminPanel()
