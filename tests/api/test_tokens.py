"""
Tests for token management endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.service import app
from src.api.database import Base, engine, get_db
from sqlalchemy.orm import Session

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    """Get authentication headers"""
    # Register and login a user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword",
            "confirm_password": "testpassword"
        }
    )
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    token = response.json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_token(client, auth_headers):
    """Test token creation"""
    response = client.post(
        "/api/v1/tokens/create",
        headers=auth_headers,
        json={
            "name": "Test Token",
            "symbol": "TEST",
            "description": "A test token",
            "initial_supply": "1000000000000000000000",
            "decimals": 18,
            "is_mintable": True,
            "is_burnable": True,
            "is_pausable": True
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    data = response.json()["data"]["token"]
    assert data["name"] == "Test Token"
    assert data["symbol"] == "TEST"

def test_list_tokens(client, auth_headers):
    """Test token listing"""
    # First create a token
    client.post(
        "/api/v1/tokens/create",
        headers=auth_headers,
        json={
            "name": "Test Token",
            "symbol": "TEST",
            "description": "A test token",
            "initial_supply": "1000000000000000000000",
            "decimals": 18
        }
    )

    response = client.get("/api/v1/tokens/list", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert isinstance(response.json()["data"]["tokens"], list)

def test_get_token(client, auth_headers):
    """Test getting token details"""
    # First create a token
    create_response = client.post(
        "/api/v1/tokens/create",
        headers=auth_headers,
        json={
            "name": "Test Token",
            "symbol": "TEST",
            "description": "A test token",
            "initial_supply": "1000000000000000000000",
            "decimals": 18
        }
    )
    token_id = create_response.json()["data"]["token"]["id"]

    response = client.get(f"/api/v1/tokens/{token_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["token"]["id"] == token_id

def test_transfer_tokens(client, auth_headers):
    """Test token transfer"""
    # First create a token
    create_response = client.post(
        "/api/v1/tokens/create",
        headers=auth_headers,
        json={
            "name": "Test Token",
            "symbol": "TEST",
            "description": "A test token",
            "initial_supply": "1000000000000000000000",
            "decimals": 18
        }
    )
    token_id = create_response.json()["data"]["token"]["id"]

    response = client.post(
        "/api/v1/tokens/transfer",
        headers=auth_headers,
        json={
            "token_id": token_id,
            "to_address": "0x1234567890123456789012345678901234567890",
            "amount": "1000000000000000000"
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_mint_tokens(client, auth_headers):
    """Test token minting"""
    # First create a token
    create_response = client.post(
        "/api/v1/tokens/create",
        headers=auth_headers,
        json={
            "name": "Test Token",
            "symbol": "TEST",
            "description": "A test token",
            "initial_supply": "1000000000000000000000",
            "decimals": 18,
            "is_mintable": True
        }
    )
    token_id = create_response.json()["data"]["token"]["id"]

    response = client.post(
        "/api/v1/tokens/mint",
        headers=auth_headers,
        json={
            "token_id": token_id,
            "amount": "1000000000000000000"
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_burn_tokens(client, auth_headers):
    """Test token burning"""
    # First create a token
    create_response = client.post(
        "/api/v1/tokens/create",
        headers=auth_headers,
        json={
            "name": "Test Token",
            "symbol": "TEST",
            "description": "A test token",
            "initial_supply": "1000000000000000000000",
            "decimals": 18,
            "is_burnable": True
        }
    )
    token_id = create_response.json()["data"]["token"]["id"]

    response = client.post(
        "/api/v1/tokens/burn",
        headers=auth_headers,
        json={
            "token_id": token_id,
            "amount": "1000000000000000000"
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] is True 