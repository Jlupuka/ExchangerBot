from typing import NoReturn

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery

from factories.factory import UserCallbackFactory
from keyboard.keyboard_factory import Factories
from lexicon.lexicon import botMessages, backLexicon

router: Router = Router()


@router.callback_query(UserCallbackFactory.filter(F.page == "info"))
async def info_handler(
    callback: CallbackQuery, callback_data: UserCallbackFactory, bot: Bot
) -> NoReturn:
    await callback.message.edit_text(
        text=botMessages["informationUser"].format(
            botName=(await bot.get_me()).username
        ),
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory,
            back=callback_data.back_page,
            back_name=backLexicon["backMainMenu"],
        ),
    )
