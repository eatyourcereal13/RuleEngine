from typing import Optional, Tuple
from datetime import datetime

from app.core.enums import TriggeredRule, CampaignStatus
from app.campaigns.models import Campaign
from app.schedules.models import CampaignSchedule
from app.rules.base import Rule


class DisabledManagementRule(Rule):
    @property
    def priority(self) -> int:
        return 1
    
    @property
    def rule_name(self) -> TriggeredRule:
        return TriggeredRule.DISABLED_MANAGEMENT
    
    @property
    def target_status(self) -> Optional[CampaignStatus]:
        return None
    
    async def evaluate(
        self,
        campaign: Campaign,
        schedules: Optional[list[CampaignSchedule]] = None,
        current_time: Optional[datetime] = None
    ) -> Tuple[bool, Optional[str]]:
        if not campaign.is_managed:
            return True, "Управление кампанией отключено"
        return False, None