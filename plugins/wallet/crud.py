from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, and_
from typing import List, Optional

from .models import Wallet, Transaction, CurrencyType, TransactionType
from .schemas import WalletCreate, WalletUpdate, TransactionCreate, TransactionUpdate

# Wallet CRUD operations
async def create_wallet(db: AsyncSession, wallet: WalletCreate) -> Wallet:
    db_wallet = Wallet(
        user_id=wallet.user_id,
        currency=wallet.currency,
        currency_type=wallet.currency_type
    )
    db.add(db_wallet)
    await db.commit()
    await db.refresh(db_wallet)
    return db_wallet

async def get_wallet(db: AsyncSession, wallet_id: int) -> Optional[Wallet]:
    result = await db.execute(select(Wallet).where(Wallet.id == wallet_id))
    return result.scalars().first()

async def get_user_wallets(db: AsyncSession, user_id: int) -> List[Wallet]:
    result = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
    return result.scalars().all()

async def get_user_wallet_by_currency(db: AsyncSession, user_id: int, currency: str) -> Optional[Wallet]:
    result = await db.execute(
        select(Wallet).where(
            and_(
                Wallet.user_id == user_id,
                Wallet.currency == currency
            )
        )
    )
    return result.scalars().first()

async def update_wallet(db: AsyncSession, wallet_id: int, wallet_data: WalletUpdate) -> Optional[Wallet]:
    await db.execute(
        update(Wallet)
        .where(Wallet.id == wallet_id)
        .values(**wallet_data.dict(exclude_unset=True))
    )
    await db.commit()
    return await get_wallet(db, wallet_id)

# Transaction CRUD operations
async def create_transaction(db: AsyncSession, transaction: TransactionCreate) -> Transaction:
    db_transaction = Transaction(
        wallet_id=transaction.wallet_id,
        amount=transaction.amount,
        transaction_type=transaction.transaction_type,
        reference=transaction.reference,
        description=transaction.description
    )
    db.add(db_transaction)
    await db.commit()
    await db.refresh(db_transaction)
    return db_transaction

async def get_transaction(db: AsyncSession, transaction_id: int) -> Optional[Transaction]:
    result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
    return result.scalars().first()

async def get_wallet_transactions(db: AsyncSession, wallet_id: int) -> List[Transaction]:
    result = await db.execute(select(Transaction).where(Transaction.wallet_id == wallet_id))
    return result.scalars().all()

async def update_transaction(db: AsyncSession, transaction_id: int, transaction_data: TransactionUpdate) -> Optional[Transaction]:
    await db.execute(
        update(Transaction)
        .where(Transaction.id == transaction_id)
        .values(**transaction_data.dict(exclude_unset=True))
    )
    await db.commit()
    return await get_transaction(db, transaction_id)

# Wallet operations
async def deposit(db: AsyncSession, wallet_id: int, amount: float, reference: Optional[str] = None, description: Optional[str] = None) -> Transaction:
    wallet = await get_wallet(db, wallet_id)
    if not wallet:
        raise ValueError("Wallet not found")
    
    # Update wallet balance
    wallet.balance += amount
    
    # Create transaction record
    transaction = Transaction(
        wallet_id=wallet_id,
        amount=amount,
        transaction_type=TransactionType.DEPOSIT,
        reference=reference,
        description=description,
        status="completed"
    )
    
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction

async def withdraw(db: AsyncSession, wallet_id: int, amount: float, reference: Optional[str] = None, description: Optional[str] = None) -> Transaction:
    wallet = await get_wallet(db, wallet_id)
    if not wallet:
        raise ValueError("Wallet not found")
    
    if wallet.balance < amount:
        raise ValueError("Insufficient funds")
    
    # Update wallet balance
    wallet.balance -= amount
    
    # Create transaction record
    transaction = Transaction(
        wallet_id=wallet_id,
        amount=-amount,  # Negative amount for withdrawal
        transaction_type=TransactionType.WITHDRAWAL,
        reference=reference,
        description=description,
        status="completed"
    )
    
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction

async def transfer(db: AsyncSession, from_wallet_id: int, to_wallet_id: int, amount: float, reference: Optional[str] = None, description: Optional[str] = None) -> tuple[Transaction, Transaction]:
    from_wallet = await get_wallet(db, from_wallet_id)
    to_wallet = await get_wallet(db, to_wallet_id)
    
    if not from_wallet or not to_wallet:
        raise ValueError("One or both wallets not found")
    
    if from_wallet.balance < amount:
        raise ValueError("Insufficient funds")
    
    if from_wallet.currency != to_wallet.currency:
        raise ValueError("Cannot transfer between different currencies")
    
    # Update wallet balances
    from_wallet.balance -= amount
    to_wallet.balance += amount
    
    # Create transaction records
    from_transaction = Transaction(
        wallet_id=from_wallet_id,
        amount=-amount,  # Negative amount for sender
        transaction_type=TransactionType.TRANSFER,
        reference=reference,
        description=description,
        status="completed"
    )
    
    to_transaction = Transaction(
        wallet_id=to_wallet_id,
        amount=amount,  # Positive amount for recipient
        transaction_type=TransactionType.TRANSFER,
        reference=reference,
        description=description,
        status="completed"
    )
    
    db.add(from_transaction)
    db.add(to_transaction)
    await db.commit()
    await db.refresh(from_transaction)
    await db.refresh(to_transaction)
    
    return (from_transaction, to_transaction)

async def apply_cashback(db: AsyncSession, wallet_id: int, amount: float, percentage: float, reference: Optional[str] = None) -> Transaction:
    wallet = await get_wallet(db, wallet_id)
    if not wallet:
        raise ValueError("Wallet not found")
    
    cashback_amount = amount * (percentage / 100)
    
    # Update wallet balance
    wallet.balance += cashback_amount
    
    # Create transaction record
    transaction = Transaction(
        wallet_id=wallet_id,
        amount=cashback_amount,
        transaction_type=TransactionType.CASHBACK,
        reference=reference,
        description=f"Cashback {percentage}% on {amount} {wallet.currency}",
        status="completed"
    )
    
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction