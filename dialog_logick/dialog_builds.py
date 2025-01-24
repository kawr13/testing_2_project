from typing import Optional, Callable, List, Type, Any, Union
from aiogram.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import F

from dialog_logick.dialog_base import DialogManager, DialogStep


class DialogBuilder:
    """Строитель для создания диалогов"""

    def __init__(self, manager: DialogManager, dialog_name: str, states_group: Type[StatesGroup]):
        self.manager = manager
        self.dialog_name = dialog_name
        self.states_group = states_group
        self.steps: List[DialogStep] = []

    def add_step(
            self,
            message: str,
            state: State,
            validator: Optional[Callable] = None,
            inline_keyboard: Optional[InlineKeyboardMarkup] = None,
            reply_keyboard: Optional[ReplyKeyboardMarkup] = None,
            pre_handlers: List[Callable] = None,
            post_handlers: List[Callable] = None,
            error_message: str = None,
            image_path: Optional[str] = None
    ) -> 'DialogBuilder':
        """Добавление шага в диалог"""
        step = DialogStep(
            message=message,
            state=state,
            validator=validator,
            inline_keyboard=inline_keyboard,
            reply_keyboard=reply_keyboard,
            pre_handlers=pre_handlers,
            post_handlers=post_handlers,
            error_message=error_message or "Некорректный ввод. Попробуйте еще раз.",
            image_path=image_path
        )
        self.steps.append(step)
        return self

    def set_final_handler(self, handler: Callable) -> 'DialogBuilder':
        """Установка обработчика завершения диалога"""
        self.manager.final_handlers[self.dialog_name] = handler
        return self

    def build(self) -> None:
        """Построение диалога и регистрация обработчиков"""
        self.manager.dialogs[self.dialog_name] = self.steps

        # Регистрируем обработчики для каждого шага
        for i, step in enumerate(self.steps):
            # Обработчик для текстовых сообщений
            @self.manager.router.message(step.state)
            async def process_message(message: Message, state: FSMContext, step_index: int = i):
                await self.manager.process_step(message, self.dialog_name, step_index, state)

            # Если есть inline_keyboard, регистрируем обработчик для callback
            if step.inline_keyboard:
                @self.manager.router.callback_query(step.state)
                async def process_callback(callback: CallbackQuery, state: FSMContext, step_index: int = i):
                    await self.manager.process_step(callback, self.dialog_name, step_index, state)
                    await callback.answer()

        # Регистрируем обработчики навигации
        @self.manager.router.callback_query(F.data == "nav_back")
        async def handle_back(callback: CallbackQuery, state: FSMContext):
            """Обработка нажатия кнопки 'Назад'"""
            context = self.manager.context_storage.get(callback.message.chat.id)
            if not context:
                print("Контекст не найден при обработке кнопки 'Назад'")
                await callback.message.answer("Ошибка: контекст не найден")
                return

            print(f"Обработка кнопки 'Назад'. Текущий контекст: {context}")
            print(f"История шагов: {context.history}")
            print(f"Текущий шаг: {context.current_step}")

            # Если мы на первом шаге (история пуста), возвращаемся в меню
            if not context.history:
                print("История пуста, возврат в меню")
                await callback.message.answer("Вы вернулись в главное меню")
                await state.clear()
                return

            # Получаем предыдущий шаг
            current_step = context.current_step
            prev_step = context.history[-1] if context.history else None

            if not prev_step:
                print("Предыдущий шаг не найден, возврат в меню")
                await callback.message.answer("Вы вернулись в главное меню")
                await state.clear()
                return

            print(f"Возврат с шага {current_step} на шаг {prev_step}")

            # Получаем предыдущий ответ пользователя
            prev_answer = context.get_answer(prev_step)
            print(f"Предыдущий ответ: {prev_answer}")

            # Устанавливаем предыдущий шаг как текущий
            context.current_step = prev_step
            # Удаляем последний шаг из истории
            context.history.pop()

            # Получаем обработчик для предыдущего шага
            step_handler = self.steps.get(prev_step)
            if not step_handler:
                print(f"Обработчик для шага {prev_step} не найден")
                await callback.message.answer("Ошибка: обработчик шага не найден")
                return

            # Отправляем сообщение с предыдущим ответом
            message = f"{step_handler.message}\n\nВаш предыдущий ответ: {prev_answer}" if prev_answer else step_handler.message
            await self.manager.send_message(
                message=callback.message,
                text=message,
                state=state,
                keyboard=step_handler.keyboard,
                edit=True
            )

        @self.manager.router.callback_query(F.data == "nav_skip")
        async def handle_skip(callback: CallbackQuery, state: FSMContext):
            current_state = await state.get_state()
            if not current_state:
                await callback.answer("Невозможно пропустить")
                return

            # Находим текущий шаг
            current_step_index = -1
            for i, step in enumerate(self.steps):
                if step.state.state == current_state:
                    current_step_index = i
                    break

            if current_step_index == -1 or current_step_index >= len(self.steps) - 1:
                await callback.answer("Невозможно пропустить")
                return

            # Проверяем, можно ли пропустить этот шаг
            if not step.inline_keyboard:  # Если нет inline_keyboard, значит шаг обязательный
                await callback.answer("Этот шаг нельзя пропустить")
                return

            # Помечаем шаг как пропущенный
            context = self.manager.context_storage.get(callback.from_user.id)
            if context:
                context.data[current_state] = "Не указано"

            # Переходим к следующему шагу
            next_step = self.steps[current_step_index + 1]
            await state.set_state(next_step.state)

            keyboard = next_step.inline_keyboard or next_step.reply_keyboard
            await self.manager.send_message(
                message=callback.message,
                text=next_step.message,
                state=state,
                image_path=next_step.image_path,
                keyboard=keyboard,
                edit=True
            )
            await callback.answer()
