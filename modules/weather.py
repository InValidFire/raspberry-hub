from fastapi import APIRouter
from common.database import APIKey, DoesNotExist
from common.constants import RECORD_NOT_FOUND

import aiohttp

router = APIRouter()

url = "http://api.weatherbit.io/v2.0"

async def load_apikey():
    try:
        apikey = APIKey.get_by_id("weatherbit")
        params = {"key": apikey.key}
        return params
    except DoesNotExist:
        return RECORD_NOT_FOUND

@router.get("/weather/forecast")
async def get_weather(city: str):
    params = load_apikey()
    if params is RECORD_NOT_FOUND:
        return params
    params['city'] = city
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{url}/current", params=params) as resp:
            return await resp.json()

@router.get("/weather/alerts")
async def get_alerts(city: str):
    params = load_apikey()
    if params is RECORD_NOT_FOUND:
        return params
    params['city'] = city
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{url}/alerts", params=params) as resp:
            return await resp.json()

@router.get("/weather/air")
async def get_air(city: str):
    params = load_apikey()
    if params is RECORD_NOT_FOUND:
        return params
    params['city'] = city
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{url}/airquality", params=params) as resp:
            return await resp.json()