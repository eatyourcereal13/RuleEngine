import pytest
from decimal import Decimal
from unittest.mock import MagicMock

from app.rules.budget_exceeded import BudgetExceededRule


@pytest.mark.asyncio
class TestBudgetRule:
    
    async def test_budget_not_exceeded(self):
        campaign = MagicMock()
        campaign.budget_limit = Decimal('1000')
        campaign.spend_today = Decimal('500')
        
        rule = BudgetExceededRule()
        triggered, details = await rule.evaluate(campaign)
        
        assert triggered is False
        assert details is None
    
    async def test_budget_exceeded(self):
        campaign = MagicMock()
        campaign.budget_limit = Decimal('1000')
        campaign.spend_today = Decimal('1500')
        
        rule = BudgetExceededRule()
        triggered, details = await rule.evaluate(campaign)
        
        assert triggered is True
        assert "Расход 1500 >= лимита 1000" in details
    
    async def test_budget_equal_limit(self):
        campaign = MagicMock()
        campaign.budget_limit = Decimal('1000')
        campaign.spend_today = Decimal('1000')
        
        rule = BudgetExceededRule()
        triggered, details = await rule.evaluate(campaign)
        
        assert triggered is True
    
    async def test_no_budget_limit(self):
        campaign = MagicMock()
        campaign.budget_limit = None
        campaign.spend_today = Decimal('1000')
        
        rule = BudgetExceededRule()
        triggered, details = await rule.evaluate(campaign)
        
        assert triggered is False