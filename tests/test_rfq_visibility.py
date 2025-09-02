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
async def test_rfq_visibility_private_access_control(client, auth_headers, auth_headers_user2, test_user_2):
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
    buyer_list = res2.json()
    assert any(r.get("title") == "Private RFQ" for r in buyer_list)

    # Invited seller cannot see unless invited; create a new private RFQ inviting seller2
    payload2 = {
        "title": "Private RFQ 2",
        "quantity": 7,
        "visibility": "private",
        "invited_seller_ids": [test_user_2.id]
    }
    res3 = client.post("/rfq/rfqs", json=payload2, headers=auth_headers)
    assert res3.status_code in (200, 201)

    # seller2 should see the invited RFQ
    res4 = client.get("/rfq/rfqs", headers=auth_headers_user2)
    assert res4.status_code == 200
    seller_list = res4.json()
    assert any(r.get("title") == "Private RFQ 2" for r in seller_list)

