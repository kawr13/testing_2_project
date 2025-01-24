import os
import re
from typing import List, Optional

import asyncio

from aiogram import Dispatcher, Router
from aiogram.filters import CommandStart
from fastapi import APIRouter, Request
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, Update, CallbackQuery, InlineKeyboardButton, URLInputFile
from icecream import ic

from forms.forms import CheckImei
from keyboards.inline import go_back_start
from models.db_utilit import is_active, is_admin
from router.auth import create_token
from utilities.actions import callback_handler, actions
from utilities.check_imei import send_to_url
from utilities.icream import log
# from keyboards.inline import
# from models.model import
# from utilities.icream import log
from utilities.keyboard_build import KeyboardBuilder
from utilities.sender import send_message

router = Router()


async def add_token_handler(call: CallbackQuery, state: FSMContext):
    token = create_token(user_id=call.message.chat.id)
    msg = f'Ваш токен:\n\n```{token}```'
    msg += '\n\nДля проверки IMEI введите его в следующем формате:'
    text = f'''```
    \ncurl -X 'POST' \\
      'https://21b0c388-3764-498a-ac3e-81843b970913.tunnel4.com/api/check-imei/' \\
      -H 'accept: application/json' \\
      -H 'Authorization: Bearer {token}' \\
      -H 'Content-Type: application/json' \\
      -d '{{"imei": "Укажите ваш IMEI"}}'
    ```'''
    msg += text
    await send_message(call.message, msg, edit=False, image_path='token', state=state, keyboars=go_back_start)