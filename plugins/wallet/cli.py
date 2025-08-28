import asyncio
import argparse
import sys
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from plugins.auth.models import User
from plugins.wallet.models import Wallet, Transaction
from plugins.wallet.crud import (
    create_wallet, get_user_wallets, get_user_wallet_by_currency,
    deposit, withdraw, transfer, apply_cashback
)

async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    """Get a user by ID."""
    from sqlalchemy.future import select
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        print(f"User with ID {user_id} not found")
        sys.exit(1)
    return user

async def create_user_wallet(db: AsyncSession, user_id: int, currency: str, currency_type: str) -> None:
    """Create a new wallet for a user."""
    # Check if user exists
    user = await get_user_by_id(db, user_id)
    
    # Check if wallet already exists
    existing_wallet = await get_user_wallet_by_currency(db, user_id, currency)
    if existing_wallet:
        print(f"User already has a wallet for {currency}")
        return
    
    # Create wallet
    wallet = await create_wallet(db, {
        "user_id": user_id,
        "currency": currency,
        "currency_type": currency_type
    })
    
    print(f"Created wallet for user {user_id} with currency {currency} (ID: {wallet.id})")

async def list_user_wallets(db: AsyncSession, user_id: int) -> None:
    """List all wallets for a user."""
    # Check if user exists
    user = await get_user_by_id(db, user_id)
    
    # Get wallets
    wallets = await get_user_wallets(db, user_id)
    
    if not wallets:
        print(f"User {user_id} has no wallets")
        return
    
    print(f"Wallets for user {user_id}:")
    for wallet in wallets:
        print(f"  ID: {wallet.id}, Currency: {wallet.currency}, Type: {wallet.currency_type}, Balance: {wallet.balance}")

async def deposit_to_wallet(db: AsyncSession, user_id: int, currency: str, amount: float) -> None:
    """Deposit funds to a user's wallet."""
    # Check if user exists
    user = await get_user_by_id(db, user_id)
    
    # Get wallet
    wallet = await get_user_wallet_by_currency(db, user_id, currency)
    if not wallet:
        print(f"User {user_id} has no wallet for {currency}")
        return
    
    # Deposit funds
    transaction = await deposit(db, wallet.id, amount, description="CLI deposit")
    
    print(f"Deposited {amount} {currency} to wallet {wallet.id}")
    print(f"New balance: {wallet.balance} {currency}")

async def withdraw_from_wallet(db: AsyncSession, user_id: int, currency: str, amount: float) -> None:
    """Withdraw funds from a user's wallet."""
    # Check if user exists
    user = await get_user_by_id(db, user_id)
    
    # Get wallet
    wallet = await get_user_wallet_by_currency(db, user_id, currency)
    if not wallet:
        print(f"User {user_id} has no wallet for {currency}")
        return
    
    # Withdraw funds
    try:
        transaction = await withdraw(db, wallet.id, amount, description="CLI withdrawal")
        print(f"Withdrew {amount} {currency} from wallet {wallet.id}")
        print(f"New balance: {wallet.balance} {currency}")
    except ValueError as e:
        print(f"Error: {str(e)}")

async def transfer_funds(db: AsyncSession, from_user_id: int, to_user_id: int, currency: str, amount: float) -> None:
    """Transfer funds between users."""
    # Check if users exist
    from_user = await get_user_by_id(db, from_user_id)
    to_user = await get_user_by_id(db, to_user_id)
    
    # Get wallets
    from_wallet = await get_user_wallet_by_currency(db, from_user_id, currency)
    if not from_wallet:
        print(f"User {from_user_id} has no wallet for {currency}")
        return
    
    to_wallet = await get_user_wallet_by_currency(db, to_user_id, currency)
    if not to_wallet:
        print(f"User {to_user_id} has no wallet for {currency}")
        return
    
    # Transfer funds
    try:
        from_transaction, to_transaction = await transfer(
            db, 
            from_wallet.id, 
            to_wallet.id, 
            amount, 
            description=f"CLI transfer from user {from_user_id} to user {to_user_id}"
        )
        print(f"Transferred {amount} {currency} from user {from_user_id} to user {to_user_id}")
        print(f"Sender's new balance: {from_wallet.balance} {currency}")
        print(f"Recipient's new balance: {to_wallet.balance} {currency}")
    except ValueError as e:
        print(f"Error: {str(e)}")

async def apply_wallet_cashback(db: AsyncSession, user_id: int, currency: str, amount: float, percentage: float) -> None:
    """Apply cashback to a user's wallet."""
    # Check if user exists
    user = await get_user_by_id(db, user_id)
    
    # Get wallet
    wallet = await get_user_wallet_by_currency(db, user_id, currency)
    if not wallet:
        print(f"User {user_id} has no wallet for {currency}")
        return
    
    # Apply cashback
    try:
        transaction = await apply_cashback(
            db, 
            wallet.id, 
            amount, 
            percentage, 
            reference="CLI cashback"
        )
        cashback_amount = amount * (percentage / 100)
        print(f"Applied {percentage}% cashback ({cashback_amount} {currency}) to wallet {wallet.id}")
        print(f"New balance: {wallet.balance} {currency}")
    except ValueError as e:
        print(f"Error: {str(e)}")

async def main():
    parser = argparse.ArgumentParser(description="Wallet CLI utility")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create wallet command
    create_parser = subparsers.add_parser("create", help="Create a new wallet")
    create_parser.add_argument("--user", type=int, required=True, help="User ID")
    create_parser.add_argument("--currency", type=str, required=True, help="Currency code")
    create_parser.add_argument("--type", type=str, default="fiat", choices=["fiat", "crypto"], help="Currency type")
    
    # List wallets command
    list_parser = subparsers.add_parser("list", help="List user wallets")
    list_parser.add_argument("--user", type=int, required=True, help="User ID")
    
    # Deposit command
    deposit_parser = subparsers.add_parser("deposit", help="Deposit funds")
    deposit_parser.add_argument("--user", type=int, required=True, help="User ID")
    deposit_parser.add_argument("--currency", type=str, required=True, help="Currency code")
    deposit_parser.add_argument("--amount", type=float, required=True, help="Amount to deposit")
    
    # Withdraw command
    withdraw_parser = subparsers.add_parser("withdraw", help="Withdraw funds")
    withdraw_parser.add_argument("--user", type=int, required=True, help="User ID")
    withdraw_parser.add_argument("--currency", type=str, required=True, help="Currency code")
    withdraw_parser.add_argument("--amount", type=float, required=True, help="Amount to withdraw")
    
    # Transfer command
    transfer_parser = subparsers.add_parser("transfer", help="Transfer funds")
    transfer_parser.add_argument("--from", type=int, required=True, dest="from_user", help="Sender user ID")
    transfer_parser.add_argument("--to", type=int, required=True, help="Recipient user ID")
    transfer_parser.add_argument("--currency", type=str, required=True, help="Currency code")
    transfer_parser.add_argument("--amount", type=float, required=True, help="Amount to transfer")
    
    # Cashback command
    cashback_parser = subparsers.add_parser("cashback", help="Apply cashback")
    cashback_parser.add_argument("--user", type=int, required=True, help="User ID")
    cashback_parser.add_argument("--currency", type=str, required=True, help="Currency code")
    cashback_parser.add_argument("--amount", type=float, required=True, help="Original transaction amount")
    cashback_parser.add_argument("--percentage", type=float, required=True, help="Cashback percentage")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    async for db in get_async_session():
        if args.command == "create":
            await create_user_wallet(db, args.user, args.currency, args.type)
        elif args.command == "list":
            await list_user_wallets(db, args.user)
        elif args.command == "deposit":
            await deposit_to_wallet(db, args.user, args.currency, args.amount)
        elif args.command == "withdraw":
            await withdraw_from_wallet(db, args.user, args.currency, args.amount)
        elif args.command == "transfer":
            await transfer_funds(db, args.from_user, args.to, args.currency, args.amount)
        elif args.command == "cashback":
            await apply_wallet_cashback(db, args.user, args.currency, args.amount, args.percentage)

if __name__ == "__main__":
    asyncio.run(main())