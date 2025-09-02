import pytest


@pytest.mark.asyncio
async def test_admin_withdrawal_approval_flow(client, auth_headers, admin_user, admin_headers):
    # Create a withdrawal as regular user
    payload = {
        "amount": 500000,
        "currency": "IRR",
        "bank_account": {
            "bank_name": "Melli",
            "account_holder": "Test Biz",
            "iban": "IR820540102680020817909002"
        }
    }
    res = client.post("/payments/withdrawals", json=payload, headers=auth_headers)
    assert res.status_code in (200, 201)
    wid = res.json().get("id") if res.status_code in (200, 201) else None

    # Admin list withdrawals
    res_list = client.get("/admin/finance/withdrawals", headers=admin_headers)
    assert res_list.status_code in (200, 204)

    # Approve if we have an id
    if wid:
        res_appr = client.post(f"/admin/finance/withdrawals/{wid}/approve", headers=admin_headers)
        assert res_appr.status_code in (200, 204)

