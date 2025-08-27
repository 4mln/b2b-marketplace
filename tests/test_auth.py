import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_signup(client):
    user_data = {
        "email": "newuser@example.com",
        "password": "securepassword123",
        "full_name": "New User"
    }
    
    response = await client.post("/auth/signup", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data
    assert "hashed_password" not in data  # Password should not be returned


@pytest.mark.asyncio
async def test_signup_duplicate_email(client, test_user):
    # Try to create a user with the same email as test_user
    user_data = {
        "email": "test@example.com",  # Same as test_user fixture
        "password": "password456",
        "full_name": "Duplicate User"
    }
    
    response = await client.post("/auth/signup", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login(client, test_user):
    login_data = {
        "username": "test@example.com",
        "password": "password123"
    }
    
    response = await client.post("/auth/token", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    login_data = {
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    
    response = await client.post("/auth/token", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_current_user(client, auth_headers):
    response = await client.get("/auth/me", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client):
    # Test with invalid token
    invalid_headers = {"Authorization": "Bearer invalidtoken123"}
    response = await client.get("/auth/me", headers=invalid_headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_user_missing_token(client):
    # Test with no token
    response = await client.get("/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED