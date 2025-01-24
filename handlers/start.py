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
from models.db_utilit import is_active, is_admin
from utilities.actions import callback_handler, actions
from utilities.check_imei import send_to_url
from utilities.icream import log
# from keyboards.inline import
# from models.model import
# from utilities.icream import log
from utilities.keyboard_build import KeyboardBuilder
from utilities.sender import send_message

router = Router()


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
    await delleting_msg(message)
    if not await is_active(message):
        await send_message(message, "*Ваш аккаунт не активен.*\n\n Запрос на доступ отправлен администратору", image_path='no_auth', edit=True, state=state)
        return
    keyboard = KeyboardBuilder(items_per_page=1)
    items = [
        {
            "text": "Проверить IMEI",
            "callback": "check_imei"
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
    await send_message(message, "*Привет!*\n👋 Я бот для проверки данных IMEI. 🔍.\nДля продолжения нажми кнопку ниже 👇\n⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓",
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


async def check_imei_handler(call: CallbackQuery, state: FSMContext, new_msg=True):
    await state.set_state(CheckImei.start)
    kb_build = KeyboardBuilder(items_per_page=1)
    items = [
        {
        },
    ]
    keyboard = await kb_build.create_inline_keyboard(
        items,
        callback_cancel='is_menu',
        group_buttons=False,
        with_pagination=False
    )
    await state.set_state(CheckImei.start)
    await send_message(call.message, 'Введите IMEI', state=state, edit=new_msg, keyboars=keyboard)


async def is_valid_imei(message: Message, state: FSMContext) -> bool:
    # Проверка формата
    if not re.match(r"^\d{15}$", message.text):

        msg = await message.answer("IMEI должен состоять из 15 цифр.")
        await state.update_data({'msg_1': msg})
        return False

    # Проверка контрольной суммы
    digits = list(map(int, message.text))
    total = 0
    for i in range(14):
        if i % 2 == 0:
            total += digits[i]
        else:
            doubled = digits[i] * 2
            total += doubled // 10 + doubled % 10

    check_digit = (100 - total) % 10
    if not digits[-1] == check_digit:

        msg = await message.answer("IMEI имеет неверную контрольную сумму.")
        await state.update_data({'msg_1': msg})
        return False
    return True


@router.message(CheckImei.start, is_valid_imei)
async def check_imei(message: Message, state: FSMContext):
    await delleting_msg(message)
    kb_build = KeyboardBuilder(items_per_page=1)
    items = [
        {
            "text": 'Проверить',
            "callback": "checking"
        },
        {
            "text": 'Ввести заново',
            "callback": "check_imei"
        }
    ]
    keyboard = await kb_build.create_inline_keyboard(
        items,
        callback_cancel='is_menu',
        group_buttons=False,
        with_pagination=False
    )
    await state.update_data({'imei': message.text})
    await send_message(message, f'Вы ввели IMEI:\n\n{message.text} подтверждаете?', state=state, edit=True, keyboars=keyboard)


async def checking_handler(call: CallbackQuery, state: FSMContext):
    dict_ = await state.get_data()
    imei = dict_.get('imei')
    ic(imei)
    # if not await is_valid_imei(call.message, state):
    #     return
    response = await send_to_url(imei)

    ic(response.get('properties').get('image'))
    msg = '*Информация о устройстве по IMEI:* \n\n'
    msg += f'Название: {response.get("properties").get("deviceName")}\n'
    msg += f'IMEI: {imei}\n'
    msg += f'meid: {response.get("properties").get("meid")}\n'
    msg += f'imei2: {response.get("properties").get("imei2")}\n'
    msg += f'serial: {response.get("properties").get("serial")}\n'
    msg += f'replaced: {response.get("properties").get("replaced")}\n'
    msg += f'technicalSupport: {response.get("properties").get("technicalSupport")}\n'
    msg += f'modelDesc: {response.get("properties").get("modelDesc")}\n'
    msg += f'refurbished: {response.get("properties").get("refurbished")}\n'
    msg += f'refurbished: {response.get("properties").get("purchaseCountry")}\n'
    msg += f'apple/region: {response.get("properties").get("apple/region")}\n'
    msg += f'apple/modelName: {response.get("properties").get("apple/modelName")}\n'
    msg += f'usaBlockStatus: {response.get("properties").get("usaBlockStatus")}\n'
    img = response.get("properties").get("image")
    if img:
        image = URLInputFile(img)
        await call.message.answer_photo(image, caption=msg)
        await check_imei_handler(call, state, new_msg=False)
        return
    await send_message(call.message, msg, image_path='imei', state=state)
    await check_imei_handler(call, state)