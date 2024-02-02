from aiogram.filters.state import State, StatesGroup


class FSMCardDetails(StatesGroup):
    requisites = State()
