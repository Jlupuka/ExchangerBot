from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from databaseAPI.commands.userCommands.user_commands import UserAPI
from databaseAPI.models import Users
from factories.factory import UserCallbackFactory
from lexicon.lexicon import errorLexicon, kycVerify
from keyboard.keyboard_factory import Factories


class DataBaseCheckUserMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        state: FSMContext = data["state"]
        user_obj: Users = await UserAPI.check_user(event.from_user.id)
        if "rub" in event.data and user_obj.KYC is False:
            return await event.message.edit_text(
                text=errorLexicon["errorKYC"],
                reply_markup=await Factories.create_fac_menu(
                    UserCallbackFactory, **kycVerify
                ),
            )
        data["user"] = user_obj
        await state.update_data(userIsAdmin=user_obj.IsAdmin)
        return await handler(event, data)
