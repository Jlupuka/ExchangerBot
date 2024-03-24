from typing import NoReturn, Union

from aiogram import Router
from aiogram import F
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from filters.filters import IsAdmin
from lexicon.lexicon import (
    botMessages,
    startCallbackAdmin,
)

from keyboard.keyboard_factory import Factories
from factories.factory import (
    AdminCallbackFactory,
    MissionCallbackFactory,
)

router: Router = Router()


@router.callback_query(
    or_f(
        AdminCallbackFactory.filter(F.page == "main"),
        MissionCallbackFactory.filter(F.page == "main"),
    ),
    IsAdmin(),
)
async def start_handler_admin(
    callback: CallbackQuery,
    callback_data: Union[AdminCallbackFactory | MissionCallbackFactory],
    state: FSMContext,
) -> NoReturn:
    await state.clear()
    await callback.message.edit_text(
        text=botMessages["startMessageAdmin"],
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory,
            sizes=(2, 2),
            back_page=callback_data.page,
            **startCallbackAdmin,
        ),
    )
