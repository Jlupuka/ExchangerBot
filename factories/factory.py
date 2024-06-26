from aiogram.filters.callback_data import CallbackData
from typing import Optional, Union


class UserCallbackFactory(CallbackData, prefix="user"):
    page: str
    back_page: Optional[str]
    mission_page: Optional[int] = 0


class AdminCallbackFactory(CallbackData, prefix="admin"):
    page: str
    back_page: Optional[str]
    mission_page: Optional[int] = 0


class MissionCallbackFactory(CallbackData, prefix="mission"):
    mission_id: int
    page: Union[str, int]
    back_page: Optional[Union[str, int]]


class KYCCallbackFactory(CallbackData, prefix="KYC"):
    user_id: int
    verif_number: int
    page: Optional[str]
