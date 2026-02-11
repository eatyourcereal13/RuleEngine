from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.database import get_db
from app.campaigns.models import Campaign
from .models import CampaignSchedule
from .schemas import ScheduleSlotResponse, ScheduleUpdateRequest

router = APIRouter()


@router.put("/campaigns/{id}/schedule", response_model=list[ScheduleSlotResponse])
async def set_schedule(
    id: UUID,
    request: ScheduleUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Устанавливает расписание для кампании (заменяет все существующие слоты)"""
    campaign = await db.get(Campaign, id)
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    
    await db.execute(
        delete(CampaignSchedule).where(CampaignSchedule.campaign_id == id)
    )
    
    for slot_data in request.slots:
        slot = CampaignSchedule(
            campaign_id=id,
            **slot_data.model_dump()
        )
        db.add(slot)
    
    await db.commit()
    
    result = await db.execute(
        select(CampaignSchedule).where(CampaignSchedule.campaign_id == id)
    )
    return result.scalars().all()


@router.get("/campaigns/{id}/schedule", response_model=list[ScheduleSlotResponse])
async def get_schedule(
    id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Возвращает расписание кампании"""
    campaign = await db.get(Campaign, id)
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    
    result = await db.execute(
        select(CampaignSchedule).where(CampaignSchedule.campaign_id == id)
    )
    return result.scalars().all()


@router.delete("/campaigns/{id}/schedule", status_code=204)
async def delete_schedule(
    id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Удаляет все расписание кампании"""
    campaign = await db.get(Campaign, id)
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    
    await db.execute(
        delete(CampaignSchedule).where(CampaignSchedule.campaign_id == id)
    )
    await db.commit()