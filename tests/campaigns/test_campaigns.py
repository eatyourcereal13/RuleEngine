# tests/unit/test_campaigns.py
import pytest
from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4
from decimal import Decimal

from app.campaigns.router import create_campaign, list_campaigns, get_campaign, update_campaign
from app.core.enums import CampaignStatus


@pytest.mark.asyncio
class TestCampaignsAPI:
    
    async def test_create_campaign(self):
        db = AsyncMock()
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        
        data = MagicMock()
        data.model_dump.return_value = {
            "name": "Тестовая кампания",
            "is_managed": True,
            "budget_limit": None,
            "stock_days_left": None,
            "stock_days_min": None,
            "schedule_enabled": False,
            "current_status": CampaignStatus.ACTIVE,
            "spend_today": Decimal('0')
        }
        
        campaign = await create_campaign(data, db)
        
        assert db.add.called
        assert db.commit.called
        assert db.refresh.called
    
    async def test_list_campaigns(self, db):
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        db.execute = AsyncMock(return_value=result_mock)
        
        campaigns = await list_campaigns(0, 100, None, db)
        
        assert db.execute.called
        assert isinstance(campaigns, list)
    
    async def test_list_campaigns_with_sync_filter(self, db):
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        db.execute = AsyncMock(return_value=result_mock)
        
        campaigns = await list_campaigns(0, 100, True, db)
        
        assert db.execute.called
        call_args = db.execute.call_args[0][0]
        assert "current_status != campaigns.target_status" in str(call_args)
    
    async def test_list_campaigns_without_sync_filter(self, db):
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        db.execute = AsyncMock(return_value=result_mock)
        
        campaigns = await list_campaigns(0, 100, False, db)
        
        assert db.execute.called
        call_args = db.execute.call_args[0][0]
        assert "current_status = campaigns.target_status" in str(call_args)
    
    async def test_get_campaign_found(self, db):
        campaign_id = uuid4()
        db.get = AsyncMock(return_value=MagicMock())
        
        result = await get_campaign(campaign_id, db)
        
        assert result is not None
        db.get.assert_called_once()
    
    async def test_get_campaign_not_found(self, db):
        from fastapi import HTTPException
        
        campaign_id = uuid4()
        db.get = AsyncMock(return_value=None)
        
        with pytest.raises(HTTPException) as exc:
            await get_campaign(campaign_id, db)
        
        assert exc.value.status_code == 404
    
    async def test_update_campaign(self, db):
        campaign_id = uuid4()
        
        mock_campaign = MagicMock()
        db.get = AsyncMock(return_value=mock_campaign)
        
        data = MagicMock()
        data.model_dump.return_value = {"name": "Новое название"}
        
        result = await update_campaign(campaign_id, data, db)
        
        assert mock_campaign.name == "Новое название"
        assert db.commit.called
        assert db.refresh.called