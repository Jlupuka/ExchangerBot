from aiogram.filters import BaseFilter
from aiogram.types import Message

from databaseAPI.commands.userCommands.admin_commands import check_admin


class IsAdmin(BaseFilter):
    """
    A filter that will check if the user is an administrator or not
    """

    async def __call__(self, message: Message) -> bool:
        """
        A filter that will check if the user is an administrator or not
        :param message: aiogram.filters.Message
        :return: bool
        """
        return await check_admin(user_id=message.from_user.id)
