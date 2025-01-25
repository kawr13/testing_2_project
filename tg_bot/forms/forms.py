from aiogram.fsm.state import StatesGroup, State


class ArtikleWb(StatesGroup):
    start = State()
    end = State()