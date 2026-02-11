import pytest
from unittest.mock import MagicMock

from app.rules.low_stock import LowStockRule


@pytest.mark.asyncio
class TestLowStockRule:
    
    async def test_stock_above_min(self):
        campaign = MagicMock()
        campaign.stock_days_left = 10
        campaign.stock_days_min = 5
        
        rule = LowStockRule()
        triggered, details = await rule.evaluate(campaign)
        
        assert triggered is False
    
    async def test_stock_below_min(self):
        campaign = MagicMock()
        campaign.stock_days_left = 3
        campaign.stock_days_min = 5
        
        rule = LowStockRule()
        triggered, details = await rule.evaluate(campaign)
        
        assert triggered is True
        assert "3 дней, минимум 5" in details
    
    async def test_stock_equal_min(self):
        campaign = MagicMock()
        campaign.stock_days_left = 5
        campaign.stock_days_min = 5
        
        rule = LowStockRule()
        triggered, details = await rule.evaluate(campaign)
        
        assert triggered is False
    
    async def test_no_stock_days_min(self):
        campaign = MagicMock()
        campaign.stock_days_min = None
        campaign.stock_days_left = 3
        
        rule = LowStockRule()
        triggered, details = await rule.evaluate(campaign)
        
        assert triggered is False
    
    async def test_no_stock_days_left(self):
        campaign = MagicMock()
        campaign.stock_days_min = 5
        campaign.stock_days_left = None
        
        rule = LowStockRule()
        triggered, details = await rule.evaluate(campaign)
        
        assert triggered is False