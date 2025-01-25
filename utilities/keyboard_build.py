from typing import List, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import math

from icecream import ic
from utilities.icream import logger

from typing import List, Optional, Dict, Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import math
import logging

logger = logging.getLogger(__name__)

from typing import List, Optional, Dict, Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import math
import logging

logger = logging.getLogger(__name__)


class KeyboardBuilder:
    def __init__(self, items_per_page: int = 10):
        self.items_per_page = items_per_page

    async def create_inline_keyboard(
            self,
            items: List[Dict[str, Any]],
            current_page: int = 1,
            with_pagination: bool = True,
            callback_pg_prefix: str = "item",
            row_width: int = 1,
            group_buttons: bool = False,
            callback_cancel: Optional[str] = None,
            callback_prod: Optional[str] = None  # Добавлен обратно для совместимости
    ) -> InlineKeyboardMarkup:
        """
        Создает инлайн клавиатуру с гибкой структурой кнопок.

        Args:
            items: Список словарей с описанием кнопок
            current_page: Текущая страница
            with_pagination: Включить пагинацию
            callback_pg_prefix: Префикс для callback пагинации
            row_width: Количество кнопок в ряду для обычного режима
            group_buttons: Режим группировки кнопок (если True, кнопки группируются для одной записи)
            callback_cancel: Callback для кнопки отмены
            callback_prod: Префикс для callback данных (для обратной совместимости)
        """
        keyboard = []

        if not items:
            return InlineKeyboardMarkup(inline_keyboard=[[]])

        total_pages = math.ceil(len(items) / self.items_per_page) if with_pagination else 1

        # Определяем текущие элементы для отображения
        if with_pagination:
            start_idx = (current_page - 1) * self.items_per_page
            end_idx = start_idx + self.items_per_page
            current_items = items[start_idx:end_idx]
        else:
            current_items = items

        # Создаем кнопки
        if group_buttons:
            # Режим группировки кнопок (несколько кнопок для одной записи)
            for item in current_items:
                row = []
                if "buttons" in item and isinstance(item["buttons"], list):
                    for btn in item["buttons"]:
                        if isinstance(btn, dict) and "text" in btn and "callback" in btn:
                            callback_data = f"{callback_prod}{btn['callback']}" if callback_prod else btn["callback"]
                            button = InlineKeyboardButton(
                                text=btn["text"],
                                callback_data=callback_data
                            )
                            row.append(button)
                if row:
                    keyboard.append(row)
        else:
            # Обычный режим (по row_width кнопок в ряду)
            for i in range(0, len(current_items), row_width):
                row = []
                ic(current_items)
                for item in current_items[i:i + row_width]:
                    if isinstance(item, dict) and "text" in item and "callback" in item:
                        callback_data = f"{callback_prod}{item['callback']}" if callback_prod else item["callback"]
                        button = InlineKeyboardButton(
                            text=item["text"],
                            callback_data=callback_data
                        )
                        ic(button)
                        row.append(button)
                if row:
                    keyboard.append(row)

        # Добавляем пагинацию
        if with_pagination and total_pages > 1:
            navigation_row = []
            if current_page > 1:
                navigation_row.append(
                    InlineKeyboardButton(
                        text="⬅️",
                        callback_data=f"{callback_pg_prefix}+page+{current_page - 1}"
                    )
                )
            navigation_row.append(
                InlineKeyboardButton(
                    text=f"{current_page}/{total_pages}",
                    callback_data="current_page"
                )
            )
            if current_page < total_pages:
                navigation_row.append(
                    InlineKeyboardButton(
                        text="➡️",
                        callback_data=f"{callback_pg_prefix}+page+{current_page + 1}"
                    )
                )
            keyboard.append(navigation_row)

        # Добавляем кнопку отмены
        if callback_cancel:
            keyboard.append([
                InlineKeyboardButton(
                    text="🔙",
                    callback_data=callback_cancel
                )
            ])

        return InlineKeyboardMarkup(inline_keyboard=keyboard)
