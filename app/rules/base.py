from abc import ABC, abstractmethod
from typing import Optional, Tuple
from datetime import datetime

from app.core.enums import TriggeredRule, CampaignStatus
from app.campaigns.models import Campaign
from app.schedules.models import CampaignSchedule


class Rule(ABC):
    """Базовый класс для всех правил"""
    
    @property
    @abstractmethod
    def priority(self) -> int:
        """Приоритет выполнения (1 - наивысший)"""
        pass
    
    @property
    @abstractmethod
    def rule_name(self) -> TriggeredRule:
        """Название правила для логов"""
        pass
    
    @property
    @abstractmethod
    def target_status(self) -> Optional[CampaignStatus]:
        """
        Какой статус установить при срабатывании.
        None - не изменять статус (для disabled_management)
        """
        pass
    
    @abstractmethod
    async def evaluate(
        self,
        campaign: Campaign,
        schedules: Optional[list[CampaignSchedule]] = None,
        current_time: Optional[datetime] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Оценивает правило.
        Возвращает (сработало ли, детали для лога)
        """
        pass