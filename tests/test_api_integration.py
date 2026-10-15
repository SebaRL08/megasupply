"""
Module: test_api_integration.py
Description: Integration test suites utilizing FastAPI's TestClient.
"""

from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_create_and_get_product():
    """Test successful product creation and retrieval."""
    response = client.post(
        "/api/products/",
        json={"name": "Industrial Valve", "stock": 50, "min_threshold": 10}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Industrial Valve"
    assert "id" in data
    
    product_id = data["id"]
    get_response = client.get(f"/api/products/{product_id}")
    assert get_response.status_code == 200
    assert get_response.json()["stock"] == 50

def test_get_product_not_found():
    """Test 404 error handling for missing items."""
    response = client.get("/api/products/9999")
    assert response.status_code == 404

def test_validation_error_on_creation():
    """Test validation error for negative stock numbers."""
    response = client.post(
        "/api/products/",
        json={"name": "Faulty Item", "stock": -5, "min_threshold": 5}
    )
    assert response.status_code == 422