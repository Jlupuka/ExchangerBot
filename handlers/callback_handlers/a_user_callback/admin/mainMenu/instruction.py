from typing import NoReturn

from aiogram import Router
from aiogram import F
from aiogram.types import CallbackQuery
from filters.filters import IsAdmin
from lexicon.lexicon import botMessages

from keyboard.keyboard_factory import Factories
from factories.factory import AdminCallbackFactory

router: Router = Router()


@router.callback_query(AdminCallbackFactory.filter(F.page == "instruction"), IsAdmin())
async def instruction_handler(
    callback: CallbackQuery, callback_data: AdminCallbackFactory
) -> NoReturn:
    await callback.message.edit_text(
        text=botMessages["instructionAdmin"],
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory, back=callback_data.back_page
        ),
    )
