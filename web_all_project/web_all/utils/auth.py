"""
User Authentication and Authorization System for web-all v4.0
Supports JWT tokens, password hashing, role-based access control (RBAC)
"""

import os
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path
import json
from dataclasses import dataclass, asdict
from enum import Enum


class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


@dataclass
class User:
    id: str
    username: str
    email: str
    password_hash: str
    role: str
    created_at: str
    last_login: Optional[str] = None
    is_active: bool = True
    api_key: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        return cls(**data)


class AuthManager:
    """Manages user authentication, authorization, and session management."""
    
    def __init__(self, secret_key: Optional[str] = None, db_path: str = "./users.db"):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.db_path = Path(db_path)
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self._load_users()
        
        # Create default admin if no users exist
        if not self.users:
            self._create_default_admin()
    
    def _load_users(self):
        """Load users from database file."""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    self.users = {uid: User.from_dict(u) for uid, u in data.items()}
            except Exception as e:
                print(f"Warning: Could not load users database: {e}")
                self.users = {}
    
    def _save_users(self):
        """Save users to database file."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.db_path, 'w') as f:
            json.dump({uid: u.to_dict() for uid, u in self.users.items()}, f, indent=2)
    
    def _create_default_admin(self):
        """Create default admin user."""
        admin_user = self.create_user(
            username="admin",
            password="admin123",  # Should be changed on first login
            email="admin@web-all.local",
            role=UserRole.ADMIN.value
        )
        print(f"⚠️  Default admin created: username='admin', password='admin123'")
        print("⚠️  Please change the password immediately!")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt."""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${hash_obj.hex()}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        try:
            salt, hash_value = password_hash.split('$')
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return hash_obj.hex() == hash_value
        except:
            return False
    
    def create_user(
        self, 
        username: str, 
        password: str, 
        email: str, 
        role: str = UserRole.USER.value
    ) -> Optional[User]:
        """Create a new user."""
        # Check if username exists
        for user in self.users.values():
            if user.username == username:
                return None
        
        user_id = secrets.token_urlsafe(16)
        user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=self._hash_password(password),
            role=role,
            created_at=datetime.now().isoformat(),
            api_key=secrets.token_urlsafe(32)
        )
        
        self.users[user_id] = user
        self._save_users()
        return user
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return JWT token."""
        # Find user by username
        user = None
        for u in self.users.values():
            if u.username == username:
                user = u
                break
        
        if not user or not user.is_active:
            return None
        
        if not self._verify_password(password, user.password_hash):
            return None
        
        # Update last login
        user.last_login = datetime.now().isoformat()
        self._save_users()
        
        # Generate JWT token
        token = self._generate_token(user)
        
        return {
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "api_key": user.api_key
            }
        }
    
    def _generate_token(self, user: User) -> str:
        """Generate JWT token for user."""
        payload = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return user info."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            user = self.users.get(payload["user_id"])
            if user and user.is_active:
                return {
                    "user_id": user.id,
                    "username": user.username,
                    "role": user.role,
                    "email": user.email
                }
        except jwt.ExpiredSignatureError:
            pass
        except jwt.InvalidTokenError:
            pass
        return None
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """Update user information."""
        user = self.users.get(user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key) and key not in ['id', 'username', 'role']:
                setattr(user, key, value)
        
        self._save_users()
        return user
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user."""
        if user_id in self.users:
            del self.users[user_id]
            self._save_users()
            return True
        return False
    
    def list_users(self) -> List[Dict[str, Any]]:
        """List all users (without password hashes)."""
        return [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "role": u.role,
                "created_at": u.created_at,
                "last_login": u.last_login,
                "is_active": u.is_active
            }
            for u in self.users.values()
        ]
    
    def has_role(self, user_id: str, required_role: str) -> bool:
        """Check if user has required role."""
        user = self.users.get(user_id)
        if not user:
            return False
        
        role_hierarchy = {
            UserRole.USER.value: 0,
            UserRole.ADMIN.value: 1,
            UserRole.SUPER_ADMIN.value: 2
        }
        
        user_level = role_hierarchy.get(user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password."""
        user = self.users.get(user_id)
        if not user:
            return False
        
        if not self._verify_password(old_password, user.password_hash):
            return False
        
        user.password_hash = self._hash_password(new_password)
        self._save_users()
        return True
    
    def generate_api_key(self, user_id: str) -> Optional[str]:
        """Generate new API key for user."""
        user = self.users.get(user_id)
        if not user:
            return None
        
        user.api_key = secrets.token_urlsafe(32)
        self._save_users()
        return user.api_key
