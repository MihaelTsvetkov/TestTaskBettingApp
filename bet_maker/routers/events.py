from typing import List, Any

import aiohttp
from fastapi import APIRouter, HTTPException

router = APIRouter()

LINE_PROVIDER_URL = "http://line-provider:8001"


@router.get("/", tags=["Events"])
async def get_events() -> List[Any]:
    """
    Получает список доступных событий из line-provider.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{LINE_PROVIDER_URL}/events") as response:
            if response.status != 200:
                raise HTTPException(status_code=500, detail="Failed to fetch events")
            events = await response.json()
    return events
