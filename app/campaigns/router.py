from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from .models import Campaign
from .schemas import CampaignCreate, CampaignUpdate, CampaignResponse

router = APIRouter()


@router.post("/campaigns", response_model=CampaignResponse, status_code=201)
async def create_campaign(
    data: CampaignCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создает новую рекламную кампанию"""
    campaign = Campaign(**data.model_dump())
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign


@router.get("/campaigns", response_model=list[CampaignResponse])
async def list_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    needs_sync: Optional[bool] = Query(None, description="Только кампании где current_status != target_status"),
    db: AsyncSession = Depends(get_db)
):
    """Возвращает список кампаний с пагинацией и фильтрацией"""
    query = select(Campaign)
    
    if needs_sync is not None:
        if needs_sync:
            query = query.where(Campaign.current_status != Campaign.target_status)
        else:
            query = query.where(Campaign.current_status == Campaign.target_status)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/campaigns/{id}", response_model=CampaignResponse)
async def get_campaign(
    id: UUID, 
    db: AsyncSession = Depends(get_db)
):
    """Возвращает кампанию по ID"""
    campaign = await db.get(Campaign, id)
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    return campaign


@router.patch("/campaigns/{id}", response_model=CampaignResponse)
async def update_campaign(
    id: UUID,
    data: CampaignUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновляет существующую кампанию"""
    campaign = await db.get(Campaign, id)
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(campaign, field, value)
    
    await db.commit()
    await db.refresh(campaign)
    return campaign