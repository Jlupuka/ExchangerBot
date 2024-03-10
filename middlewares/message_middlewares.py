from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message

from databaseAPI.commands.userCommands.user_commands import UserAPI


class DataBaseCheckUserMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        await UserAPI.check_user(event.from_user.id)
        return await handler(event, data)
