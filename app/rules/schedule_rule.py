from typing import Optional, Tuple
from datetime import datetime

from app.core.enums import TriggeredRule, CampaignStatus
from app.campaigns.models import Campaign
from app.schedules.models import CampaignSchedule
from app.rules.base import Rule


class ScheduleRule(Rule):
    @property
    def priority(self) -> int:
        return 2
    
    @property
    def rule_name(self) -> TriggeredRule:
        return TriggeredRule.SCHEDULE
    
    @property
    def target_status(self) -> Optional[CampaignStatus]:
        return CampaignStatus.PAUSED
    
    async def evaluate(
        self,
        campaign: Campaign,
        schedules: Optional[list[CampaignSchedule]] = None,
        current_time: Optional[datetime] = None
    ) -> Tuple[bool, Optional[str]]:
        if not campaign.schedule_enabled or not schedules:
            return False, None
        
        now = current_time or datetime.now()
        weekday = now.weekday()
        current_time_only = now.time()
        
        for slot in schedules:
            if slot.day_of_week == weekday:
                if slot.start_time <= current_time_only <= slot.end_time:
                    return False, None
        
        active_slots = [
            f"{s.day_of_week} {s.start_time}-{s.end_time}" 
            for s in schedules if s.day_of_week == weekday
        ]
        slots_info = ", ".join(active_slots) if active_slots else "нет слотов на сегодня"
        
        return True, f"Текущее время {current_time_only} вне активных слотов ({slots_info})"