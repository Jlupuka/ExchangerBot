from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from databaseAPI.commands.userCommands.user_commands import UserAPI
from databaseAPI.models import Users


class DataBaseCheckUserMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        user_obj: Users = await UserAPI.check_user(event.from_user.id)
        state: FSMContext = data["state"]
        await state.update_data(userIsAdmin=user_obj.IsAdmin)
        return await handler(event, data)
