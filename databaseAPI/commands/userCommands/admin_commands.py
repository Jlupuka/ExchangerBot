from services import logger
from typing import Sequence

from databaseAPI.commands.userCommands.user_commands import UserAPI

from sqlalchemy.exc import IntegrityError

from databaseAPI.database import get_session
from databaseAPI.models.models import Users


class AdminAPI(UserAPI):
    @staticmethod
    async def check_admin(user_id: int, check_admin: bool) -> bool:
        """
        Checking the user for an admin
        :param check_admin: bool
        :param user_id: int
        :return: bool
        """
        user: Users = (await UserAPI.select_user(UserId=user_id))[0]
        return user.Admin if check_admin is False else user.Admin and user.WorkType

    @staticmethod
    async def make_admin(user_id: int) -> Users:
        """
        Changes a user's privilege to administrator
        :param user_id: int
        :return: None
        """
        async with get_session() as session:
            try:
                return await UserAPI.update_user(user_id=user_id, Admin=True)
            except IntegrityError as IE:
                logger.error(f"Indentation error in function '{__name__}': {IE}")
                session.rollback()

    @staticmethod
    async def count_adminsWork() -> int:
        admins: list[Users] | int = await AdminAPI.select_work_admins()
        return len(admins) if isinstance(admins, list) else 0

    @staticmethod
    async def select_work_admins() -> list[Users] | int:
        admins: Sequence[Users] = await UserAPI.select_user(Admin=True, WorkType=True)
        return admins if admins else 0
