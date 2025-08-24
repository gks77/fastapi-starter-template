"""
Unit tests for profile endpoints.
"""

from fastapi.testclient import TestClient
from typing import Dict, Any
from uuid import uuid4
import tempfile
import os


class TestProfiles:
    """Test profile endpoints."""

    def test_get_my_profile_not_exists(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test getting profile when it doesn't exist."""
        response = client.get("/api/v1/profiles/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["has_profile"] is False
        assert "user_id" in data

    def test_create_profile_success(self, client: TestClient, auth_headers: Dict[str, str], sample_profile_data: Dict[str, Any]):
        """Test creating a new profile."""
        response = client.post("/api/v1/profiles/", json=sample_profile_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["action"] == "created"
        assert "profile_id" in data
        assert data["message"] == "Profile created successfully"

    def test_update_profile_success(self, client: TestClient, auth_headers: Dict[str, str], sample_profile_data: Dict[str, Any]):
        """Test updating an existing profile."""
        # Create profile first
        response = client.post("/api/v1/profiles/", json=sample_profile_data, headers=auth_headers)
        assert response.status_code == 200
        
        # Update profile
        update_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "bio": "Updated bio"
        }
        response = client.post("/api/v1/profiles/", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["action"] == "updated"
        assert "profile_id" in data

    def test_get_my_profile_exists(self, client: TestClient, auth_headers: Dict[str, str], sample_profile_data: Dict[str, Any]):
        """Test getting profile when it exists."""
        # Create profile first
        response = client.post("/api/v1/profiles/", json=sample_profile_data, headers=auth_headers)
        assert response.status_code == 200
        
        # Get profile
        response = client.get("/api/v1/profiles/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["has_profile"] is True
        assert "profile_id" in data
        assert "profile_data" in data
        assert data["profile_data"]["first_name"] == sample_profile_data["first_name"]

    def test_create_profile_unauthorized(self, client: TestClient, sample_profile_data: Dict[str, Any]):
        """Test creating profile without authentication."""
        response = client.post("/api/v1/profiles/", json=sample_profile_data)
        assert response.status_code == 401

    def test_get_my_profile_unauthorized(self, client: TestClient):
        """Test getting profile without authentication."""
        response = client.get("/api/v1/profiles/me")
        assert response.status_code == 401

    def test_get_user_profile_not_found(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test getting profile for non-existent user."""
        fake_user_id = str(uuid4())
        response = client.get(f"/api/v1/profiles/user/{fake_user_id}", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Profile not found"

    def test_get_user_profile_exists(self, client: TestClient, auth_headers: Dict[str, str], sample_profile_data: Dict[str, Any]):
        """Test getting another user's profile."""
        # Create profile for current user
        response = client.post("/api/v1/profiles/", json=sample_profile_data, headers=auth_headers)
        assert response.status_code == 200
        
        # Get current user ID
        response = client.get("/api/v1/users/me", headers=auth_headers)
        user_id = response.json()["id"]
        
        # Get user profile (own profile)
        response = client.get(f"/api/v1/profiles/user/{user_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id
        assert data["is_own_profile"] is True

    def test_search_profiles_success(self, client: TestClient, auth_headers: Dict[str, str], sample_profile_data: Dict[str, Any]):
        """Test searching profiles."""
        # Create a public profile first
        public_profile_data = sample_profile_data.copy()
        public_profile_data["is_profile_public"] = "public"
        response = client.post("/api/v1/profiles/", json=public_profile_data, headers=auth_headers)
        assert response.status_code == 200
        
        # Search profiles
        response = client.get("/api/v1/profiles/search?q=John", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total" in data
        assert "query" in data
        assert data["query"] == "John"

    def test_search_profiles_short_query(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test searching profiles with too short query."""
        response = client.get("/api/v1/profiles/search?q=a", headers=auth_headers)
        
        assert response.status_code == 422  # Validation error for min_length=2

    def test_search_profiles_pagination(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test search profiles pagination."""
        response = client.get("/api/v1/profiles/search?q=test&skip=10&limit=5", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["skip"] == 10
        assert data["limit"] == 5

    def test_get_public_profiles(self, client: TestClient, auth_headers: Dict[str, str], sample_profile_data: Dict[str, Any]):
        """Test getting all public profiles."""
        # Create a public profile
        public_profile_data = sample_profile_data.copy()
        public_profile_data["is_profile_public"] = "public"
        response = client.post("/api/v1/profiles/", json=public_profile_data, headers=auth_headers)
        assert response.status_code == 200
        
        # Get public profiles
        response = client.get("/api/v1/profiles/public", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total" in data
        assert isinstance(data["results"], list)

    def test_get_public_profiles_pagination(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test public profiles pagination."""
        response = client.get("/api/v1/profiles/public?skip=5&limit=10", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["skip"] == 5
        assert data["limit"] == 10

    def test_delete_my_profile_not_exists(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test deleting profile when it doesn't exist."""
        response = client.delete("/api/v1/profiles/", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Profile not found"

    def test_delete_my_profile_success(self, client: TestClient, auth_headers: Dict[str, str], sample_profile_data: Dict[str, Any]):
        """Test deleting existing profile."""
        # Create profile first
        response = client.post("/api/v1/profiles/", json=sample_profile_data, headers=auth_headers)
        assert response.status_code == 200
        
        # Delete profile
        response = client.delete("/api/v1/profiles/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Profile deleted successfully"

    def test_delete_profile_unauthorized(self, client: TestClient):
        """Test deleting profile without authentication."""
        response = client.delete("/api/v1/profiles/")
        assert response.status_code == 401

    def test_upload_avatar_unauthorized(self, client: TestClient):
        """Test uploading avatar without authentication."""
        # Create a dummy image file
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
            tmp_file.write(b"dummy image content")
            tmp_file_path = tmp_file.name
        
        try:
            with open(tmp_file_path, "rb") as f:
                response = client.post("/api/v1/profiles/upload-avatar", files={"file": f})
                assert response.status_code == 401
        finally:
            os.unlink(tmp_file_path)

    def test_delete_avatar_unauthorized(self, client: TestClient):
        """Test deleting avatar without authentication."""
        response = client.delete("/api/v1/profiles/avatar")
        assert response.status_code == 401

    def test_delete_avatar_no_profile(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test deleting avatar when profile doesn't exist."""
        response = client.delete("/api/v1/profiles/avatar", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Profile not found"
