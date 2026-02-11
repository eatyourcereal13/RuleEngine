import pytest
from unittest.mock import MagicMock

from app.rules.disabled_management import DisabledManagementRule


@pytest.mark.asyncio
class TestDisabledManagementRule:
    
    async def test_management_enabled(self):
        campaign = MagicMock()
        campaign.is_managed = True
        
        rule = DisabledManagementRule()
        triggered, details = await rule.evaluate(campaign)
        
        assert triggered is False
    
    async def test_management_disabled(self):
        campaign = MagicMock()
        campaign.is_managed = False
        
        rule = DisabledManagementRule()
        triggered, details = await rule.evaluate(campaign)
        
        assert triggered is True
        assert "Управление кампанией отключено" in details