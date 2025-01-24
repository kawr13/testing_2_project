from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from aiogram import Router
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, URLInputFile, InlineKeyboardMarkup, \
    ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
import asyncio

from icecream import ic


@dataclass
class DialogStep:
    """Расширенный класс шага диалога"""
    message: str
    state: State
    validator: Optional[Callable] = None
    inline_keyboard: Optional[InlineKeyboardMarkup] = None
    reply_keyboard: Optional[ReplyKeyboardMarkup] = None
    pre_handlers: List[Callable] = field(default_factory=list)
    post_handlers: List[Callable] = field(default_factory=list)
    error_message: str = "Некорректный ввод. Попробуйте еще раз."
    image_path: Optional[str] = None

    def __post_init__(self):
        """Проверяем и инициализируем обработчики"""
        # Проверяем что pre_handlers и post_handlers это списки
        if self.pre_handlers and not isinstance(self.pre_handlers, list):
            self.pre_handlers = [self.pre_handlers]
        if self.post_handlers and not isinstance(self.post_handlers, list):
            self.post_handlers = [self.post_handlers]

        # Если обработчики не заданы, создаем пустые списки
        if self.pre_handlers is None:
            self.pre_handlers = []
        if self.post_handlers is None:
            self.post_handlers = []


class DialogManager:
    """Улучшенный менеджер диалогов"""

    def __init__(self, router: Router):
        self.router = router
        self.dialogs: Dict[str, List[DialogStep]] = {}
        self.final_handlers: Dict[str, Callable] = {}

    async def delete_message(self, message: Message, timer: int = None):
        """Удаление сообщения с опциональным таймером"""
        try:
            if timer:
                await asyncio.sleep(timer)
            await message.delete()
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

    async def send_message(
            self,
            message: Message,
            text: str,
            state: FSMContext,
            image_path: str = None,
            keyboard: Union[InlineKeyboardMarkup, ReplyKeyboardMarkup] = None,
            edit: bool = True
    ) -> Message:
        """Отправка сообщения с поддержкой редактирования и изображений"""
        try:
            # Получаем сохраненные данные
            state_data = await state.get_data()
            last_bot_message = state_data.get('last_bot_message')

            # Получаем ID чата
            chat_id = message.chat.id if isinstance(message, Message) else message.message.chat.id

            print(f"Отправка сообщения. Edit: {edit}")
            print(f"Last bot message from state: {last_bot_message}")

            # Если сообщение от пользователя, удаляем его
            if not message.from_user.is_bot:
                await self.delete_message(message)
            ic(state_data)
            new_message = None
            if image_path:
                from utilities.actions import img_dict as img_page
                img_url = img_page.get(image_path)
                image = URLInputFile(img_url)
                state_data = await state.get_data()
                if edit and (last_bot_message or state_data.get('msg_1')):
                    try:

                        target_message = last_bot_message or state_data.get('msg_1')
                        media = InputMediaPhoto(media=image, caption=text)
                        new_message = await target_message.edit_media(
                            media=media,
                            reply_markup=keyboard,
                        parse_mode = ParseMode.MARKDOWN
                        )
                        print("Сообщение успешно отредактировано (с фото)")
                    except Exception as e:
                        print(f"Ошибка при редактировании сообщения с фото: {e}")

                if not new_message:
                    new_message = await message.answer_photo(
                        photo=image,
                        caption=text,
                        reply_markup=keyboard,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    # Удаляем предыдущее сообщение
                    if last_bot_message:
                        await self.delete_message(last_bot_message)
                    if state_data.get('msg_1'):
                        await self.delete_message(state_data['msg_1'])
            else:
                if edit and (last_bot_message or state_data.get('last_message') or state_data.get('msg_1')):
                    try:
                        target_message = last_bot_message or state_data['last_message'] or state_data.get('msg_1')
                        new_message = await target_message.edit_text(
                            text=text,
                            reply_markup=keyboard,
                            parse_mode=ParseMode.MARKDOWN
                        )
                        print("Сообщение успешно отредактировано (без фото)")
                    except Exception as e:
                        print(f"Ошибка при редактировании сообщения: {e}")

                if not new_message:
                    new_message = await message.answer(
                        text=text,
                        reply_markup=keyboard,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    # Удаляем предыдущее сообщение
                    if last_bot_message:
                        await self.delete_message(last_bot_message)
                    elif state_data.get('last_message'):
                        await self.delete_message(state_data['last_message'])

            # Сохраняем сообщение в state
            if new_message:
                await state.update_data(last_bot_message=new_message)

            return new_message

        except Exception as e:
            print(f"Ошибка в send_message: {e}")
            # В случае ошибки пытаемся отправить новое сообщение
            try:
                if image_path:
                    from utilities.actions import img_dict as img_page
                    img_url = img_page.get(image_path)
                    image = URLInputFile(img_url)
                    new_message = await message.answer_photo(
                        photo=image,
                        caption=text,
                        reply_markup=keyboard,
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    new_message = await message.answer(
                        text=text,
                        reply_markup=keyboard,
                        parse_mode=ParseMode.MARKDOWN
                    )
                await state.update_data(last_bot_message=new_message)
                return new_message
            except Exception as e:
                print(f"Критическая ошибка в send_message: {e}")
                return None

    async def start_dialog(
            self,
            message: Message,
            dialog_name: str,
            state: FSMContext,
            initial_data: Dict[str, Any] = None
    ):
        """Начало нового диалога"""
        user_id = message.chat.id  # Используем ID чата вместо from_user.id

        # Инициализируем state с пустой историей и начальными данными
        await state.update_data({
            'history': [],
            'current_dialog': dialog_name,
            **(initial_data or {})
        })

        first_step = self.dialogs[dialog_name][0]
        await state.set_state(first_step.state)

        # Выполняем pre_handlers
        for handler in first_step.pre_handlers:
            await handler(message, state)

        # Отправляем сообщение с соответствующей клавиатурой
        keyboard = first_step.inline_keyboard or first_step.reply_keyboard
        last_message = await self.send_message(
            message=message,
            text=first_step.message,
            state=state,
            image_path=first_step.image_path,
            keyboard=keyboard,
            edit=True
        )

        # Обновляем last_message в state
        await state.update_data(last_message=last_message)

    async def back_to_previous_dialog(
            self,
            message: Message,
            state: FSMContext
    ):
        """Возврат к предыдущему диалогу с сохранением контекста"""
        state_data = await state.get_data()

        if not state_data or not state_data.get('last_message'):
            print(f"Нет последнего сообщения. State: {state_data}")
            await message.answer("Невозможно вернуться назад")
            return

        # Получаем предыдущий шаг
        prev_step = state_data.get('prev_step')

        # Получаем предыдущий ответ
        prev_answer = state_data.get(prev_step)

        # Удаляем текущий шаг из истории
        state_data['history'].pop()

        # Получаем обработчик для предыдущего шага
        dialog_name = state_data.get('current_dialog')
        if dialog_name not in self.dialogs:
            return

        dialog_steps = self.dialogs[dialog_name]
        current_step_index = next((i for i, step in enumerate(dialog_steps)
                                   if step.state.state == prev_step), None)

        if current_step_index is None:
            return

        dialog_step = dialog_steps[current_step_index]

        # Устанавливаем предыдущее состояние
        await state.set_state(dialog_step.state)

        # Отправляем сообщение с предыдущим ответом
        message = f"{dialog_step.message}\n\nВаш предыдущий ответ: {prev_answer}" if prev_answer else dialog_step.message
        await self.send_message(
            message=message,
            text=message,
            state=state,
            keyboard=dialog_step.inline_keyboard or dialog_step.reply_keyboard,
            edit=True
        )

    async def process_step(
            self,
            message: Union[Message, CallbackQuery],
            dialog_name: str,
            step_index: int,
            state: FSMContext
    ):
        """Обработка шага диалога с поддержкой различных типов ввода"""
        # Получаем user_id и контекст
        user_id = message.chat.id if isinstance(message, Message) else message.message.chat.id
        state_data = await state.get_data()

        # Инициализируем history если его нет
        if 'history' not in state_data:
            state_data['history'] = []
            await state.update_data(history=[])

        current_step = self.dialogs[dialog_name][step_index]
        msg = message if isinstance(message, Message) else message.message

        # Выполняем pre_handlers текущего шага
        if current_step.pre_handlers:
            print(f"Выполняем pre_handlers для шага {current_step.state.state}")
            for handler in current_step.pre_handlers:
                try:
                    await handler(msg, state)
                except Exception as e:
                    print(f"Ошибка в pre_handler: {e}")

        # Получаем введенные данные
        input_data = message.text if isinstance(message, Message) else message.data
        ic(input_data)
        # Валидация с трансформацией
        if current_step.validator:
            print(f"Выполняем validator для шага {current_step.state.state}")
            try:
                validation_result = await current_step.validator(input_data)
                if isinstance(validation_result, bool):
                    # Если validator вернул bool - это проверка
                    if not validation_result:
                        await self.send_message(
                            message=msg,
                            text=current_step.error_message,
                            state=state,
                            edit=True
                        )
                        return
                else:
                    # Если validator вернул не bool - это трансформация
                    input_data = validation_result
            except Exception as e:
                print(f"Ошибка в validator: {e}")
                await self.send_message(
                    message=msg,
                    text=current_step.error_message,
                    state=state,
                    edit=True
                )
                return

        # Сохраняем данные в state
        state_name = current_step.state.state
        await state.update_data(**{state_name: input_data})

        if state_name not in state_data.get('history', []):
            state_data['history'].append(state_name)

        print(f"Сохранены данные для состояния {state_name}: {input_data}")
        print(f"История шагов: {state_data.get('history')}")

        # Выполняем post_handlers текущего шага
        if current_step.post_handlers:
            print(f"Выполняем post_handlers для шага {current_step.state.state}")
            for handler in current_step.post_handlers:
                try:
                    await handler(msg, state)
                except Exception as e:
                    print(f"Ошибка в post_handler: {e}")

        # Переход к следующему шагу или завершение
        if step_index + 1 < len(self.dialogs[dialog_name]):
            next_step = self.dialogs[dialog_name][step_index + 1]
            await state.set_state(next_step.state)

            # Выполняем pre_handlers следующего шага
            if next_step.pre_handlers:
                print(f"Выполняем pre_handlers следующего шага {next_step.state.state}")
                for handler in next_step.pre_handlers:
                    try:
                        await handler(msg, state)
                    except Exception as e:
                        print(f"Ошибка в pre_handler следующего шага: {e}")

            keyboard = next_step.inline_keyboard or next_step.reply_keyboard
            await self.send_message(
                message=msg,
                text=next_step.message,
                state=state,
                image_path=next_step.image_path,
                keyboard=keyboard,
                edit=True
            )
        else:
            # Выполняем финальный обработчик
            if dialog_name in self.final_handlers:
                try:
                    await self.final_handlers[dialog_name](msg, state)
                except Exception as e:
                    print(f"Ошибка в final_handler: {e}")

            # Очистка клавиатуры
            await self.send_message(
                message=msg,
                text="Диалог завершен",
                state=state,
                keyboard=ReplyKeyboardRemove(),
                edit=True
            )

    async def handle_back(
            self,
            message: Message,
            state: FSMContext,
            img: str
    ) -> bool:
        """Обработка команды "назад" с возвратом к предыдущему шагу"""
        current_state = await state.get_state()
        if not current_state:
            return False

        state_data = await state.get_data()
        if not state_data or 'history' not in state_data or not state_data['history']:
            return False

        # Получаем предыдущий шаг
        prev_step = state_data['history'][-1]

        # Получаем предыдущий ответ
        prev_answer = state_data.get(prev_step)

        # Удаляем текущий шаг из истории
        state_data['history'].pop()

        # Получаем обработчик для предыдущего шага
        dialog_name = state_data.get('current_dialog')
        if dialog_name not in self.dialogs:
            return False

        dialog_steps = self.dialogs[dialog_name]
        current_step_index = next((i for i, step in enumerate(dialog_steps)
                                   if step.state.state == prev_step), None)

        if current_step_index is None:
            return False

        dialog_step = dialog_steps[current_step_index]

        # Устанавливаем предыдущее состояние
        await state.set_state(dialog_step.state)

        # Отправляем сообщение с предыдущим ответом
        messages = f"{dialog_step.message}\n\nВаш предыдущий ответ: {prev_answer}" if prev_answer else dialog_step.message
        await self.send_message(
            message=message,
            text=messages,
            state=state,
            keyboard=dialog_step.inline_keyboard or dialog_step.reply_keyboard,
            edit=True,
            image_path=img
        )

        return True

    async def handle_skip(
            self,
            message: Message,
            state: FSMContext,
            img: str
    ) -> bool:
        """Обработка команды "пропустить" с переходом к следующему шагу"""
        current_state = await state.get_state()
        if not current_state:
            return False

        state_data = await state.get_data()
        dialog_name = state_data.get('current_dialog')
        if not dialog_name or dialog_name not in self.dialogs:
            return False

        dialog_steps = self.dialogs[dialog_name]
        current_step_index = next((i for i, step in enumerate(dialog_steps)
                                   if step.state.state == current_state), None)

        if current_step_index is None or current_step_index + 1 >= len(dialog_steps):
            return False

        # Переход к следующему шагу
        next_step = dialog_steps[current_step_index + 1]
        await state.set_state(next_step.state)

        # Добавляем текущий шаг в историю
        if 'history' not in state_data:
            state_data['history'] = []
        state_data['history'].append(current_state)
        await state.update_data(history=state_data['history'])

        # Отправляем сообщение следующего шага
        await self.send_message(
            message=message,
            text=next_step.message,
            state=state,
            keyboard=next_step.inline_keyboard or next_step.reply_keyboard,
            edit=True,
            image_path=img
        )

        return True
