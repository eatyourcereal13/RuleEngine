from typing import Optional, Tuple
from datetime import datetime

from app.core.enums import TriggeredRule, CampaignStatus
from app.campaigns.models import Campaign
from app.schedules.models import CampaignSchedule
from app.rules.base import Rule


class LowStockRule(Rule):
    @property
    def priority(self) -> int:
        return 3
    
    @property
    def rule_name(self) -> TriggeredRule:
        return TriggeredRule.LOW_STOCK
    
    @property
    def target_status(self) -> Optional[CampaignStatus]:
        return CampaignStatus.PAUSED
    
    async def evaluate(
        self,
        campaign: Campaign,
        schedules: Optional[list[CampaignSchedule]] = None,
        current_time: Optional[datetime] = None
    ) -> Tuple[bool, Optional[str]]:
        if (campaign.stock_days_min is not None and 
            campaign.stock_days_left is not None and
            campaign.stock_days_left < campaign.stock_days_min):
            return True, f"Остаток {campaign.stock_days_left} дней, минимум {campaign.stock_days_min}"
        return False, None