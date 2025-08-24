"""
Unit tests for session endpoints.
"""

from fastapi.testclient import TestClient
from typing import Dict, Any
from uuid import uuid4


class TestSessions:
    """Test session endpoints."""

    def test_get_my_sessions_success(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test getting current user's sessions."""
        response = client.get("/api/v1/sessions/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "session_count" in data
        assert "active_only" in data
        assert isinstance(data["session_count"], int)
        assert data["session_count"] >= 0

    def test_get_my_sessions_inactive_included(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test getting sessions including inactive ones."""
        response = client.get("/api/v1/sessions/me?active_only=false", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["active_only"] is False
        assert "session_count" in data

    def test_get_my_sessions_unauthorized(self, client: TestClient):
        """Test getting sessions without authentication."""
        response = client.get("/api/v1/sessions/me")
        assert response.status_code == 401

    def test_revoke_session_not_found(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test revoking a non-existent session."""
        fake_session_id = str(uuid4())
        response = client.delete(f"/api/v1/sessions/{fake_session_id}", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Session not found"

    def test_revoke_session_unauthorized(self, client: TestClient):
        """Test revoking session without authentication."""
        fake_session_id = str(uuid4())
        response = client.delete(f"/api/v1/sessions/{fake_session_id}")
        assert response.status_code == 401

    def test_revoke_all_sessions_success(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test revoking all sessions for current user."""
        response = client.delete("/api/v1/sessions/all", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "revoked_count" in data
        assert isinstance(data["revoked_count"], int)
        assert data["revoked_count"] >= 0

    def test_revoke_all_sessions_include_current(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test revoking all sessions including current one."""
        response = client.delete("/api/v1/sessions/all?exclude_current=false", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "revoked_count" in data

    def test_revoke_all_sessions_unauthorized(self, client: TestClient):
        """Test revoking all sessions without authentication."""
        response = client.delete("/api/v1/sessions/all")
        assert response.status_code == 401

    def test_cleanup_expired_sessions_regular_user_forbidden(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test that regular users cannot cleanup expired sessions."""
        response = client.post("/api/v1/sessions/cleanup", headers=auth_headers)
        
        # Should be forbidden for regular users (requires superuser)
        assert response.status_code == 403

    def test_cleanup_expired_sessions_unauthorized(self, client: TestClient):
        """Test cleanup expired sessions without authentication."""
        response = client.post("/api/v1/sessions/cleanup")
        assert response.status_code == 401
