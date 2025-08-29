from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from plugins.user.security import get_current_user
from plugins.user.models import User
from plugins.search.schemas import SavedSearchCreate, SavedSearchOut, SearchResponse, SearchResult
from plugins.search.crud import create_saved_search, list_saved_searches, log_search
from plugins.products.models import Product
from sqlalchemy import select
import os, httpx


router = APIRouter()


@router.post("/saved", response_model=SavedSearchOut)
async def save_search(payload: SavedSearchCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_session)):
    return await create_saved_search(db, user.id, payload)


@router.get("/saved", response_model=list[SavedSearchOut])
async def get_saved_searches(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_session)):
    return await list_saved_searches(db, user.id)


@router.get("/products", response_model=SearchResponse)
async def search_products(q: str = Query(""), db: AsyncSession = Depends(get_session)):
    if q:
        try:
            await log_search(db, q)
        except Exception:
            pass
    # Try MeiliSearch
    try:
        meili_url = os.getenv("MEILI_URL", "http://localhost:7700")
        meili_key = os.getenv("MEILI_KEY")
        headers = {"X-Meili-API-Key": meili_key} if meili_key else {}
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.post(
                f"{meili_url}/indexes/products/search",
                json={"q": q, "limit": 50},
                headers=headers,
            )
            if resp.status_code == 200:
                data = resp.json()
                hits = data.get("hits", [])
                items = [
                    SearchResult(
                        id=h.get("id"),
                        name=h.get("name", ""),
                        description=h.get("description"),
                        price=h.get("price", 0.0),
                    )
                    for h in hits
                ]
                return SearchResponse(items=items)
    except Exception as e:
        print(f"[MeiliSearch] fallback due to error: {e}")

    # Fallback DB search
    result = await db.execute(select(Product).where(Product.name.ilike(f"%{q}%")).limit(50))
    items = [
        SearchResult(id=p.id, name=p.name, description=p.description, price=p.price)
        for p in result.scalars().all()
    ]
    return SearchResponse(items=items)


@router.post("/sync/products")
async def sync_products(db: AsyncSession = Depends(get_session)):
    products = (await db.execute(select(Product))).scalars().all()
    meili_url = os.getenv("MEILI_URL", "http://localhost:7700")
    meili_key = os.getenv("MEILI_KEY")
    headers = {"X-Meili-API-Key": meili_key} if meili_key else {}
    docs = [
        {"id": p.id, "name": p.name, "description": p.description, "price": p.price}
        for p in products
    ]
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{meili_url}/indexes/products/documents",
                json=docs,
                headers=headers,
            )
            if resp.status_code >= 400:
                return {"indexed": 0, "error": resp.text}
    except Exception as e:
        return {"indexed": 0, "error": str(e)}
    return {"indexed": len(docs)}


@router.post("/indexes/products/settings")
async def set_products_index_settings(
    synonyms: dict | None = None,
    typo_tolerance: dict | None = None,
):
    meili_url = os.getenv("MEILI_URL", "http://localhost:7700")
    meili_key = os.getenv("MEILI_KEY")
    headers = {"X-Meili-API-Key": meili_key} if meili_key else {}
    payloads = []
    if synonyms is not None:
        payloads.append(("synonyms", synonyms))
    if typo_tolerance is not None:
        payloads.append(("typo-tolerance", typo_tolerance))
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            results = []
            for path, body in payloads:
                resp = await client.patch(f"{meili_url}/indexes/products/settings/{path}", json=body, headers=headers)
                results.append({"path": path, "status": resp.status_code})
            return {"updated": results}
    except Exception as e:
        return {"error": str(e)}


