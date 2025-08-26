from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.db import get_session
from . import schemas, crud

router = APIRouter()

# -----------------------------
# List all transactions
# -----------------------------
@router.get("/", response_model=List[schemas.TransactionOut])
async def list_transactions(db: AsyncSession = Depends(get_session)):
    return await crud.get_transactions(db)

# -----------------------------
# Create a payment
# -----------------------------
@router.post("/", response_model=schemas.TransactionOut)
async def create_transaction(transaction: schemas.TransactionCreate, db: AsyncSession = Depends(get_session)):
    return await crud.create_transaction(db, transaction)

# -----------------------------
# Get payment by ID
# -----------------------------
@router.get("/{transaction_id}", response_model=schemas.TransactionOut)
async def get_transaction(transaction_id: int, db: AsyncSession = Depends(get_session)):
    transaction = await crud.get_transaction_by_id(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction
