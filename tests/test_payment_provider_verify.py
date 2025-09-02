import pytest


@pytest.mark.asyncio
async def test_payment_verify_with_stubbed_provider(client, db_session, auth_headers):
    # Seed a pending payment for the test user
    from plugins.payments.models import Payment, PaymentStatus, PaymentType
    from sqlalchemy import insert, select
    # Find user id from token context is not trivial; use test user email from fixture assumptions
    # Retrieve user created by fixture
    from plugins.user.models import User
    result = await db_session.execute(select(User).where(User.email == "test@example.com"))
    user = result.scalars().first()
    assert user is not None

    payment = Payment(
        user_id=user.id,
        amount=10000.0,
        currency="IRR",
        payment_method="zarinpal",
        payment_type=PaymentType.WALLET_TOPUP,
        status=PaymentStatus.PENDING,
        reference_id="test_ref_1",
        description="Test payment"
    )
    db_session.add(payment)
    await db_session.commit()
    await db_session.refresh(payment)

    # Stub provider factory to always succeed on verify
    import plugins.payments.iran_providers as providers

    class DummyProvider:
        async def verify_payment(self, authority, amount):
            return {
                "success": True,
                "transaction_id": "TX123",
                "provider_response": {"ok": True}
            }

    def dummy_factory(name, cfg):
        return DummyProvider()

    import plugins.payments.iran_providers as iran_providers
    original_factory = iran_providers.IranPaymentFactory.create_provider
    iran_providers.IranPaymentFactory.create_provider = staticmethod(dummy_factory)

    try:
        res = client.post(
            "/payments/verify",
            json={"payment_id": payment.id, "authority": "AUTH123"},
            headers=auth_headers,
        )
        assert res.status_code == 200
        body = res.json()
        assert body.get("success") is True
    finally:
        # Restore factory
        iran_providers.IranPaymentFactory.create_provider = original_factory

