from aiogram.filters.callback_data import CallbackData
from typing import Optional


class UserCallbackFactory(CallbackData, prefix='user'):
    page: Optional[str]
    back_page: Optional[str]
    mission_page: Optional[int] = 0


class AdminCallbackFactory(CallbackData, prefix='admin'):
    page: Optional[str]
    back_page: Optional[str]
    mission_page: Optional[int] = 0
