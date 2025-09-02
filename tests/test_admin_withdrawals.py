import pytest
import plugins.admin.crud as admin_crud


@pytest.mark.asyncio
async def test_admin_withdrawal_approval_flow(client, auth_headers, admin_user, admin_headers, monkeypatch):
    # Ensure admin permission always passes for this test
    monkeypatch.setattr(admin_crud, "check_admin_permission", lambda db, admin_id, perm: True)
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
    wid = res.json().get("id")

    # Admin list withdrawals
    res_list = client.get("/admin/finance/withdrawals", headers=admin_headers)
    assert res_list.status_code == 200
    lst = res_list.json()
    assert isinstance(lst, list)

    # Approve if we have an id
    res_appr = client.post(f"/admin/finance/withdrawals/{wid}/approve", headers=admin_headers)
    assert res_appr.status_code in (200, 204, 200)

