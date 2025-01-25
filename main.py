import ipaddress
import logging

import uvicorn
from icecream import ic
from pydantic import BaseModel

from models.db_utilit import set_active
from utilities.configurate import settings
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
from tg_bot.handlers import start
from contextlib import asynccontextmanager

from dataclasses import dataclass, field
from backend.router.user_list import router as usr_lst
from backend.router.wb_api import router as wb_api
from tg_bot.bot_conf import dp, bot
from tg_bot.handlers.start import router as st_rout
from tg_bot.handlers.as_token import router as as_token
from tg_bot.handlers.user_list import router as user_list
from tg_bot.handlers.wb_pars import router as wb_pars
from backend.router.auth import router as auth, verify_token, is_admin
from db_conf import engine, Base
from utilities.shedule_process import scheduler

load_dotenv()

logging.getLogger("uvicorn").setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)
BOT_TOKEN: Optional[str] = os.getenv("BOT_TOKEN")


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    scheduler.start()
    async with engine.begin() as conn:
        # Создание всех таблиц
        await conn.run_sync(Base.metadata.create_all)

    dp.include_routers(st_rout, as_token, user_list, wb_pars)
    dp.routers_initialized = True
    await bot.set_webhook(
        url=f'{settings.WEBHOOK_URL}{settings.WEBHOOK_PATH}',
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True
    )

    yield
    scheduler.shutdown()
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(auth)
app.include_router(usr_lst)
app.include_router(wb_api)


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


@app.on_event("startup")
async def startup():
    webhook_url = f'{settings.WEBHOOK_URL}{settings.WEBHOOK_PATH}'
    await bot.set_webhook(webhook_url)
    logger.info("База данных подключена")


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


@app.on_event("shutdown")
async def shutdown() -> None:
    await bot.delete_webhook()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)