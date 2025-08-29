from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from plugins.user.security import get_current_user
from plugins.user.models import User
from .schemas import CampaignCreate, CampaignOut, PlacementCreate, PlacementOut
from . import crud


router = APIRouter()


@router.post("/campaigns", response_model=CampaignOut)
async def create_campaign_endpoint(payload: CampaignCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_session)):
    return await crud.create_campaign(db, owner_id=user.id, data=payload)


@router.get("/campaigns", response_model=list[CampaignOut])
async def list_campaigns_endpoint(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_session)):
    return await crud.list_campaigns(db, owner_id=user.id)


@router.post("/placements", response_model=PlacementOut)
async def create_placement_endpoint(payload: PlacementCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_session)):
    return await crud.create_placement(db, data=payload)


@router.get("/campaigns/{campaign_id}/placements", response_model=list[PlacementOut])
async def list_placements_endpoint(campaign_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_session)):
    return await crud.list_placements(db, campaign_id)


