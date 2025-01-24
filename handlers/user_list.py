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
from models.model import User
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


class PaginateUsers:
    def __init__(self):
        self.page = None
        self.items_per_page = None
        self.resumes = None
        self.resum = None

    async def __fetch_products(self):
        offset = (self.page - 1) * self.items_per_page
        limit = offset + self.items_per_page
        return self.resumes[offset:limit]

    async def get_message(self) -> str:
        """Формирование сообщения для текущей страницы."""
        current_page_resumes = await self.__fetch_products()
        if not current_page_resumes:
            return "Пользователи не найдены."

        msg = '*Список пользователей*:\n\n'
        msg += ''.join([
            f'{i + 1}. {resume.tg_id}.\n Статус: {resume.is_active}\n\n'
            for i, resume in enumerate(current_page_resumes, start=(self.page - 1))
        ])
        ic(msg)
        log.info(msg)
        return msg


paginate_users = PaginateUsers()

async def add_user_handler(call: CallbackQuery, state: FSMContext, page: int = 1):
    items_per_page = 1
    dict_ = await state.get_data()
    users = await User.filter().all()
    ic(call.data)
    if '+' in call.data and len(call.data.split('+')) == 3:
        page = int(call.data.split('+')[2])
        ic(page)
        paginate_users.page = page
        paginate_users.items_per_page = items_per_page
    else:
        paginate_users.page = page
        paginate_users.items_per_page = items_per_page


    await state.update_data({'user': users})
    paginate_users.resumes = users

    users_list = paginate_users.resumes

    items = [
        {
            "text": f"Заблокировать/разблокировать {user.tg_id}",
            "callback": f"is_block+{user.tg_id}"
        } for user in users_list
    ]
    keyboards = await KeyboardBuilder(items_per_page=items_per_page).create_inline_keyboard(
        items,
        current_page=page,
        callback_cancel='is_menu',
        callback_pg_prefix='add_user',
        with_pagination=True
    )
    if len(items) == 0:
        items = [{"text": "Нет пользователей", "callback": None}]
    message = await paginate_users.get_message()
    await state.update_data({'pages': page})
    await send_message(call.message, message, state=state, image_path='user', edit=True, keyboars=keyboards)


async def block_handler(call: CallbackQuery, state: FSMContext):
    from utilities.bot_conf import bot
    dict_ = await state.get_data()
    page = dict_.get('pages')
    id = call.data.split('+')[1]
    user = await User.filter(tg_id=id).first()
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
        await bot.send_message(user.tg_id, 'Ваш аккаунт был активирован\n\nПовторно запустите бота')
    await user.save()
    await add_user_handler(call, state, page=page)