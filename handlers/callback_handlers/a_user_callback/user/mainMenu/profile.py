from typing import NoReturn

from aiogram import Router, F
from aiogram.types import CallbackQuery

from databaseAPI.tables import Users
from factories.factory import UserCallbackFactory
from keyboard.keyboard_factory import Factories
from lexicon.lexicon import botMessages, kycVerificationLexicon, profileUser
from services.userService import UserService

router: Router = Router()


@router.callback_query(UserCallbackFactory.filter(F.page == "profile"))
async def profile_handler(
    callback: CallbackQuery, callback_data: UserCallbackFactory, user: Users
) -> NoReturn:
    await callback.message.edit_text(
        text=botMessages["profileTextUser"].format(
            userID=user.UserId,
            KYCStatus=kycVerificationLexicon[user.KYC],
            dateRegistration=await UserService.format_date_string(
                date_string=str(user.DateTime)
            ),
        ),
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory,
            back_page=callback_data.page,
            back="main",
            sizes=(2,),
            **profileUser,
        ),
    )
