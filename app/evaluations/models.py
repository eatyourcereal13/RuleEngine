from sqlalchemy import Column, Enum, JSON, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.core.enums import CampaignStatus, TriggeredRule


class RuleEvaluationLog(Base):
    __tablename__ = "rule_evaluation_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    triggered_rule = Column(Enum(TriggeredRule), nullable=True)
    previous_target = Column(Enum(CampaignStatus), nullable=True)
    new_target = Column(Enum(CampaignStatus), nullable=False)
    context = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())