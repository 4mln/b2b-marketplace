import pytest


@pytest.mark.asyncio
async def test_payment_invoice_pdf(client, auth_headers):
    # This test assumes a payment with id 1 may not exist, so it should 404 or succeed if seeded.
    res = client.get("/payments/1/invoice.pdf", headers=auth_headers)
    # Accept 200 (PDF returned) or 404 (not found), but not 500
    assert res.status_code in (200, 404)
    if res.status_code == 200:
        assert res.headers.get("content-type", "").startswith("application/pdf")

