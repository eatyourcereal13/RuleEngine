from sqlalchemy import Column, Integer, Time, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base


class CampaignSchedule(Base):
    __tablename__ = "campaign_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            'campaign_id', 'day_of_week', 'start_time', 'end_time',
            name='uq_campaign_schedule_unique_slot'
        ),
    )