from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import Campaign, Placement
from .schemas import CampaignCreate, PlacementCreate


async def create_campaign(db: AsyncSession, owner_id: int, data: CampaignCreate) -> Campaign:
    campaign = Campaign(owner_id=owner_id, **data.dict())
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign


async def list_campaigns(db: AsyncSession, owner_id: int | None = None) -> list[Campaign]:
    query = select(Campaign)
    if owner_id is not None:
        query = query.where(Campaign.owner_id == owner_id)
    result = await db.execute(query)
    return result.scalars().all()


async def create_placement(db: AsyncSession, data: PlacementCreate) -> Placement:
    placement = Placement(**data.dict())
    db.add(placement)
    await db.commit()
    await db.refresh(placement)
    return placement


async def list_placements(db: AsyncSession, campaign_id: int) -> list[Placement]:
    result = await db.execute(select(Placement).where(Placement.campaign_id == campaign_id))
    return result.scalars().all()


