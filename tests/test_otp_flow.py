import pytest
import types


@pytest.mark.asyncio
async def test_otp_request_and_verify(client, db_session, monkeypatch):
    # Stub external HTTP call (Kavenegar) used in OTP request
    class DummyAsyncClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            return False
        async def get(self, *args, **kwargs):
            class Resp:
                status_code = 200
                def json(self):
                    return {"status": "ok"}
            return Resp()

    import httpx
    monkeypatch.setattr(httpx, "AsyncClient", DummyAsyncClient)

    phone = "+989121234567"
    # Request OTP
    res = client.post("/auth/otp/request", json={"phone": phone})
    assert res.status_code == 200

    # Fetch user to get the generated OTP code
    from sqlalchemy import select
    from plugins.auth.models import User
    result = await db_session.execute(select(User).where(User.phone == phone))
    user = result.scalars().first()
    assert user is not None
    assert user.otp_code is not None

    # Verify OTP
    res2 = client.post("/auth/otp/verify", json={"phone": phone, "code": user.otp_code})
    assert res2.status_code == 200
    data = res2.json()
    assert "access_token" in data
    assert data.get("token_type") == "bearer"

