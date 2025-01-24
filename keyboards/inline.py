from aiogram.types import (

    ReplyKeyboardMarkup,

    KeyboardButton,

    InlineKeyboardButton,

    InlineKeyboardMarkup,

)

go_back_start = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад", callback_data="is_menu"),
        ],
    ],
    resize_keyboard=True
)