from typing import NoReturn

from aiogram import Router, F
from aiogram.types import CallbackQuery

from factories.factory import UserCallbackFactory
from keyboard.keyboard_factory import Factories
from lexicon.lexicon import botMessages
from services.userService import UserService

router: Router = Router()


@router.callback_query(UserCallbackFactory.filter(F.page == "statistics"))
async def statistics_handler(
    callback: CallbackQuery, callback_data: UserCallbackFactory
) -> NoReturn:
    await callback.message.edit_text(
        text=botMessages["statisticTextUser"].format(
            **await UserService.statistic_user(user_id=callback.from_user.id)
        ),
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory, back_page="main", back=callback_data.back_page
        ),
    )
