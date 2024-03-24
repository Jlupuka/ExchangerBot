from typing import NoReturn, Any

from aiogram import Router, Bot
from aiogram import F
from aiogram.types import CallbackQuery, user as user_aiogram

from databaseAPI.commands.submissions_commands import SubmissionsAPI
from filters.filters import IsAdmin
from lexicon.lexicon import botMessages

from keyboard.keyboard_factory import Factories
from factories.factory import AdminCallbackFactory
from services.userService import UserService

router: Router = Router()


@router.callback_query(AdminCallbackFactory.filter(F.page == "statistics"), IsAdmin())
async def statistics_handler(
    callback: CallbackQuery, callback_data: AdminCallbackFactory, bot: Bot
) -> NoReturn:
    data: dict[str:Any] = await SubmissionsAPI.get_statistic_data()
    gain_statistic: dict[str:Any] = await UserService.statistic_admin()
    result = {**data, **gain_statistic}
    bot_data: user_aiogram.User = await bot.get_me()
    await callback.message.edit_text(
        text=botMessages["statisticAdmin"].format(
            **result,
            botName=bot_data.username,
        ),
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory, back=callback_data.back_page
        ),
    )
