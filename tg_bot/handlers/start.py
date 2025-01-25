import os
import re
from typing import List, Optional

import asyncio

from aiogram import Dispatcher, Router
from aiogram.filters import CommandStart
from dotenv import load_dotenv
from fastapi import APIRouter, Request
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, Update, CallbackQuery, InlineKeyboardButton, URLInputFile
from icecream import ic
from models.model import User


from models.db_utilit import is_active, is_admin, get_user, get_admins
from utilities.actions import callback_handler, actions
from utilities.icream import log
# from keyboards.inline import
# from models.model import
# from utilities.icream import log
from utilities.keyboard_build import KeyboardBuilder
from utilities.sender import send_message

router = Router()
load_dotenv()

async def delleting_msg(meseges: Optional[Message|CallbackQuery]):
    msg = meseges if isinstance(meseges, Message) else meseges.message
    try:
        if msg.text == '/start':
            return
        await msg.delete()
    except:
        pass


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    from tg_bot.bot_conf import bot
    await delleting_msg(message)
    ic(await get_user(message.chat.id))
    if not await is_active(message):
        admins = await get_admins()
        for admin in admins:
            await bot.send_message(admin.tg_id, f'Запрос на активацию аккаунта {message.chat.id}')
        await send_message(message, f"*Ваш аккаунт не активен.*\n\n Запрос на доступ отправлен администратору\n\nСсылка на API {os.getenv('WEBHOOK_URL')}", image_path='no_auth', edit=True, state=state)
        return
    keyboard = KeyboardBuilder(items_per_page=1)
    items = [
        {
            "text": "Проверить товар по артикулу",
            "callback": "check_articul"
        },
        {
            "text": "Получить токен!",
            "callback": "add_token"
        },
    ]
    kb_start = await keyboard.create_inline_keyboard(
        items,
        current_page=1,  # Используем текущую страницу
        group_buttons=False,
        with_pagination=False,
    )
    if await is_admin(message):
        kb = InlineKeyboardButton(text='Активация пользователя', callback_data='add_user')
        kb_start.inline_keyboard.append([kb])
    await send_message(message, (f"*Привет!*\n👋 Я бот для получения информации о товаре на складах WB."
                                f" 🔍.\n\nСсылка на API {os.getenv('WEBHOOK_URL')}/docs\n"
                                f"Для продолжения нажми кнопку ниже 👇\n⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓"),
                       image_path='imei', edit=True, state=state, keyboars=kb_start)


@router.callback_query()
async def filter_handler(call: CallbackQuery, state: FSMContext):
    ic(call.data)
    dict_ = await state.get_data()
    data = callback_handler.handle(call.data)
    ic(data)
    if data in actions.keys():
        log.info(data)
        if data == 'is_menu':
            msg_1 = dict_.get('msg_1')
            await state.clear()
            await state.set_data({'msg_1': msg_1})
            await actions[data](call.message, state)
            return
        await actions[data](call, state)
        return




