from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery

from databaseAPI.commands.userCommands.user_commands import UserAPI
from databaseAPI.tables import Users
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
            data: Dict[str, Any]
    ) -> Any:
        user_obj: Users = await UserAPI.check_user(event.from_user.id)
        if 'rub' in event.data and user_obj.KYC is False:
            return await event.message.edit_text(text=errorLexicon['errorKYC'],
                                                 reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                                                              **kycVerify))

        return await handler(event, data)
