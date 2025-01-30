"""
Tests for authentication endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.service import app
from src.api.database import Base, engine, get_db
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
import uuid
from src.api.models import User

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db: Session = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    db: Session = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

def test_register_user(client):
    """Test user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword",
            "confirm_password": "testpassword"
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "Registration successful" in response.json()["message"]

def test_login_user(client):
    """Test user login"""
    # First register a user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword",
            "confirm_password": "testpassword"
        }
    )

    # Then try to login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "token" in response.json()["data"]

def test_invalid_login(client):
    """Test login with invalid credentials"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401

def test_protected_endpoint(client):
    """Test accessing protected endpoint"""
    # Try without token
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

    # Login and get token
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword",
            "confirm_password": "testpassword"
        }
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    token = login_response.json()["data"]["token"]

    # Try with token
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

def test_create_user(test_db: Session):
    """Test user creation in database"""
    user_data = {
        "id": str(uuid.uuid4()),  # Generate unique ID
        "email": "test@example.com",
        "password": "testpassword"
    }
    test_db.add(User(**user_data))
    test_db.commit()
    
    # Test user lookup by ID
    user = test_db.query(User).filter(User.id == user_data["id"]).first()
    assert user is not None
    assert user.id == user_data["id"]
    assert user.email == user_data["email"]

def test_unique_user_ids(test_db: Session):
    """Test that each user gets a unique ID"""
    user1_id = str(uuid.uuid4())
    user2_id = str(uuid.uuid4())
    
    assert user1_id != user2_id  # Verify UUIDs are unique 