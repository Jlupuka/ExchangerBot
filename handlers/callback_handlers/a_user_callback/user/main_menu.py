from typing import NoReturn

from aiogram import Router, F
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from factories.factory import UserCallbackFactory, MissionCallbackFactory
from keyboard.keyboard_factory import Factories
from lexicon.lexicon import botMessages, startCallbackUser

router: Router = Router()


@router.callback_query(
    or_f(
        MissionCallbackFactory.filter(F.page == "main"),
        UserCallbackFactory.filter(F.page == "main"),
    )
)
async def main_handler(
    callback: CallbackQuery, state: FSMContext, callback_data: UserCallbackFactory
) -> NoReturn:
    await state.clear()
    await callback.message.edit_text(
        text=botMessages["startMessageUser"],
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory,
            back_page=callback_data.page,
            sizes=(2, 1, 2),
            **startCallbackUser,
        ),
    )
