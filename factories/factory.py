from aiogram.filters.callback_data import CallbackData
from typing import Optional


class UserCallbackFactory(CallbackData, prefix='user'):
    page: Optional[str]
    back_page: Optional[str]
    mission_page: Optional[int] = 0


class AdminCallbackFactory(CallbackData, prefix='admin'):
    page: Optional[str]
    back_page: Optional[str]


class MissionCallbackFactory(CallbackData, prefix='mission'):
    page: Optional[str]
    back_page: Optional[str | int]
    mission_id: Optional[int]
