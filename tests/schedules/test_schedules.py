import pytest
from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4
from datetime import time

from app.schedules.router import set_schedule, get_schedule, delete_schedule


@pytest.mark.asyncio
class TestSchedulesAPI:
    
    async def test_set_schedule(self, db):
        campaign_id = uuid4()
        
        db.get = AsyncMock(return_value=MagicMock())
        
        request = MagicMock()
        slot_mock = MagicMock()
        slot_mock.model_dump.return_value = {
            "day_of_week": 1,
            "start_time": time(9, 0),
            "end_time": time(21, 0)
        }
        request.slots = [slot_mock]
        
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        db.execute = AsyncMock(return_value=result_mock)
        
        await set_schedule(campaign_id, request, db)
        
        assert db.execute.called
        assert db.commit.called
    
    async def test_get_schedule(self, db):
        campaign_id = uuid4()
        
        db.get = AsyncMock(return_value=MagicMock())
        
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        db.execute = AsyncMock(return_value=result_mock)
        
        schedules = await get_schedule(campaign_id, db)
        
        assert isinstance(schedules, list)
        assert db.execute.called
    
    async def test_delete_schedule(self, db):
        campaign_id = uuid4()
        
        db.get = AsyncMock(return_value=MagicMock())
        db.execute = AsyncMock()
        
        await delete_schedule(campaign_id, db)
        
        assert db.execute.called
        assert db.commit.called
    
    async def test_set_schedule_campaign_not_found(self, db):
        from fastapi import HTTPException
        
        campaign_id = uuid4()
        db.get = AsyncMock(return_value=None)
        
        request = MagicMock()
        
        with pytest.raises(HTTPException) as exc:
            await set_schedule(campaign_id, request, db)
        
        assert exc.value.status_code == 404
    
    async def test_get_schedule_campaign_not_found(self, db):
        from fastapi import HTTPException
        
        campaign_id = uuid4()
        db.get = AsyncMock(return_value=None)
        
        with pytest.raises(HTTPException) as exc:
            await get_schedule(campaign_id, db)
        
        assert exc.value.status_code == 404
    
    async def test_delete_schedule_campaign_not_found(self, db):
        from fastapi import HTTPException
        
        campaign_id = uuid4()
        db.get = AsyncMock(return_value=None)
        
        with pytest.raises(HTTPException) as exc:
            await delete_schedule(campaign_id, db)
        
        assert exc.value.status_code == 404