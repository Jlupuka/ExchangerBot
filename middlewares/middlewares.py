from typing import Callable, Dict, Any, Awaitable

from services import logger

from aiogram import BaseMiddleware
from aiogram.types import Message

from databaseAPI.commands.userCommands.user_commands import check_user
from databaseAPI.commands.userCommands.admin_commands import make_admin, check_admin

from config.config import load_config, Config

config: Config = load_config()


class DataBaseCheckUserMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        await check_user(user_id := event.from_user.id)
        logger.info(f'User id={user_id}')
        if user_id in config.AdminId.ADMINID and not await check_admin(user_id=user_id):
            logger.debug(f'Gave a role user_id={user_id}')
            await make_admin(user_id=user_id)
        return await handler(event, data)
