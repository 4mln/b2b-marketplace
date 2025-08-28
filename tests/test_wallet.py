import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from plugins.wallet.models import Wallet, Transaction
from plugins.wallet.crud import create_wallet, deposit, withdraw, transfer
from plugins.auth.models import User

# Test wallet creation
async def test_create_wallet(db: AsyncSession, test_user: User):
    wallet = await create_wallet(db, {
        "user_id": test_user.id,
        "currency": "USD",
        "currency_type": "fiat"
    })
    
    assert wallet.id is not None
    assert wallet.user_id == test_user.id
    assert wallet.currency == "USD"
    assert wallet.balance == 0.0

# Test deposit functionality
async def test_deposit(db: AsyncSession, test_user: User):
    # Create a wallet first
    wallet = await create_wallet(db, {
        "user_id": test_user.id,
        "currency": "USD",
        "currency_type": "fiat"
    })
    
    # Deposit funds
    transaction = await deposit(db, wallet.id, 100.0, description="Test deposit")
    
    # Refresh wallet to get updated balance
    await db.refresh(wallet)
    
    assert transaction.id is not None
    assert transaction.amount == 100.0
    assert transaction.transaction_type == "deposit"
    assert transaction.status == "completed"
    assert wallet.balance == 100.0

# Test withdrawal functionality
async def test_withdraw(db: AsyncSession, test_user: User):
    # Create a wallet first
    wallet = await create_wallet(db, {
        "user_id": test_user.id,
        "currency": "USD",
        "currency_type": "fiat"
    })
    
    # Deposit funds first
    await deposit(db, wallet.id, 100.0, description="Initial deposit")
    
    # Withdraw funds
    transaction = await withdraw(db, wallet.id, 50.0, description="Test withdrawal")
    
    # Refresh wallet to get updated balance
    await db.refresh(wallet)
    
    assert transaction.id is not None
    assert transaction.amount == -50.0  # Negative amount for withdrawal
    assert transaction.transaction_type == "withdrawal"
    assert transaction.status == "completed"
    assert wallet.balance == 50.0

# Test insufficient funds for withdrawal
async def test_withdraw_insufficient_funds(db: AsyncSession, test_user: User):
    # Create a wallet first
    wallet = await create_wallet(db, {
        "user_id": test_user.id,
        "currency": "USD",
        "currency_type": "fiat"
    })
    
    # Deposit funds first
    await deposit(db, wallet.id, 100.0, description="Initial deposit")
    
    # Try to withdraw more than available
    with pytest.raises(ValueError, match="Insufficient funds"):
        await withdraw(db, wallet.id, 150.0, description="Test withdrawal")
    
    # Refresh wallet to get updated balance
    await db.refresh(wallet)
    
    # Balance should remain unchanged
    assert wallet.balance == 100.0

# Test transfer between wallets
async def test_transfer(db: AsyncSession, test_user: User):
    # Create two wallets
    wallet1 = await create_wallet(db, {
        "user_id": test_user.id,
        "currency": "USD",
        "currency_type": "fiat"
    })
    
    wallet2 = await create_wallet(db, {
        "user_id": test_user.id,  # Same user for simplicity
        "currency": "USD",
        "currency_type": "fiat"
    })
    
    # Deposit funds to first wallet
    await deposit(db, wallet1.id, 100.0, description="Initial deposit")
    
    # Transfer funds
    from_transaction, to_transaction = await transfer(
        db, wallet1.id, wallet2.id, 50.0, description="Test transfer"
    )
    
    # Refresh wallets to get updated balances
    await db.refresh(wallet1)
    await db.refresh(wallet2)
    
    assert from_transaction.id is not None
    assert from_transaction.amount == -50.0  # Negative amount for sender
    assert from_transaction.transaction_type == "transfer"
    assert from_transaction.status == "completed"
    
    assert to_transaction.id is not None
    assert to_transaction.amount == 50.0  # Positive amount for recipient
    assert to_transaction.transaction_type == "transfer"
    assert to_transaction.status == "completed"
    
    assert wallet1.balance == 50.0
    assert wallet2.balance == 50.0

# API endpoint tests (requires running application)
async def test_wallet_api_endpoints(client: AsyncClient, test_user_token: str):
    # Create wallet
    response = await client.post(
        "/api/v1/wallet/",
        json={
            "user_id": 1,  # Assuming test user has ID 1
            "currency": "USD",
            "currency_type": "fiat"
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 201
    wallet_data = response.json()
    assert wallet_data["currency"] == "USD"
    
    # Get user wallets
    response = await client.get(
        "/api/v1/wallet/me",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    wallets_data = response.json()
    assert len(wallets_data["wallets"]) > 0
    
    # Deposit funds
    response = await client.post(
        "/api/v1/wallet/deposit",
        json={
            "amount": 100.0,
            "currency": "USD"
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    transaction_data = response.json()
    assert transaction_data["amount"] == 100.0
    assert transaction_data["transaction_type"] == "deposit"
    
    # Check updated balance
    response = await client.get(
        "/api/v1/wallet/me",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    wallets_data = response.json()
    usd_wallet = next(w for w in wallets_data["wallets"] if w["currency"] == "USD")
    assert usd_wallet["balance"] == 100.0