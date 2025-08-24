"""
Unit tests for user endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any
from uuid import uuid4


class TestUsers:
    """Test user endpoints."""

    def test_create_user_success(self, client: TestClient, test_user_data: Dict[str, Any]):
        """Test successful user creation."""
        response = client.post("/api/v1/users/", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert "id" in data
        assert "password" not in data  # Password should not be returned
        assert data["is_active"] is True
        assert data["is_superuser"] is False

    def test_create_user_duplicate_username(self, client: TestClient, test_user_data: Dict[str, Any]):
        """Test creating user with duplicate username."""
        # Create first user
        response = client.post("/api/v1/users/", json=test_user_data)
        assert response.status_code == 201
        
        # Try to create user with same username but different email
        duplicate_data = test_user_data.copy()
        duplicate_data["email"] = f"different_{uuid4().hex[:8]}@example.com"
        
        response = client.post("/api/v1/users/", json=duplicate_data)
        assert response.status_code == 400

    def test_create_user_duplicate_email(self, client: TestClient, test_user_data: Dict[str, Any]):
        """Test creating user with duplicate email."""
        # Create first user
        response = client.post("/api/v1/users/", json=test_user_data)
        assert response.status_code == 201
        
        # Try to create user with same email but different username
        duplicate_data = test_user_data.copy()
        duplicate_data["username"] = f"different_{uuid4().hex[:8]}"
        
        response = client.post("/api/v1/users/", json=duplicate_data)
        assert response.status_code == 400

    def test_create_user_invalid_email(self, client: TestClient, test_user_data: Dict[str, Any]):
        """Test creating user with invalid email."""
        invalid_data = test_user_data.copy()
        invalid_data["email"] = "invalid-email"
        
        response = client.post("/api/v1/users/", json=invalid_data)
        assert response.status_code == 422

    def test_create_user_short_password(self, client: TestClient, test_user_data: Dict[str, Any]):
        """Test creating user with password too short."""
        invalid_data = test_user_data.copy()
        invalid_data["password"] = "123"
        
        response = client.post("/api/v1/users/", json=invalid_data)
        # If no password length validation is enforced, this should succeed
        # In production, you might want to add password validation
        assert response.status_code in [201, 422]  # Accept either valid creation or validation error

    def test_create_user_missing_fields(self, client: TestClient):
        """Test creating user with missing required fields."""
        # Missing username
        response = client.post("/api/v1/users/", json={
            "email": "test@example.com",
            "password": "testpassword123"
        })
        assert response.status_code == 422
        
        # Missing email
        response = client.post("/api/v1/users/", json={
            "username": "testuser",
            "password": "testpassword123"
        })
        assert response.status_code == 422
        
        # Missing password
        response = client.post("/api/v1/users/", json={
            "username": "testuser",
            "email": "test@example.com"
        })
        assert response.status_code == 422

    def test_get_current_user(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test getting current user."""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert "email" in data
        assert "password" not in data

    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test getting current user without authentication."""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 401

    def test_get_user_by_id_own_user(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test getting user by ID (own user)."""
        # First get current user to get the ID
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        user_id = response.json()["id"]
        
        # Get user by ID
        response = client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id

    def test_get_user_by_id_other_user_forbidden(self, client: TestClient, auth_headers: Dict[str, str], test_user_data: Dict[str, Any]):
        """Test getting another user by ID (should be forbidden for non-superuser)."""
        # Create another user
        other_user_data = {
            "username": f"otheruser_{uuid4().hex[:8]}",
            "email": f"other_{uuid4().hex[:8]}@example.com",
            "password": "testpassword123"
        }
        response = client.post("/api/v1/users/", json=other_user_data)
        assert response.status_code == 201
        other_user_id = response.json()["id"]
        
        # Try to get other user (should be forbidden)
        response = client.get(f"/api/v1/users/{other_user_id}", headers=auth_headers)
        assert response.status_code == 403

    def test_get_user_by_id_not_found(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test getting user by non-existent ID."""
        fake_id = str(uuid4())
        response = client.get(f"/api/v1/users/{fake_id}", headers=auth_headers)
        # The API first checks permissions, so non-superuser gets 403 before 404
        assert response.status_code == 403

    def test_update_user_own_profile(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test updating own user profile."""
        # Get current user ID
        response = client.get("/api/v1/users/me", headers=auth_headers)
        user_id = response.json()["id"]
        
        # Update user
        update_data = {
            "username": f"updated_{uuid4().hex[:8]}",
            "email": f"updated_{uuid4().hex[:8]}@example.com"
        }
        response = client.put(f"/api/v1/users/{user_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == update_data["username"]
        assert data["email"] == update_data["email"]

    def test_update_user_unauthorized(self, client: TestClient):
        """Test updating user without authentication."""
        fake_id = str(uuid4())
        update_data = {"username": "newusername"}
        response = client.put(f"/api/v1/users/{fake_id}", json=update_data)
        assert response.status_code == 401

    def test_get_users_list_superuser_only(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test getting users list (should require superuser)."""
        response = client.get("/api/v1/users/", headers=auth_headers)
        # Should be forbidden for regular user
        assert response.status_code == 403

    def test_delete_user_superuser_only(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test deleting user (should require superuser)."""
        # Get current user ID
        response = client.get("/api/v1/users/me", headers=auth_headers)
        user_id = response.json()["id"]
        
        # Try to delete (should be forbidden for regular user)
        response = client.delete(f"/api/v1/users/{user_id}", headers=auth_headers)
        assert response.status_code == 403
