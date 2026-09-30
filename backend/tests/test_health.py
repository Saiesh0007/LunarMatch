import pytest
from client_helper import test_client

def test_health_endpoint():
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "LunarMatch" in data["service"]
    assert data["cv_available"] is True

def test_capabilities_endpoint():
    response = test_client.get("/api/v1/capabilities")
    assert response.status_code == 200
    data = response.json()
    assert "capabilities" in data
    names = [c["name"] for c in data["capabilities"]]
    assert "SIFT Feature Extraction" in names
    assert "Spatial Grid Balancing" in names
    assert "RIFT2 Phase Feature" in names
    assert "Sub-Pixel Refinement" in names
