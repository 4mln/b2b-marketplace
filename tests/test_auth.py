import pytest
from fastapi import status
from httpx import AsyncClient
from app.main import app  # Make sure this is your FastAPI instance with auth router included

# ---------------------- TEST SIGNUP ----------------------
@pytest.mark.asyncio
async def test_signup():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        user_data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "full_name": "New User"
        }
        response = await client.post("/api/v1/auth/signup", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
        assert "hashed_password" not in data


# ---------------------- TEST SIGNUP DUPLICATE ----------------------
@pytest.mark.asyncio
async def test_signup_duplicate_email(test_user):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        user = await test_user  # ✅ Await the fixture
        user_data = {
            "email": user["email"],  # Use the fixture email
            "password": "password456",
            "full_name": "Duplicate User"
        }
        response = await client.post("/api/v1/auth/signup", json=user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()


# ---------------------- TEST LOGIN ----------------------
@pytest.mark.asyncio
async def test_login(test_user):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        user = await test_user
        login_data = {
            "username": user["email"],
            "password": "password123"
        }
        response = await client.post("/api/v1/auth/token", data=login_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


# ---------------------- TEST LOGIN INVALID ----------------------
@pytest.mark.asyncio
async def test_login_invalid_credentials():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = await client.post("/api/v1/auth/token", data=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect" in response.json()["detail"].lower()


# ---------------------- TEST GET CURRENT USER ----------------------
@pytest.mark.asyncio
async def test_get_current_user(auth_headers):
    headers = await auth_headers  # ✅ Await the fixture
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "id" in data


# ---------------------- TEST GET CURRENT USER INVALID TOKEN ----------------------
@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        invalid_headers = {"Authorization": "Bearer invalidtoken123"}
        response = await client.get("api/v1/auth/me", headers=invalid_headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------- TEST GET CURRENT USER MISSING TOKEN ----------------------
@pytest.mark.asyncio
async def test_get_current_user_missing_token():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("api/v1/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
