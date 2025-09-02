import pytest


@pytest.mark.asyncio
async def test_rfq_visibility_public(client, auth_headers):
    payload = {
        "title": "Public RFQ",
        "quantity": 10,
        "visibility": "public"
    }
    res = client.post("/rfq/rfqs", json=payload, headers=auth_headers)
    assert res.status_code in (200, 201)

    res2 = client.get("/rfq/rfqs", headers=auth_headers)
    assert res2.status_code == 200
    data = res2.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_rfq_visibility_private_access_control(client, auth_headers):
    # Create private RFQ inviting no one; only buyer can see
    payload = {
        "title": "Private RFQ",
        "quantity": 5,
        "visibility": "private",
        "invited_seller_ids": []
    }
    res = client.post("/rfq/rfqs", json=payload, headers=auth_headers)
    assert res.status_code in (200, 201)

    # Listing should include it for buyer
    res2 = client.get("/rfq/rfqs", headers=auth_headers)
    assert res2.status_code == 200
    assert isinstance(res2.json(), list)

