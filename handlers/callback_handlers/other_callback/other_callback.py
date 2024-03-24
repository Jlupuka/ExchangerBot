from typing import Union
from aiogram import Router
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from factories.factory import (
    UserCallbackFactory,
    AdminCallbackFactory,
    MissionCallbackFactory,
)
from services import logger

router: Router = Router()


@router.callback_query(
    or_f(
        UserCallbackFactory.filter(),
        AdminCallbackFactory.filter(),
        MissionCallbackFactory.filter(),
    )
)
async def send_any_callback(
    callback: CallbackQuery,
    callback_data: Union[
        UserCallbackFactory | AdminCallbackFactory | MissionCallbackFactory
    ],
    state: FSMContext,
) -> None:
    await callback.answer("Что?")
    logger.info(
        "userID=%s, callbackData=(%s), state=%s",
        callback.from_user.id,
        callback_data,
        await state.get_state(),
    )
