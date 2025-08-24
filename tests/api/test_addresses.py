"""
Unit tests for address endpoints.
"""

from fastapi.testclient import TestClient
from typing import Dict, Any
from uuid import uuid4


class TestAddresses:
    """Test address endpoints."""

    def test_get_user_addresses_empty(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test getting addresses when user has none."""
        response = client.get("/api/v1/addresses/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_create_address_success(self, client: TestClient, auth_headers: Dict[str, str], sample_address_data: Dict[str, Any]):
        """Test creating a new address."""
        response = client.post("/api/v1/addresses/", json=sample_address_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["address_line_1"] == sample_address_data["address_line_1"]
        assert data["city"] == sample_address_data["city"]
        assert data["is_default"] is True  # First address should be default
        assert "id" in data

    def test_create_address_unauthorized(self, client: TestClient, sample_address_data: Dict[str, Any]):
        """Test creating address without authentication."""
        response = client.post("/api/v1/addresses/", json=sample_address_data)
        assert response.status_code == 401

    def test_create_address_invalid_data(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test creating address with invalid data."""
        invalid_data = {
            "address_line_1": "",  # Empty required field
            "city": "Test City"
        }
        response = client.post("/api/v1/addresses/", json=invalid_data, headers=auth_headers)
        assert response.status_code == 422

    def test_get_user_addresses_with_data(self, client: TestClient, auth_headers: Dict[str, str], sample_address_data: Dict[str, Any]):
        """Test getting addresses when user has addresses."""
        # Create an address first
        response = client.post("/api/v1/addresses/", json=sample_address_data, headers=auth_headers)
        assert response.status_code == 201
        
        # Get addresses
        response = client.get("/api/v1/addresses/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["address_line_1"] == sample_address_data["address_line_1"]

    def test_get_user_addresses_pagination(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test addresses pagination."""
        response = client.get("/api/v1/addresses/?skip=0&limit=10", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_user_addresses_filter_by_type(self, client: TestClient, auth_headers: Dict[str, str], sample_address_data: Dict[str, Any]):
        """Test filtering addresses by type."""
        # Create shipping address
        shipping_data = sample_address_data.copy()
        shipping_data["address_type"] = "shipping"
        response = client.post("/api/v1/addresses/", json=shipping_data, headers=auth_headers)
        assert response.status_code == 201
        
        # Filter by shipping type
        response = client.get("/api/v1/addresses/?address_type=shipping", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        for addr in data:
            assert addr["address_type"] == "shipping"

    def test_get_user_addresses_unauthorized(self, client: TestClient):
        """Test getting addresses without authentication."""
        response = client.get("/api/v1/addresses/")
        assert response.status_code == 401

    def test_get_default_address_none(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test getting default address when none exists."""
        response = client.get("/api/v1/addresses/default", headers=auth_headers)
        
        assert response.status_code == 200
        # Should return null/None when no default address
        assert response.json() is None

    def test_get_default_address_exists(self, client: TestClient, auth_headers: Dict[str, str], sample_address_data: Dict[str, Any]):
        """Test getting default address when it exists."""
        # Create an address (first one should be default)
        response = client.post("/api/v1/addresses/", json=sample_address_data, headers=auth_headers)
        assert response.status_code == 201
        
        # Get default address
        response = client.get("/api/v1/addresses/default", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data is not None
        assert data["is_default"] is True

    def test_get_address_by_id_success(self, client: TestClient, auth_headers: Dict[str, str], sample_address_data: Dict[str, Any]):
        """Test getting specific address by ID."""
        # Create an address
        response = client.post("/api/v1/addresses/", json=sample_address_data, headers=auth_headers)
        assert response.status_code == 201
        address_id = response.json()["id"]
        
        # Get address by ID
        response = client.get(f"/api/v1/addresses/{address_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == address_id
        assert data["address_line_1"] == sample_address_data["address_line_1"]

    def test_get_address_by_id_not_found(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test getting non-existent address by ID."""
        fake_id = str(uuid4())
        response = client.get(f"/api/v1/addresses/{fake_id}", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Address not found"

    def test_get_address_unauthorized(self, client: TestClient):
        """Test getting address without authentication."""
        fake_id = str(uuid4())
        response = client.get(f"/api/v1/addresses/{fake_id}")
        assert response.status_code == 401

    def test_update_address_success(self, client: TestClient, auth_headers: Dict[str, str], sample_address_data: Dict[str, Any]):
        """Test updating an existing address."""
        # Create an address
        response = client.post("/api/v1/addresses/", json=sample_address_data, headers=auth_headers)
        assert response.status_code == 201
        address_id = response.json()["id"]
        
        # Update address
        update_data = {
            "address_line_1": "456 Updated St",
            "city": "Updated City"
        }
        response = client.put(f"/api/v1/addresses/{address_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["address_line_1"] == update_data["address_line_1"]
        assert data["city"] == update_data["city"]

    def test_update_address_not_found(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test updating non-existent address."""
        fake_id = str(uuid4())
        update_data = {"address_line_1": "123 Test St"}
        response = client.put(f"/api/v1/addresses/{fake_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Address not found"

    def test_update_address_unauthorized(self, client: TestClient):
        """Test updating address without authentication."""
        fake_id = str(uuid4())
        update_data = {"address_line_1": "123 Test St"}
        response = client.put(f"/api/v1/addresses/{fake_id}", json=update_data)
        assert response.status_code == 401

    def test_set_default_address_success(self, client: TestClient, auth_headers: Dict[str, str], sample_address_data: Dict[str, Any]):
        """Test setting an address as default."""
        # Create an address
        response = client.post("/api/v1/addresses/", json=sample_address_data, headers=auth_headers)
        assert response.status_code == 201
        address_id = response.json()["id"]
        
        # Set as default
        response = client.post("/api/v1/addresses/set-default", json={"address_id": address_id}, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Address set as default successfully"
        assert data["address"]["is_default"] is True

    def test_set_default_address_not_found(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test setting non-existent address as default."""
        fake_id = str(uuid4())
        response = client.post("/api/v1/addresses/set-default", json={"address_id": fake_id}, headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Address not found or inactive"

    def test_set_default_address_unauthorized(self, client: TestClient):
        """Test setting default address without authentication."""
        fake_id = str(uuid4())
        response = client.post("/api/v1/addresses/set-default", json={"address_id": fake_id})
        assert response.status_code == 401

    def test_delete_address_soft_delete(self, client: TestClient, auth_headers: Dict[str, str], sample_address_data: Dict[str, Any]):
        """Test soft deleting an address."""
        # Create an address
        response = client.post("/api/v1/addresses/", json=sample_address_data, headers=auth_headers)
        assert response.status_code == 201
        address_id = response.json()["id"]
        
        # Soft delete address
        response = client.delete(f"/api/v1/addresses/{address_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "deactivated" in data["message"]

    def test_delete_address_hard_delete(self, client: TestClient, auth_headers: Dict[str, str], sample_address_data: Dict[str, Any]):
        """Test hard deleting an address."""
        # Create an address
        response = client.post("/api/v1/addresses/", json=sample_address_data, headers=auth_headers)
        assert response.status_code == 201
        address_id = response.json()["id"]
        
        # Hard delete address
        response = client.delete(f"/api/v1/addresses/{address_id}?hard_delete=true", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "permanently deleted" in data["message"]

    def test_delete_address_not_found(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test deleting non-existent address."""
        fake_id = str(uuid4())
        response = client.delete(f"/api/v1/addresses/{fake_id}", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Address not found"

    def test_delete_address_unauthorized(self, client: TestClient):
        """Test deleting address without authentication."""
        fake_id = str(uuid4())
        response = client.delete(f"/api/v1/addresses/{fake_id}")
        assert response.status_code == 401

    def test_get_addresses_by_type_success(self, client: TestClient, auth_headers: Dict[str, str], sample_address_data: Dict[str, Any]):
        """Test getting addresses by specific type."""
        # Create different types of addresses
        shipping_data = sample_address_data.copy()
        shipping_data["address_type"] = "shipping"
        response = client.post("/api/v1/addresses/", json=shipping_data, headers=auth_headers)
        assert response.status_code == 201
        
        billing_data = sample_address_data.copy()
        billing_data["address_type"] = "billing"
        billing_data["address_line_1"] = "789 Billing St"
        response = client.post("/api/v1/addresses/", json=billing_data, headers=auth_headers)
        assert response.status_code == 201
        
        # Get shipping addresses
        response = client.get("/api/v1/addresses/type/shipping", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        for addr in data:
            assert addr["address_type"] == "shipping"

    def test_get_addresses_by_invalid_type(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test getting addresses by invalid type."""
        response = client.get("/api/v1/addresses/type/invalid", headers=auth_headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "address_type must be one of" in data["detail"]

    def test_get_addresses_by_type_unauthorized(self, client: TestClient):
        """Test getting addresses by type without authentication."""
        response = client.get("/api/v1/addresses/type/shipping")
        assert response.status_code == 401

    def test_multiple_addresses_default_management(self, client: TestClient, auth_headers: Dict[str, str], sample_address_data: Dict[str, Any]):
        """Test that only one address can be default at a time."""
        # Create first address (should be default)
        response = client.post("/api/v1/addresses/", json=sample_address_data, headers=auth_headers)
        assert response.status_code == 201
        first_address_id = response.json()["id"]
        
        # Create second address
        second_address_data = sample_address_data.copy()
        second_address_data["address_line_1"] = "456 Second St"
        response = client.post("/api/v1/addresses/", json=second_address_data, headers=auth_headers)
        assert response.status_code == 201
        second_address_id = response.json()["id"]
        
        # Set second address as default
        response = client.post("/api/v1/addresses/set-default", json={"address_id": second_address_id}, headers=auth_headers)
        assert response.status_code == 200
        
        # Check that only second address is default
        response = client.get("/api/v1/addresses/default", headers=auth_headers)
        assert response.status_code == 200
        default_address = response.json()
        assert default_address["id"] == second_address_id
        
        # Verify first address is no longer default
        response = client.get(f"/api/v1/addresses/{first_address_id}", headers=auth_headers)
        assert response.status_code == 200
        first_address = response.json()
        assert first_address["is_default"] is False
