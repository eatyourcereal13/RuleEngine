import pytest
from unittest.mock import MagicMock
from datetime import datetime, time
from decimal import Decimal

from app.evaluations.engine import RuleEngine
from app.core.enums import CampaignStatus, TriggeredRule


@pytest.fixture
def engine():
    return RuleEngine()


@pytest.fixture
def mock_campaign():
    campaign = MagicMock()
    campaign.id = "test-id"
    campaign.name = "test"
    campaign.current_status = "active"
    campaign.target_status = None
    campaign.is_managed = True
    campaign.budget_limit = None
    campaign.spend_today = Decimal('0')
    campaign.stock_days_left = None
    campaign.stock_days_min = None
    campaign.schedule_enabled = False
    return campaign


@pytest.fixture
def schedule_wednesday():
    schedule = MagicMock()
    schedule.day_of_week = 2
    schedule.start_time = time(9, 0)
    schedule.end_time = time(21, 0)
    return [schedule]


@pytest.mark.asyncio
class TestScenarios:
    """5 сценариев из ТЗ"""
    
    async def test_scenario_1_schedule(self, engine, mock_campaign, schedule_wednesday):
        mock_campaign.schedule_enabled = True
        current_time = datetime(2024, 1, 10, 22, 30)
        
        status, rule, details = await engine.evaluate(mock_campaign, schedule_wednesday, current_time)
        
        assert status == CampaignStatus.PAUSED
        assert rule == TriggeredRule.SCHEDULE
    
    async def test_scenario_2_low_stock(self, engine, mock_campaign):
        mock_campaign.stock_days_left = 3
        mock_campaign.stock_days_min = 5
        
        status, rule, details = await engine.evaluate(mock_campaign)
        
        assert status == CampaignStatus.PAUSED
        assert rule == TriggeredRule.LOW_STOCK
    
    async def test_scenario_3_budget(self, engine, mock_campaign):
        mock_campaign.budget_limit = Decimal('1000')
        mock_campaign.spend_today = Decimal('1000')
        
        status, rule, details = await engine.evaluate(mock_campaign)
        
        assert status == CampaignStatus.PAUSED
        assert rule == TriggeredRule.BUDGET_EXCEEDED
    
    async def test_scenario_4_priority(self, engine, mock_campaign, schedule_wednesday):
        mock_campaign.schedule_enabled = True
        mock_campaign.budget_limit = Decimal('1000')
        mock_campaign.spend_today = Decimal('1500')
        current_time = datetime(2024, 1, 10, 22, 30)
        
        status, rule, details = await engine.evaluate(mock_campaign, schedule_wednesday, current_time)
        
        assert status == CampaignStatus.PAUSED
        assert rule == TriggeredRule.SCHEDULE
    
    async def test_scenario_5_no_restrictions(self, engine, mock_campaign):
        status, rule, details = await engine.evaluate(mock_campaign)
        
        assert status == CampaignStatus.ACTIVE
        assert rule is None