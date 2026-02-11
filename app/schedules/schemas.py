from pydantic import BaseModel, ConfigDict, Field, field_validator, ValidationInfo
from uuid import UUID
from datetime import time
from typing import List


class ScheduleSlotBase(BaseModel):
    day_of_week: int = Field(ge=0, le=6)
    start_time: time
    end_time: time

    @field_validator('end_time')
    @classmethod
    def validate_time_range(cls, v: time, info: ValidationInfo) -> time:
        start = info.data.get('start_time')
        if start and v <= start:
            raise ValueError('end_time must be after start_time')
        return v


class ScheduleSlotCreate(ScheduleSlotBase):
    pass


class ScheduleSlotResponse(ScheduleSlotBase):
    id: UUID
    campaign_id: UUID
    
    model_config = ConfigDict(from_attributes=True)


class ScheduleUpdateRequest(BaseModel):
    slots: List[ScheduleSlotCreate]