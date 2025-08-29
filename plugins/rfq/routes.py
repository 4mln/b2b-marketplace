from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from plugins.user.security import get_current_user
from plugins.user.models import User
from .schemas import RFQCreate, RFQOut, QuoteCreate, QuoteOut
from . import crud
from .dependencies import enforce_rfq_limit
from plugins.ratings.crud import get_reputation_score


router = APIRouter()


@router.post("/rfqs", response_model=RFQOut)
async def create_rfq_endpoint(
    payload: RFQCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    await enforce_rfq_limit(user.id, db)
    return await crud.create_rfq(db, buyer_id=user.id, data=payload)


@router.get("/rfqs", response_model=list[RFQOut])
async def list_rfqs_endpoint(db: AsyncSession = Depends(get_session)):
    return await crud.list_rfqs(db)


@router.post("/quotes", response_model=QuoteOut)
async def create_quote_endpoint(
    payload: QuoteCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    return await crud.create_quote(db, seller_id=user.id, data=payload)


@router.get("/rfqs/{rfq_id}/quotes", response_model=list[QuoteOut])
async def list_quotes_for_rfq_endpoint(rfq_id: int, db: AsyncSession = Depends(get_session)):
    quotes = await crud.list_quotes_for_rfq(db, rfq_id)
    # sort by seller reputation desc
    scored: list[tuple[float, any]] = []
    for q in quotes:
        score = await get_reputation_score(db, q.seller_id)
        scored.append((score, q))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [q for _, q in scored]


