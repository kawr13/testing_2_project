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

from tg_bot.forms.forms import ArtikleWb
from tg_bot.handlers.start import delleting_msg
from tg_bot.keyboards.inline import go_back_start
from models.db_utilit import is_active, is_admin, get_all_users, get_user, update_user
from models.model import User
from utilities.actions import callback_handler, actions
from utilities.icream import log
from utilities.keyboard_build import KeyboardBuilder
from utilities.sender import send_message
from wb_parsing import WBParser

router = Router()


async def is_valid_code(message: Message, state: FSMContext) -> bool:
    result = re.fullmatch(r"^\d+$", message.text)
    if result is None:
        msg = await message.answer('Неправильно введен код')
        await asyncio.sleep(5)
        await msg.delete()
        return False
    return True


async def check_articul_handler(call: CallbackQuery, state: FSMContext):
    await state.set_state(ArtikleWb.start)
    msg = 'Укажите ваш артикул'
    await send_message(call.message, msg, edit=False, image_path='wb', state=state, keyboars=go_back_start)


@router.message(ArtikleWb.start, is_valid_code)
async def cheak_articul_number(message: Message, state: FSMContext):
    text = message.text
    await delleting_msg(message)
    await state.set_state(ArtikleWb.end)
    data = await WBParser.parse_product(text)
    messages = 'Актуальные данные по товару:\n\n'
    messages += f'Артикул: {data.get("artikul")}\n\n'
    messages += f'Наименование: {data.get("name")}\n\n'
    messages += f'Цена: {data.get("price")}\n\n'
    messages += f'Рейтинг: {data.get("rating")}\n\n'
    messages += f'Общее количество по складам:\n\n{data.get("total_quantity")}\n\n'
    await send_message(message, messages, edit=False, image_path='wb', state=state, keyboars=go_back_start)