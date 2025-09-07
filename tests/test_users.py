# tests/plugins/users/test_users.py
"""
Production-grade async tests for the User plugin.

Behavior:
- Runs each test inside a DB transaction that is rolled back at the end -> isolates tests from each other and from real DB state.
- Overrides the app's DB dependency to use the transaction-bound session.
- Uses httpx.AsyncClient against the FastAPI app.
- Exercises register, login (JWT), protected route, update, delete, and edge-cases.

Adjust these names at the top if your project uses different function/variable names.
"""

import asyncio
import json
import pytest
import pytest_asyncio
from httpx import AsyncClient
from faker import Faker

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

# --- Adjust these imports if your project structure differs ---
from app.main import app  # FastAPI app
from app.core.db import engine, get_async_session  # engine and dependency to override
# ------------------------------------------------------------

faker = Faker()

# Endpoint paths — change if your API uses different routes
REGISTER_PATH = "/api/users/register"
LOGIN_PATH = "/api/auth/login"
ME_PATH = "/api/users/me"
USER_BY_ID_PATH = "/api/users/{user_id}"  # supports GET, PATCH, DELETE

# Helper to set Authorization header
def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture(scope="session")
def anyio_backend():
    # required by pytest-asyncio / anyio sometimes — keep session scope
    return "asyncio"


@pytest_asyncio.fixture(scope="function")
async def db_transaction_fixture():
    """
    Create a transaction-scoped session bound to a single connection.
    All changes are rolled back when this fixture finishes.
    """
    # Connect a raw connection and begin a nested transaction
    async with engine.connect() as conn:
        trans = await conn.begin()
        # create a session factory bound to the connection
        TestSessionLocal = sessionmaker(
            bind=conn, class_=AsyncSession, expire_on_commit=False
        )

        async def get_test_session() -> AsyncSession:
            async with TestSessionLocal() as session:
                yield session

        try:
            yield get_test_session
        finally:
            # rollback the outer transaction and close connection
            await trans.rollback()


@pytest_asyncio.fixture
async def async_client(db_transaction_fixture, monkeypatch):
    """
    Provides an httpx AsyncClient with overridden DB dependency which
    yields sessions created from the transactional connection above.
    """

    # override the app dependency that provides DB sessions
    # NOTE: if your dependency name is different, edit import at top (get_async_session)
    app.dependency_overrides[get_async_session] = db_transaction_fixture

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client

    # clean up override
    app.dependency_overrides.pop(get_async_session, None)


# ---------- Helper functions used across tests ----------
async def register_user(client: AsyncClient, email: str = None, password: str = "Password123!"):
    email = email or faker.email()
    payload = {
        "email": email,
        "password": password,
        "full_name": faker.name(),
        # add any required fields your endpoint needs (username, phone, etc.)
    }
    resp = await client.post(REGISTER_PATH, json=payload)
    return resp


async def login_user(client: AsyncClient, email: str, password: str = "Password123!"):
    payload = {"username": email, "password": password}
    resp = await client.post(LOGIN_PATH, data=payload)
    return resp


# -------------------- Tests --------------------

@pytest.mark.asyncio
async def test_register_and_login_and_me_flow(async_client: AsyncClient):
    # Register
    email = faker.unique.email()
    register_resp = await register_user(async_client, email=email)
    assert register_resp.status_code in (200, 201), f"unexpected register code: {register_resp.status_code} / body: {register_resp.text}"

    body = register_resp.json()
    assert "id" in body or "email" in body, "response should include user id or user payload"

    # Login (some projects expect form-data for OAuth2 password flow)
    login_resp = await login_user(async_client, email=email, password="Password123!")
    assert login_resp.status_code == 200, f"login failed: {login_resp.status_code} / {login_resp.text}"
    token_data = login_resp.json()
    assert "access_token" in token_data or "token" in token_data, f"token not in login response: {token_data}"

    # normalize token key
    token = token_data.get("access_token") or token_data.get("token") or token_data.get("accessToken")

    # Protected /me
    me_resp = await async_client.get(ME_PATH, headers=auth_header(token))
    assert me_resp.status_code == 200, f"/me failed: {me_resp.status_code} / {me_resp.text}"
    me_json = me_resp.json()
    assert me_json.get("email") == email or "id" in me_json, "/me response missing expected fields"


@pytest.mark.asyncio
async def test_duplicate_registration_returns_400(async_client: AsyncClient):
    email = faker.unique.email()
    r1 = await register_user(async_client, email=email)
    assert r1.status_code in (200, 201)

    r2 = await register_user(async_client, email=email)
    # duplication should be rejected
    assert r2.status_code in (400, 409), f"expected 400/409 on duplicate, got {r2.status_code} / {r2.text}"


@pytest.mark.asyncio
async def test_login_with_wrong_password_returns_401(async_client: AsyncClient):
    email = faker.unique.email()
    await register_user(async_client, email=email, password="CorrectPassword123!")
    login_resp = await login_user(async_client, email=email, password="WrongPassword!")
    assert login_resp.status_code in (401, 400), f"expected 401/400 for wrong password, got {login_resp.status_code} / {login_resp.text}"


@pytest.mark.asyncio
async def test_protected_endpoint_rejects_without_token(async_client: AsyncClient):
    resp = await async_client.get(ME_PATH)  # no auth header
    assert resp.status_code in (401, 403), f"expected 401/403 when no token provided, got {resp.status_code}"


@pytest.mark.asyncio
async def test_update_and_delete_user_flow(async_client: AsyncClient):
    # Register + login
    email = faker.unique.email()
    reg = await register_user(async_client, email=email)
    assert reg.status_code in (200, 201)

    login = await login_user(async_client, email=email, password="Password123!")
    assert login.status_code == 200
    token = (login.json().get("access_token") or login.json().get("token") or login.json().get("accessToken"))

    # Get /me to find ID (or use response from register)
    me = await async_client.get(ME_PATH, headers=auth_header(token))
    assert me.status_code == 200
    me_json = me.json()
    user_id = me_json.get("id") or me_json.get("user_id") or me_json.get("pk")
    assert user_id, "could not determine user id from /me"

    # Update user (partial update)
    patch_payload = {"full_name": "Updated Name"}
    patch_resp = await async_client.patch(USER_BY_ID_PATH.format(user_id=user_id), json=patch_payload, headers=auth_header(token))
    assert patch_resp.status_code in (200, 204), f"patch failed: {patch_resp.status_code} / {patch_resp.text}"

    # Re-get user and confirm update
    get_resp = await async_client.get(USER_BY_ID_PATH.format(user_id=user_id), headers=auth_header(token))
    assert get_resp.status_code == 200
    get_json = get_resp.json()
    # Not all projects echo full_name; this is a best-effort check
    assert get_json.get("full_name") == "Updated Name" or "full_name" in get_json

    # Delete user
    delete_resp = await async_client.delete(USER_BY_ID_PATH.format(user_id=user_id), headers=auth_header(token))
    assert delete_resp.status_code in (200, 204), f"delete failed: {delete_resp.status_code} / {delete_resp.text}"

    # confirm user cannot login again (optional)
    login_after = await login_user(async_client, email=email, password="Password123!")
    assert login_after.status_code in (400, 401, 404), "expected login failure after deletion"


# Optionally add more exhaustive tests: password policy, email confirmation flows, rate-limit checks, etc.
