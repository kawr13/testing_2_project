import asyncio
import json
import os

import aiohttp
import httpx
from dotenv import load_dotenv
from icecream import ic

load_dotenv()


token_sandbox = os.getenv("IMEI_TOKEN_SANDBOX")
token_production = os.getenv("IMEI_TOKEN_PRODUCTION")


async def send_to_url(imei: str):
    url = f"https://api.imeicheck.net/v1/checks"
    headers = {
        'Authorization': 'Bearer ' + token_sandbox,
        'Accept-Language': 'en',
        'Content-Type': 'application/json'
    }
    ic(imei)
    body = json.dumps({
        "deviceId": imei,
        "serviceId": 12
    })
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=body) as response:
            response = await response.json()
    # async with httpx.AsyncClient() as client:
    #     response = await client.post(
    #         url,
    #         headers=headers,
    #         data=body
    #     )
        return response

