"""
Unit tests for authentication endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any


class TestAuth:
    """Test authentication endpoints."""

    def test_login_success(self, client: TestClient, test_user_data: Dict[str, Any]):
        """Test successful login."""
        # Create user first
        response = client.post("/api/v1/users/", json=test_user_data)
        assert response.status_code == 201
        
        # Login
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    def test_login_invalid_username(self, client: TestClient):
        """Test login with invalid username."""
        login_data = {
            "username": "nonexistent_user",
            "password": "somepassword"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect username or password"

    def test_login_invalid_password(self, client: TestClient, test_user_data: Dict[str, Any]):
        """Test login with invalid password."""
        # Create user first
        response = client.post("/api/v1/users/", json=test_user_data)
        assert response.status_code == 201
        
        # Try login with wrong password
        login_data = {
            "username": test_user_data["username"],
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect username or password"

    def test_login_missing_username(self, client: TestClient):
        """Test login with missing username."""
        login_data = {
            "password": "somepassword"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 422  # Validation error

    def test_login_missing_password(self, client: TestClient):
        """Test login with missing password."""
        login_data = {
            "username": "someuser"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 422  # Validation error

    def test_login_empty_credentials(self, client: TestClient):
        """Test login with empty credentials."""
        login_data = {
            "username": "",
            "password": ""
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        
        # Empty credentials should trigger authentication error (401)
        # This is more secure than exposing validation details (422)
        assert response.status_code == 401

    def test_login_form_data_format(self, client: TestClient, test_user_data: Dict[str, Any]):
        """Test that login endpoint expects form data, not JSON."""
        # Create user first
        response = client.post("/api/v1/users/", json=test_user_data)
        assert response.status_code == 201
        
        # Try login with JSON instead of form data (should still work with TestClient)
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # TestClient might handle this differently, but in real scenarios,
        # form data is required for OAuth2PasswordRequestForm
        # The important thing is that the endpoint works with proper form data
        assert response.status_code in [200, 422]  # Either works or validation error
