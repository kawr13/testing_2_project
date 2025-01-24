from aiogram.fsm.context import FSMContext
from aiogram.types import Message, Update, CallbackQuery, FSInputFile, InputMediaPhoto, InlineKeyboardMarkup, \
    URLInputFile
from aiogram.enums import ParseMode
import asyncio

from icecream import ic

from utilities.actions import img_dict


async def delete_message(message: Message, timer: int = 5):
    if timer:
        await asyncio.sleep(timer)
        await message.delete()
        return
    await message.delete()


async def send_message(message: Message, text: str, image_path: str = None, edit: bool = False,
                       keyboars: InlineKeyboardMarkup = None, state: FSMContext = None):
    dict_ = await state.get_data() if state else {}

    async def state_set(msg: Message):
        try:
            await state.update_data({'msg_1': msg})
            return
        except:
            pass

    async def delleting_msg(msg: Message):
        try:
            await msg.delete()
        except:
            pass

    async def set_image(image_path: str):
        print(image_path)

        image_path = img_dict.get(image_path)
        # image = FSInputFile(image_path)
        image = URLInputFile(image_path)
        return image

    if image_path:
        image = await set_image(image_path)

        '''

        Если используется файл из папки, то вместо URLInputFile можно использовать FSInputFile
        image = FSInputFile(image_path)
        image = URLInputFile(image_path)
        '''

        if edit:
            media = InputMediaPhoto(media=image, caption=text)
            ic(dict_)
            if dict_.get('msg_1', None):
                try:
                    msg_1 = await dict_['msg_1'].edit_media(media, reply_markup=keyboars,
                                                            parse_mode='Markdown')
                    await state_set(msg_1)
                    return
                except Exception as e:
                    ic(f'Хуйбала сработала {e}')
                    await delleting_msg(dict_['msg_1'])
                    msg_1 = await message.answer_photo(photo=image, caption=text, reply_markup=keyboars,
                                                       parse_mode="Markdown")
                    await state_set(msg_1)
                    return
            try:
                msg_1 = await message.edit_media(media, reply_markup=keyboars,
                                                 parse_mode="Markdown")
                await state.set_data({'msg_1': msg_1})
                return
            except Exception as e:
                msg_1 = await message.answer_photo(photo=image, caption=text, reply_markup=keyboars,
                                                   parse_mode="Markdown")
                await state.set_data({'msg_1': msg_1})
                return
        if dict_.get('msg_1', None):
            await delleting_msg(dict_['msg_1'])
        await delleting_msg(message)
        msg_1 = await message.answer_photo(photo=image, caption=text, reply_markup=keyboars,
                                           parse_mode="Markdown")

        await state_set(msg_1)

    else:
        if edit:
            if dict_.get('msg_1', None):
                try:
                    msg = await dict_['msg_1'].edit_text(text, reply_markup=keyboars, parse_mode="Markdown")
                except:
                    await delleting_msg(dict_['msg_1'])
                    msg = await message.answer(text, reply_markup=keyboars, parse_mode="Markdown")
                await state_set(msg)
                return
            try:
                msg = await message.edit_text(text, reply_markup=keyboars, parse_mode="Markdown")
            except:
                if dict_.get('msg_1'):
                    await delleting_msg(dict_.get('msg_1'))
                msg = await message.answer(text, reply_markup=keyboars, parse_mode="Markdown")
            await state_set(msg)
            return
        await delleting_msg(message)
        msg = await message.answer(text, reply_markup=keyboars, parse_mode="Markdown")
        await state_set(msg)
