from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

from app.core.enums import CampaignStatus, TriggeredRule


class EvaluationResult(BaseModel):
    target_status: CampaignStatus
    triggered_rule: Optional[TriggeredRule]
    rule_details: Optional[str] = None


class BulkEvaluationItem(BaseModel):
    campaign_id: UUID
    target_status: CampaignStatus
    triggered_rule: Optional[TriggeredRule]


class BulkEvaluationResponse(BaseModel):
    evaluated: int
    results: list[BulkEvaluationItem]


class EvaluationLogResponse(BaseModel):
    id: UUID
    campaign_id: UUID
    triggered_rule: Optional[TriggeredRule]
    previous_target: Optional[CampaignStatus]
    new_target: CampaignStatus
    context: dict
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)