from aiogram import Router, Bot
from aiogram import F
from aiogram.types import CallbackQuery

from databaseAPI.commands.userCommands.admin_commands import AdminAPI
from lexicon.lexicon import (
    botMessages,
    startCallbackAdmin,
    startCallbackUser,
)

from keyboard.keyboard_factory import Factories
from factories.factory import (
    AdminCallbackFactory,
    UserCallbackFactory,
    KYCCallbackFactory,
)

router: Router = Router()


@router.callback_query(KYCCallbackFactory.filter(F.page == "verifUser"))
async def approve_verif_user(
    callback: CallbackQuery, callback_data: KYCCallbackFactory, bot: Bot
) -> None:
    await AdminAPI.update_user(user_id=callback_data.user_id, KYC=True)
    await callback.message.answer(
        text=botMessages["approveVerif"].format(userID=callback_data.user_id),
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory, sizes=(2, 2), back_page="main", **startCallbackAdmin
        ),
    )
    await bot.send_message(
        chat_id=callback_data.user_id,
        text=botMessages["approveVerifUser"],
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory, sizes=(2, 1, 2), back_page="main", **startCallbackUser
        ),
    )
    await callback.message.delete()


@router.callback_query(KYCCallbackFactory.filter(F.page == "reject"))
async def reject_verif_user(
    callback: CallbackQuery, callback_data: KYCCallbackFactory, bot: Bot
) -> None:
    await callback.message.answer(
        text=botMessages["rejectVerifAdmin"].format(userID=callback_data.user_id),
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory, sizes=(2, 2), back_page="main", **startCallbackAdmin
        ),
    )
    await bot.send_message(
        chat_id=callback_data.user_id,
        text=botMessages["rejectVerifUser"],
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory, sizes=(2, 1, 2), back_page="main", **startCallbackUser
        ),
    )
    await callback.message.delete()
