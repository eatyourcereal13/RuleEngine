from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.campaigns.models import Campaign
from app.schedules.models import CampaignSchedule
from .models import RuleEvaluationLog
from .schemas import EvaluationResult, BulkEvaluationResponse, BulkEvaluationItem, EvaluationLogResponse
from .engine import RuleEngine, get_rule_engine

router = APIRouter()


@router.post("/campaigns/{id}/evaluate", response_model=EvaluationResult)
async def evaluate_campaign(
    id: UUID,
    dry_run: bool = Query(False, description="Не сохранять target_status в БД"),
    db: AsyncSession = Depends(get_db),
    engine: RuleEngine = Depends(get_rule_engine)
):
    """Вычисляет target_status для кампании по правилам"""
    campaign = await db.get(Campaign, id)
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    
    current_time = datetime.now()
    
    schedules = []
    if campaign.schedule_enabled:
        result = await db.execute(
            select(CampaignSchedule).where(CampaignSchedule.campaign_id == id)
        )
        schedules = result.scalars().all()
    
    if dry_run:
        status, rule, details = await engine.evaluate(
            campaign=campaign,
            schedules=schedules,
            current_time=current_time
        )
    else:
        status, rule, details = await engine.evaluate_and_log(
            campaign=campaign,
            schedules=schedules,
            db=db,
            current_time=current_time,
            dry_run=False
        )
        await db.commit()
        await db.refresh(campaign)
    
    return EvaluationResult(
        target_status=status,
        triggered_rule=rule,
        rule_details=details
    )


@router.post("/campaigns/evaluate-all", response_model=BulkEvaluationResponse)
async def evaluate_all(
    dry_run: bool = Query(False, description="Не сохранять target_status в БД"),
    db: AsyncSession = Depends(get_db),
    engine: RuleEngine = Depends(get_rule_engine)
):
    """Вычисляет target_status для всех управляемых кампаний"""
    campaigns_result = await db.execute(
        select(Campaign).where(Campaign.is_managed == True)
    )
    campaigns = campaigns_result.scalars().all()
    
    if not campaigns:
        return BulkEvaluationResponse(evaluated=0, results=[])
    
    campaign_ids = [c.id for c in campaigns]
    
    campaigns_with_schedule = [c for c in campaigns if c.schedule_enabled]
    schedule_ids = [c.id for c in campaigns_with_schedule]
    
    schedules_by_campaign = {}
    if schedule_ids:
        schedules_result = await db.execute(
            select(CampaignSchedule)
            .where(CampaignSchedule.campaign_id.in_(schedule_ids))
        )
        for schedule in schedules_result.scalars().all():
            if schedule.campaign_id not in schedules_by_campaign:
                schedules_by_campaign[schedule.campaign_id] = []
            schedules_by_campaign[schedule.campaign_id].append(schedule)
    
    current_time = datetime.now()
    
    results = []
    for campaign in campaigns:
        schedules = schedules_by_campaign.get(campaign.id, []) if campaign.schedule_enabled else []
        
        if dry_run:
            status, rule, _ = await engine.evaluate(
                campaign=campaign,
                schedules=schedules,
                current_time=current_time
            )
        else:
            status, rule, _ = await engine.evaluate_and_log(
                campaign=campaign,
                schedules=schedules,
                db=db,
                current_time=current_time,
                dry_run=False
            )
        
        results.append(BulkEvaluationItem(
            campaign_id=campaign.id,
            target_status=status,
            triggered_rule=rule
        ))
    
    if not dry_run:
        await db.commit()
    
    return BulkEvaluationResponse(
        evaluated=len(results),
        results=results
    )


@router.get("/campaigns/{id}/evaluation-history", response_model=list[EvaluationLogResponse])
async def get_history(
    id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """История вычислений для кампании"""
    campaign = await db.get(Campaign, id)
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    
    result = await db.execute(
        select(RuleEvaluationLog)
        .where(RuleEvaluationLog.campaign_id == id)
        .order_by(desc(RuleEvaluationLog.created_at))
        .offset(skip)
        .limit(limit)
    )
    
    return result.scalars().all()