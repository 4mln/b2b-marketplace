from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from plugins.user.security import get_current_user
from plugins.user.models import User
from .schemas import RFQCreate, RFQOut, QuoteCreate, QuoteOut
from . import crud
from .dependencies import enforce_rfq_limit
from plugins.ratings.crud import get_reputation_score
from sqlalchemy import select
from plugins.seller.models import Seller
# AuthUser import removed as User is now imported from plugins.user.models
from typing import List, Optional


router = APIRouter()


@router.post("/rfqs", response_model=RFQOut)
async def create_rfq_endpoint(
    payload: RFQCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(__import__("app.db.session", fromlist=["get_session"]).get_session),
):
    await enforce_rfq_limit(user.id, db)
    # Spam throttle: simple rate limit based on recent RFQs
    from datetime import datetime, timedelta
    recent = await crud.list_rfqs(db)
    recent = [r for r in recent if r.buyer_id == user.id and getattr(r, 'created_at', datetime.min) >= datetime.utcnow() - timedelta(minutes=5)]
    if len(recent) >= 5:
        raise HTTPException(status_code=429, detail="Too many RFQs. Please wait a few minutes.")
    # Visibility handling: store invited_seller_ids/visibility
    return await crud.create_rfq(db, buyer_id=user.id, data=payload)


@router.get("/rfqs", response_model=list[RFQOut])
async def list_rfqs_endpoint(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    rfqs = await crud.list_rfqs(db)
    visible: list = []
    for r in rfqs:
        vis = getattr(r, 'visibility', None) or 'public'
        if vis == 'public':
            visible.append(r)
        else:
            invited = set(getattr(r, 'invited_seller_ids', []) or [])
            # If current user is buyer or invited seller (by user id), allow
            if r.buyer_id == current_user.id or current_user.id in invited:
                visible.append(r)
    return visible


@router.post("/quotes", response_model=QuoteOut)
async def create_quote_endpoint(
    payload: QuoteCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session),
):
    # Enforce private visibility: only invited sellers can quote
    rfq = await db.get(crud.RFQ, payload.rfq_id)  # type: ignore[attr-defined]
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    vis = getattr(rfq, 'visibility', None) or 'public'
    if vis == 'private':
        invited = set(getattr(rfq, 'invited_seller_ids', []) or [])
        if user.id not in invited and user.id != rfq.buyer_id:
            raise HTTPException(status_code=403, detail="Not invited to this RFQ")
    return await crud.create_quote(db, seller_id=user.id, data=payload)


@router.get("/rfqs/{rfq_id}/quotes", response_model=list[QuoteOut])
async def list_quotes_for_rfq_endpoint(rfq_id: int, db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    quotes = await crud.list_quotes_for_rfq(db, rfq_id)
    # sort by seller reputation desc
    scored: list[tuple[float, any]] = []
    for q in quotes:
        score = await get_reputation_score(db, q.seller_id)
        scored.append((score, q))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [q for _, q in scored]


@router.get("/rfqs/{rfq_id}/matches", response_model=list[dict])
async def suggest_sellers_for_rfq(
    rfq_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session),
):
    """Suggest relevant sellers for an RFQ by simple heuristics:
    - Match on buyer's guild via products.seller join if available later (placeholder)
    - Prefer verified sellers (auth User.kyc_status)
    - Prefer featured/verified sellers; sort by reputation score
    - Optional: use RFQ title/spec keywords against seller business fields
    Returns lightweight seller cards.
    """
    # Load RFQ
    rfq = await db.get(crud.RFQ, rfq_id)  # type: ignore[attr-defined]
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")

    # Base seller list
    result = await db.execute(select(Seller))
    sellers: List[Seller] = result.scalars().all()

    # Score sellers
    scored: list[tuple[float, Seller]] = []
    title = (rfq.title or "").lower()
    for s in sellers:
        score = 0.0
        # Feature/verification boosts
        if getattr(s, "is_verified", False):
            score += 2.0
        if getattr(s, "is_featured", False):
            score += 1.0
        # Business meta boosts
        owner: Optional[AuthUser] = await db.get(AuthUser, s.user_id)
        if owner:
            if getattr(owner, "kyc_status", "") in ("business_verified", "otp_verified"):
                score += 1.0
            # Simple keyword match on business_name/industry
            bn = (getattr(owner, "business_name", "") or "").lower()
            ind = (getattr(owner, "business_industry", "") or "").lower()
            if title and (title in bn or title in ind):
                score += 1.5
        # Reputation boost
        try:
            rep = await get_reputation_score(db, s.id)
            score += float(rep or 0) / 100.0
        except Exception:
            pass
        scored.append((score, s))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = [s for _, s in scored[:limit]]

    cards = []
    for s in top:
        owner: Optional[AuthUser] = await db.get(AuthUser, s.user_id)
        rep = 0.0
        try:
            rep = float(await get_reputation_score(db, s.id) or 0)
        except Exception:
            rep = 0.0
        cards.append({
            "seller_id": s.id,
            "name": s.name,
            "subscription": s.subscription,
            "is_verified": s.is_verified,
            "is_featured": s.is_featured,
            "business_name": getattr(owner, "business_name", None) if owner else None,
            "kyc_status": getattr(owner, "kyc_status", None) if owner else None,
            "reputation": rep,
        })

    return cards

