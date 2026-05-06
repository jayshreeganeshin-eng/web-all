"""
User Management System
Handles user authentication, roles, and permissions
"""

import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from pathlib import Path
import json


class UserManager:
    """Manage users, authentication, and permissions."""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.users_file = self.data_dir / "users.json"
        self.sessions_file = self.data_dir / "sessions.json"
        
        # Load or initialize users
        self.users = self._load_users()
        self.sessions = self._load_sessions()
        
        # Create default admin if no users exist
        if not self.users:
            self.create_user("admin", "admin123", role="admin")
    
    def _load_users(self) -> Dict[str, Any]:
        """Load users from file."""
        if self.users_file.exists():
            with open(self.users_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_sessions(self) -> Dict[str, Any]:
        """Load sessions from file."""
        if self.sessions_file.exists():
            with open(self.sessions_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_users(self):
        """Save users to file."""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def _save_sessions(self):
        """Save sessions to file."""
        with open(self.sessions_file, 'w') as f:
            json.dump(self.sessions, f, indent=2)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(
        self,
        username: str,
        password: str,
        email: str = "",
        role: str = "user"
    ) -> Dict[str, Any]:
        """Create a new user."""
        if username in self.users:
            raise ValueError(f"User {username} already exists")
        
        user_id = str(uuid.uuid4())
        self.users[username] = {
            "id": user_id,
            "username": username,
            "password_hash": self._hash_password(password),
            "email": email,
            "role": role,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "is_active": True,
            "permissions": self._get_role_permissions(role)
        }
        
        self._save_users()
        
        return {
            "id": user_id,
            "username": username,
            "role": role,
            "message": "User created successfully"
        }
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return session token."""
        if username not in self.users:
            return None
        
        user = self.users[username]
        if user["password_hash"] != self._hash_password(password):
            return None
        
        if not user["is_active"]:
            return None
        
        # Create session
        session_token = str(uuid.uuid4())
        self.sessions[session_token] = {
            "user_id": user["id"],
            "username": username,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        # Update last login
        user["last_login"] = datetime.now().isoformat()
        self._save_users()
        self._save_sessions()
        
        return session_token
    
    def get_user_by_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get user info from session token."""
        if session_token not in self.sessions:
            return None
        
        session = self.sessions[session_token]
        
        # Check expiration
        expires_at = datetime.fromisoformat(session["expires_at"])
        if datetime.now() > expires_at:
            del self.sessions[session_token]
            self._save_sessions()
            return None
        
        # Find user
        for username, user in self.users.items():
            if user["id"] == session["user_id"]:
                return {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "role": user["role"],
                    "permissions": user["permissions"]
                }
        
        return None
    
    def logout(self, session_token: str):
        """Invalidate session."""
        if session_token in self.sessions:
            del self.sessions[session_token]
            self._save_sessions()
    
    def _get_role_permissions(self, role: str) -> List[str]:
        """Get permissions for a role."""
        permissions = {
            "admin": ["read", "write", "delete", "manage_users", "manage_settings"],
            "user": ["read", "write"],
            "viewer": ["read"]
        }
        return permissions.get(role, [])
    
    def list_users(self) -> List[Dict[str, Any]]:
        """List all users (without password hashes)."""
        return [
            {
                "id": user["id"],
                "username": username,
                "email": user["email"],
                "role": user["role"],
                "created_at": user["created_at"],
                "last_login": user["last_login"],
                "is_active": user["is_active"]
            }
            for username, user in self.users.items()
        ]
    
    def update_user(self, username: str, **kwargs) -> Dict[str, Any]:
        """Update user information."""
        if username not in self.users:
            raise ValueError(f"User {username} not found")
        
        user = self.users[username]
        
        # Allowed fields to update
        allowed_fields = ["email", "role", "is_active"]
        for field, value in kwargs.items():
            if field in allowed_fields:
                user[field] = value
                if field == "role":
                    user["permissions"] = self._get_role_permissions(value)
        
        self._save_users()
        return {"message": "User updated successfully"}
    
    def delete_user(self, username: str):
        """Delete a user."""
        if username not in self.users:
            raise ValueError(f"User {username} not found")
        
        if username == "admin":
            raise ValueError("Cannot delete admin user")
        
        del self.users[username]
        self._save_users()
        
        # Invalidate all sessions for this user
        user_sessions = [
            token for token, session in self.sessions.items()
            if session["username"] == username
        ]
        for token in user_sessions:
            del self.sessions[token]
        self._save_sessions()


# Global user manager instance
user_manager = UserManager()
