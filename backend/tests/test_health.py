"""Test health check endpoints."""

import pytest
from datetime import datetime


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data
    assert "health" in data


def test_health_check(client):
    """Test basic health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "message" in data
    assert "timestamp" in data
    assert "version" in data
    assert "environment" in data


def test_detailed_health_check(client):
    """Test detailed health check endpoint."""
    response = client.get("/api/v1/health/detailed")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "application" in data
    assert "system" in data
    assert "endpoints" in data
    
    # Check application info
    app_info = data["application"]
    assert app_info["name"] == "ContractCopilot"
    assert "version" in app_info
    assert "environment" in app_info
    
    # Check endpoints info
    endpoints = data["endpoints"]
    assert endpoints["health"] == "/health"
    assert endpoints["docs"] == "/docs"
