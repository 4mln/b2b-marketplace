from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from plugins.guilds import crud as guilds_crud
from plugins.guilds.schemas import GuildCreate, GuildUpdate, GuildOut
from plugins.products.crud import list_products
from sqlalchemy import update
from plugins.products.models import Product
from plugins.rfq import crud as rfq_crud
from plugins.ads import crud as ads_crud
from plugins.compliance.crud import write_audit_log


router = APIRouter()


@router.get("/guilds", response_model=list[GuildOut])
async def admin_list_guilds(db: AsyncSession = Depends(get_session)):
    return await guilds_crud.list_guilds(db)


@router.post("/guilds", response_model=GuildOut)
async def admin_create_guild(payload: GuildCreate, db: AsyncSession = Depends(get_session)):
    existing = await guilds_crud.get_guild_by_slug(db, payload.slug)
    if existing:
        raise HTTPException(status_code=400, detail="Slug exists")
    return await guilds_crud.create_guild(db, payload)


@router.patch("/guilds/{guild_id}", response_model=GuildOut)
async def admin_update_guild(guild_id: int, payload: GuildUpdate, db: AsyncSession = Depends(get_session)):
    guild = await guilds_crud.update_guild(db, guild_id, payload)
    if not guild:
        raise HTTPException(status_code=404, detail="Not found")
    await write_audit_log(db, data={"actor": "admin", "action": "update_guild", "entity": f"guild:{guild_id}"})
    return guild


@router.get("/products")
async def admin_list_products(db: AsyncSession = Depends(get_session)):
    return await list_products(db, page=1, page_size=50)


@router.get("/rfqs")
async def admin_list_rfqs(db: AsyncSession = Depends(get_session)):
    return await rfq_crud.list_rfqs(db)


@router.get("/ads/campaigns")
async def admin_list_ad_campaigns(db: AsyncSession = Depends(get_session)):
    return await ads_crud.list_campaigns(db)


@router.post("/products/{product_id}/approve")
async def admin_approve_product(product_id: int, db: AsyncSession = Depends(get_session)):
    await db.execute(update(Product).where(Product.id == product_id).values(status="approved"))
    await db.commit()
    await write_audit_log(db, data={"actor": "admin", "action": "approve_product", "entity": f"product:{product_id}"})
    return {"detail": "approved"}


@router.post("/products/{product_id}/reject")
async def admin_reject_product(product_id: int, reason: str = "", db: AsyncSession = Depends(get_session)):
    await db.execute(update(Product).where(Product.id == product_id).values(status="rejected"))
    await db.commit()
    await write_audit_log(db, data={"actor": "admin", "action": f"reject_product:{reason}", "entity": f"product:{product_id}"})
    return {"detail": "rejected"}


