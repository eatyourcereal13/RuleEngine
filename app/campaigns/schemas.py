from pydantic import BaseModel, ConfigDict, field_validator
from decimal import Decimal
from uuid import UUID
from datetime import datetime
from typing import Optional

from app.core.enums import CampaignStatus


class CampaignBase(BaseModel):
    name: str
    is_managed: bool = True
    budget_limit: Optional[Decimal] = None
    stock_days_left: Optional[int] = None
    stock_days_min: Optional[int] = None
    schedule_enabled: bool = False

    @field_validator('budget_limit')
    @classmethod
    def validate_budget_limit(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError('budget_limit must be >= 0')
        return v


class CampaignCreate(CampaignBase):
    current_status: CampaignStatus = CampaignStatus.ACTIVE
    spend_today: Decimal = Decimal(0)


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    current_status: Optional[CampaignStatus] = None
    is_managed: Optional[bool] = None
    budget_limit: Optional[Decimal] = None
    spend_today: Optional[Decimal] = None
    stock_days_left: Optional[int] = None
    stock_days_min: Optional[int] = None
    schedule_enabled: Optional[bool] = None


class CampaignResponse(CampaignBase):
    id: UUID
    current_status: CampaignStatus
    target_status: Optional[CampaignStatus]
    spend_today: Decimal
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)