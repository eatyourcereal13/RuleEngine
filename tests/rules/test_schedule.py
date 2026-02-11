import pytest
from datetime import datetime, time
from unittest.mock import MagicMock

from app.rules.schedule_rule import ScheduleRule


@pytest.mark.asyncio
class TestScheduleRule:
    
    async def test_within_schedule(self):
        campaign = MagicMock()
        campaign.schedule_enabled = True
        
        schedule = MagicMock()
        schedule.day_of_week = 2
        schedule.start_time = time(9, 0)
        schedule.end_time = time(21, 0)
        
        current_time = datetime(2024, 1, 10, 15, 30)  #Ср 15:30
        
        rule = ScheduleRule()
        triggered, details = await rule.evaluate(campaign, [schedule], current_time)
        
        assert triggered is False
    
    async def test_outside_schedule(self):
        campaign = MagicMock()
        campaign.schedule_enabled = True
        
        schedule = MagicMock()
        schedule.day_of_week = 2
        schedule.start_time = time(9, 0)
        schedule.end_time = time(21, 0)
        
        current_time = datetime(2024, 1, 10, 22, 30)  #Ср 22:30
        
        rule = ScheduleRule()
        triggered, details = await rule.evaluate(campaign, [schedule], current_time)
        
        assert triggered is True
        assert "вне активных слотов" in details
    
    async def test_schedule_disabled(self):
        campaign = MagicMock()
        campaign.schedule_enabled = False
        
        schedule = MagicMock()
        schedule.day_of_week = 2
        schedule.start_time = time(9, 0)
        schedule.end_time = time(21, 0)
        
        current_time = datetime(2024, 1, 10, 22, 30)
        
        rule = ScheduleRule()
        triggered, details = await rule.evaluate(campaign, [schedule], current_time)
        
        assert triggered is False
    
    async def test_no_schedules(self):
        campaign = MagicMock()
        campaign.schedule_enabled = True
        
        current_time = datetime(2024, 1, 10, 22, 30)
        
        rule = ScheduleRule()
        triggered, details = await rule.evaluate(campaign, None, current_time)
        
        assert triggered is False
        assert details is None
    
    async def test_edge_morning(self):
        campaign = MagicMock()
        campaign.schedule_enabled = True
        
        schedule = MagicMock()
        schedule.day_of_week = 2
        schedule.start_time = time(9, 0)
        schedule.end_time = time(21, 0)
        
        current_time = datetime(2024, 1, 10, 9, 0)  #Ср 09:00
        
        rule = ScheduleRule()
        triggered, details = await rule.evaluate(campaign, [schedule], current_time)
        
        assert triggered is False
    
    async def test_edge_evening(self):
        campaign = MagicMock()
        campaign.schedule_enabled = True
        
        schedule = MagicMock()
        schedule.day_of_week = 2
        schedule.start_time = time(9, 0)
        schedule.end_time = time(21, 0)
        
        current_time = datetime(2024, 1, 10, 21, 0)  #Ср 21:00
        
        rule = ScheduleRule()
        triggered, details = await rule.evaluate(campaign, [schedule], current_time)
        
        assert triggered is False
    
    async def test_different_day(self):
        campaign = MagicMock()
        campaign.schedule_enabled = True
        
        schedule = MagicMock()
        schedule.day_of_week = 2  #Ср
        schedule.start_time = time(9, 0)
        schedule.end_time = time(21, 0)
        
        current_time = datetime(2024, 1, 13, 15, 30)  #Сб
        
        rule = ScheduleRule()
        triggered, details = await rule.evaluate(campaign, [schedule], current_time)
        
        assert triggered is True