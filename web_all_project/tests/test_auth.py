"""Tests for authentication system."""

import pytest
from web_all.utils.auth import AuthManager, UserRole


class TestAuthManager:
    """Test authentication manager."""
    
    def test_create_user(self):
        """Test user creation."""
        auth = AuthManager(db_path="./test_users.db")
        user = auth.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com"
        )
        
        assert user is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == UserRole.USER.value
        
        # Cleanup
        import os
        if os.path.exists("./test_users.db"):
            os.remove("./test_users.db")
    
    def test_authenticate_success(self):
        """Test successful authentication."""
        auth = AuthManager(db_path="./test_users.db")
        
        # Create user first
        auth.create_user(
            username="authuser",
            password="securepass",
            email="auth@test.com"
        )
        
        # Authenticate
        result = auth.authenticate("authuser", "securepass")
        
        assert result is not None
        assert "token" in result
        assert "user" in result
        assert result["user"]["username"] == "authuser"
        
        # Cleanup
        import os
        if os.path.exists("./test_users.db"):
            os.remove("./test_users.db")
    
    def test_authenticate_failure(self):
        """Test failed authentication."""
        auth = AuthManager(db_path="./test_users.db")
        
        auth.create_user(
            username="failuser",
            password="correctpass",
            email="fail@test.com"
        )
        
        # Wrong password
        result = auth.authenticate("failuser", "wrongpass")
        assert result is None
        
        # Cleanup
        import os
        if os.path.exists("./test_users.db"):
            os.remove("./test_users.db")
    
    def test_verify_token(self):
        """Test token verification."""
        auth = AuthManager(db_path="./test_users.db")
        
        auth.create_user(
            username="tokenuser",
            password="tokenpass",
            email="token@test.com"
        )
        
        result = auth.authenticate("tokenuser", "tokenpass")
        token = result["token"]
        
        # Verify token
        user_info = auth.verify_token(token)
        
        assert user_info is not None
        assert user_info["username"] == "tokenuser"
        assert user_info["role"] == UserRole.USER.value
        
        # Cleanup
        import os
        if os.path.exists("./test_users.db"):
            os.remove("./test_users.db")
    
    def test_list_users(self):
        """Test listing users."""
        auth = AuthManager(db_path="./test_users.db")
        
        auth.create_user("user1", "pass1", "user1@test.com")
        auth.create_user("user2", "pass2", "user2@test.com")
        
        users = auth.list_users()
        
        assert len(users) >= 2
        usernames = [u["username"] for u in users]
        assert "user1" in usernames
        assert "user2" in usernames
        
        # No passwords in list
        for user in users:
            assert "password_hash" not in user
        
        # Cleanup
        import os
        if os.path.exists("./test_users.db"):
            os.remove("./test_users.db")
    
    def test_change_password(self):
        """Test password change."""
        auth = AuthManager(db_path="./test_users.db")
        
        user = auth.create_user("pwduser", "oldpass", "pwd@test.com")
        
        # Change password
        success = auth.change_password(user.id, "oldpass", "newpass")
        assert success is True
        
        # Old password should fail
        result = auth.authenticate("pwduser", "oldpass")
        assert result is None
        
        # New password should work
        result = auth.authenticate("pwduser", "newpass")
        assert result is not None
        
        # Cleanup
        import os
        if os.path.exists("./test_users.db"):
            os.remove("./test_users.db")
    
    def test_role_hierarchy(self):
        """Test role-based access control."""
        auth = AuthManager(db_path="./test_users.db")
        
        admin = auth.create_user("admin2", "adminpass", "admin@test.com", UserRole.ADMIN.value)
        user = auth.create_user("regular2", "userpass", "user@test.com", UserRole.USER.value)
        
        assert admin is not None
        assert user is not None
        
        # Admin should have admin access
        assert auth.has_role(admin.id, UserRole.ADMIN.value) is True
        assert auth.has_role(admin.id, UserRole.USER.value) is True
        
        # Regular user should not have admin access
        assert auth.has_role(user.id, UserRole.ADMIN.value) is False
        assert auth.has_role(user.id, UserRole.USER.value) is True
        
        # Cleanup
        import os
        if os.path.exists("./test_users.db"):
            os.remove("./test_users.db")
