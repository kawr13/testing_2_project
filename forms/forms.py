from aiogram.fsm.state import StatesGroup, State


class CheckImei(StatesGroup):
    start = State()
    end = State()