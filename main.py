import ipaddress
import logging

import uvicorn
from icecream import ic
from pydantic import BaseModel

from db_conf import init, close
from models.db_utilit import set_active
from utilities.check_imei import send_to_url
from utilities.configurate import settings
# from utilities.icream import log
from fastapi.staticfiles import StaticFiles
import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Any, Optional, List, Dict, Callable
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from aiogram import BaseMiddleware
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from fastapi import APIRouter, Request
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, Update

import sys
import os
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from dotenv import load_dotenv
from handlers import start

from dataclasses import dataclass, field
# from router.rout_fast import router as fast_router
from utilities.bot_conf import dp, bot
from handlers.start import router as st_rout
from handlers.as_token import router as as_token
from handlers.user_list import router as user_list
from router.auth import router as auth, verify_token, is_admin

load_dotenv()

logging.getLogger("uvicorn").setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)
BOT_TOKEN: Optional[str] = os.getenv("BOT_TOKEN")


async def lifespan(app: FastAPI) -> None:
    await init()
    dp.include_routers(st_rout, as_token, user_list,)
    dp.routers_initialized = True
    await bot.set_webhook(
        url=f'{settings.WEBHOOK_URL}{settings.WEBHOOK_PATH}',
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True
    )

    yield
    await close()

app = FastAPI(lifespan=lifespan)
app.include_router(auth)


TELEGRAM_IP_RANGES = [
    "149.154.160.0/20",
    "91.108.4.0/22"
]

async def is_telegram_ip(ip: str) -> bool:
    """Проверка, принадлежит ли IP Telegram"""
    ip_addr = ipaddress.ip_address(ip)
    for net in TELEGRAM_IP_RANGES:
        if ip_addr in ipaddress.ip_network(net):
            return True
    return False


@app.post('/webhook')
async def telegram_webhook(request: Request):
    ic(request.headers)
    client_ip = request.headers.get("x-real-ip") or request.client.host
    if not await is_telegram_ip(client_ip):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized: Request not from Telegram"
        )
    json_body = await request.json()
    update = Update.model_validate(json_body, context={'bot': bot})
    await dp.feed_update(bot, update)


async def verify_api_key(api_token: str) -> None:
    if api_token != BOT_TOKEN:
        logger.error('Не авторизованный запрос')
        raise HTTPException(status_code=403, detail='Не авторизованный запрос')

@app.on_event("startup")
async def startup():
    webhook_url = f'{settings.WEBHOOK_URL}{settings.WEBHOOK_PATH}'
    await bot.set_webhook(webhook_url)
    logger.info("База данных подключена")


# Модель для тела запроса
class IMEIRequest(BaseModel):
    imei: str


class UserTgId(BaseModel):
    tg_id: int
    is_active: bool


class UserTgIdOut(BaseModel):
    tg_id: int
    is_active: bool


@app.post('/api/check-imei/')
async def check_imei_api(data: IMEIRequest, user_id: int = Depends(verify_token)):
    response = await send_to_url(data.imei)
    return response


@app.on_event("shutdown")
async def shutdown() -> None:
    await bot.delete_webhook()


@app.post('/api/vite-list/')
async def vite_list(data : UserTgId, user_id: int = Depends(verify_token)):
    tg_id = data.tg_id
    is_active = data.is_active
    result = await set_active(tg_id=tg_id, is_activ=is_active)
    return UserTgIdOut(tg_id=tg_id, is_active=is_active)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)