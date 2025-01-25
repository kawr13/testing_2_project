import logging
import os
from dataclasses import dataclass
from typing import Callable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import Update
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from aiogram import Bot, Dispatcher, types, F


load_dotenv()

logging.getLogger("aiogram").setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN")
dp: Dispatcher = Dispatcher()


bot: Bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))



