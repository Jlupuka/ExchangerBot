from aiogram import Router, Bot
from aiogram import F
from aiogram.types import CallbackQuery
from filters.filters import IsAdmin
from lexicon.lexicon import botMessages

from keyboard.keyboard_factory import Factories
from factories.factory import AdminCallbackFactory

router: Router = Router()


@router.callback_query(AdminCallbackFactory.filter(F.page == "information"), IsAdmin())
async def information_handler(
    callback: CallbackQuery, callback_data: AdminCallbackFactory, bot: Bot
) -> None:
    await callback.message.edit_text(
        text=botMessages["informationAdmin"].format(
            botName=(await bot.get_me()).username
        ),
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory, back=callback_data.back_page
        ),
    )
