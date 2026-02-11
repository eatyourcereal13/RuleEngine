from sqlalchemy import Column, String, Boolean, Numeric, Integer, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.core.enums import CampaignStatus


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    current_status = Column(Enum(CampaignStatus), nullable=False, default=CampaignStatus.ACTIVE)
    target_status = Column(Enum(CampaignStatus), nullable=False, default=CampaignStatus.ACTIVE)
    is_managed = Column(Boolean, nullable=False, default=True)
    budget_limit = Column(Numeric(10, 2), nullable=True)
    spend_today = Column(Numeric(10, 2), nullable=False, default=0)
    stock_days_left = Column(Integer, nullable=True)
    stock_days_min = Column(Integer, nullable=True)
    schedule_enabled = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())