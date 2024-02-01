from services import logger

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine.result import ChunkedIteratorResult

from databaseAPI.database import get_session
from databaseAPI.tables.usersTable import Users


async def __add_user(user_id: int) -> None:
    """
    Add a user to the database
    :param user_id:
    :return: None
    """
    async with get_session() as session:
        user_object: Users = Users(
            UserId=user_id
        )
        session.add(user_object)
        try:
            await session.commit()
            logger.info(f'Added user. user_id={user_id}')
            return None
        except IntegrityError as IE:
            logger.error(f"Indentation error in function '{__name__}': {IE}")
            await session.rollback()


async def select_user(user_id: int) -> Users | None:
    """
    Retrieve user data by user_id
    :param user_id:
    :return: Users | None
    """
    async with get_session() as session:
        sql = select(Users).where(
            Users.UserId == user_id
        )
        user_chunk: ChunkedIteratorResult = await session.execute(sql)
        return user_chunk.scalars().all()


async def check_user(user_id: int) -> None:
    """
    Check, if there is no user - add to the database, otherwise - nothing
    :param user_id:
    :return: None
    """
    if await select_user(user_id=user_id) is None:
        await __add_user(user_id=user_id)


async def select_all_users() -> list[Users] | None:
    """
    Select all users from the 'Users'-table.
    :return:  None
    """
    async with get_session() as session:
        sql = select(Users)
        result: ChunkedIteratorResult = await session.execute(sql)
        return result.scalars().all()
