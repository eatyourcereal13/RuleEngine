from typing import Optional, Tuple
from datetime import datetime

from app.core.enums import TriggeredRule, CampaignStatus
from app.campaigns.models import Campaign
from app.schedules.models import CampaignSchedule
from app.rules.base import Rule


class BudgetExceededRule(Rule):
    @property
    def priority(self) -> int:
        return 4
    
    @property
    def rule_name(self) -> TriggeredRule:
        return TriggeredRule.BUDGET_EXCEEDED
    
    @property
    def target_status(self) -> Optional[CampaignStatus]:
        return CampaignStatus.PAUSED
    
    async def evaluate(
        self,
        campaign: Campaign,
        schedules: Optional[list[CampaignSchedule]] = None,
        current_time: Optional[datetime] = None
    ) -> Tuple[bool, Optional[str]]:
        if (campaign.budget_limit is not None and 
            campaign.spend_today >= campaign.budget_limit):
            return True, f"Расход {campaign.spend_today} >= лимита {campaign.budget_limit}"
        return False, None