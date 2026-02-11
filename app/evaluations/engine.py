from datetime import datetime
from typing import List, Tuple, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import CampaignStatus, TriggeredRule
from app.campaigns.models import Campaign
from app.schedules.models import CampaignSchedule
from app.rules import get_all_rules
from app.rules.base import Rule
from .models import RuleEvaluationLog


class RuleEngine:
    """Движок правил. Применяет правила строго по приоритету."""
    
    _rules: Optional[List[Rule]] = None
    
    @classmethod
    def _get_rules(cls) -> List[Rule]:
        """Кэширование правил от себя добавил"""
        if cls._rules is None:
            cls._rules = get_all_rules()
        return cls._rules
    
    async def evaluate(
        self,
        campaign: Campaign,
        schedules: Optional[List[CampaignSchedule]] = None,
        current_time: Optional[datetime] = None
    ) -> Tuple[CampaignStatus, Optional[TriggeredRule], Optional[str]]:
        """
        Применяет правила к кампании.
        
        Returns:
            (target_status, triggered_rule, details)
            triggered_rule = None если правила не сработали (статус ACTIVE)
        """
        current_time = current_time or datetime.now()
        schedules = schedules or []
        
        for rule in self._get_rules():
            triggered, details = await rule.evaluate(
                campaign=campaign,
                schedules=schedules,
                current_time=current_time
            )
            
            if triggered:
                if rule.target_status is None:
                    return campaign.target_status or CampaignStatus.ACTIVE, rule.rule_name, details
                
                return rule.target_status, rule.rule_name, details
        
        return CampaignStatus.ACTIVE, None, None
    
    async def evaluate_and_log(
        self,
        campaign: Campaign,
        db: AsyncSession,
        schedules: Optional[List[CampaignSchedule]] = None,
        current_time: Optional[datetime] = None,
        dry_run: bool = False
    ) -> Tuple[CampaignStatus, Optional[TriggeredRule], Optional[str]]:
        previous_target = campaign.target_status
        
        status, rule, details = await self.evaluate(
            campaign=campaign,
            schedules=schedules,
            current_time=current_time
        )
        
        context = self._build_context(campaign, schedules, current_time)
        
        log = RuleEvaluationLog(
            campaign_id=campaign.id,
            triggered_rule=rule,
            previous_target=previous_target,
            new_target=status,
            context=context,
            created_at=current_time
        )
        
        db.add(log)
        
        if not dry_run:
            campaign.target_status = status
        
        return status, rule, details
    
    def _build_context(
        self,
        campaign: Campaign,
        schedules: List[CampaignSchedule],
        current_time: datetime
    ) -> dict:
        """Создает снапшот данных для логирования"""
        
        schedule_slots = []
        for slot in schedules:
            schedule_slots.append({
                "day": slot.day_of_week,
                "start": slot.start_time.isoformat(),
                "end": slot.end_time.isoformat()
            })
        
        return {
            "current_status": campaign.current_status.value,
            "is_managed": campaign.is_managed,
            "budget_limit": str(campaign.budget_limit) if campaign.budget_limit else None,
            "spend_today": str(campaign.spend_today),
            "stock_days_left": campaign.stock_days_left,
            "stock_days_min": campaign.stock_days_min,
            "schedule_enabled": campaign.schedule_enabled,
            
            "current_time": current_time.isoformat(),
            "current_weekday": current_time.weekday(),
            "schedules_count": len(schedules),
            "schedules": schedule_slots[:5],
            
            "engine_version": "1.0"  # версия движка как задел на будущее
        }


_engine_instance: Optional[RuleEngine] = None


def get_rule_engine() -> RuleEngine:
    """Возвращает экземпляр RuleEngine"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = RuleEngine()
    return _engine_instance