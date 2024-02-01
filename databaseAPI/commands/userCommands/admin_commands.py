from services import logger

from user_commands import select_user

from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from databaseAPI.database import get_session
from databaseAPI.tables.usersTable import Users


async def check_admin(user_id: int) -> bool:
    """
    Checking the user for an admin
    :param user_id: int
    :return: bool
    """
    user: Users = await select_user(user_id=user_id)
    return user.Admin


async def make_admin(user_id: int) -> None:
    """
    Changes a user's privilege to administrator
    :param user_id: int
    :return: None
    """
    async with get_session() as session:
        sql = update(Users).where(
            Users.UserId == user_id
        ).values(
            Admin=True
        )
        try:
            await session.execute(sql)
            await session.commit()
            return None
        except IntegrityError as IE:
            logger.error(f"Indentation error in function '{__name__}': {IE}")
            session.rollback()
