from aiogram.filters.state import State, StateType


class FSMCardDetails(StateType):
    requisites = State()
