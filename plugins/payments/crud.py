from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import Transaction
from .schemas import TransactionCreate

async def init_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Transaction.metadata.create_all)

# -----------------------------
# Create transaction
# -----------------------------
async def create_transaction(db: AsyncSession, transaction: TransactionCreate):
    tx = Transaction(**transaction.dict())
    db.add(tx)
    await db.commit()
    await db.refresh(tx)
    return tx

# -----------------------------
# Get all transactions
# -----------------------------
async def get_transactions(db: AsyncSession):
    result = await db.execute(select(Transaction))
    return result.scalars().all()

# -----------------------------
# Get transaction by ID
# -----------------------------
async def get_transaction_by_id(db: AsyncSession, transaction_id: int):
    result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
    return result.scalars().first()
