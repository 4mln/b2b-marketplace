import pytest
import plugins.admin.crud as admin_crud


@pytest.mark.asyncio
async def test_create_and_list_withdrawal(client, auth_headers, monkeypatch):
    # Ensure admin permission checks won't interfere inadvertently
    monkeypatch.setattr(admin_crud, "check_admin_permission", lambda db, admin_id, perm: True)
    # Create withdrawal
    payload = {
        "amount": 1234500,
        "currency": "IRR",
        "bank_account": {
            "bank_name": "Melli",
            "account_holder": "Test Biz",
            "iban": "IR820540102680020817909002"
        }
    }
    res = client.post("/payments/withdrawals", json=payload, headers=auth_headers)
    assert res.status_code in (200, 201)
    data = res.json()
    assert "id" in data
    wid = data["id"]

    # List my withdrawals
    res2 = client.get("/payments/withdrawals", headers=auth_headers)
    assert res2.status_code == 200
    lst = res2.json()
    assert isinstance(lst, list)
    assert any(item.get("id") == wid for item in lst)

