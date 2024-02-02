from aiogram.filters.callback_data import CallbackData
from typing import Optional


class MainCallbackFactory(CallbackData, prefix='menu'):
    page: Optional[str]
    back_page: Optional[str]
    missons_page: Optional[int] = 0
