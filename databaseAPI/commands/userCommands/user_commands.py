from services import logger

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.engine.result import ChunkedIteratorResult

from databaseAPI.database import get_session
from databaseAPI.tables.usersTable import Users
from config.config import load_config

config = load_config()


async def __add_user(user_id: int) -> Users | None:
    """
    Add a user to the database
    :param user_id:
    :return: None
    """
    async with get_session() as session:
        admin_flag = user_id in config.AdminId.ADMINID
        user_object: Users = Users(
            UserId=user_id,
            Admin=admin_flag
        )
        session.add(user_object)
        try:
            await session.commit()
            logger.info(f'Added user. user_id={user_id}')
            return user_object
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
        user_scalar: list = user_chunk.scalars().all()
        try:
            return user_scalar[0] if user_scalar else None
        except NoResultFound as NRF:
            logger.error(f"Indentation error in function '{__name__}': {NRF}")
            await session.rollback()


async def check_user(user_id: int) -> Users:
    """
    Check, if there is no user - add to the database, otherwise - nothing
    :param user_id:
    :return: None
    """
    user: Users | None = await select_user(user_id=user_id)
    if not user:
        user: Users | None = await __add_user(user_id=user_id)
    return user


async def select_all_users() -> list[Users] | None:
    """
    Select all users from the 'Users'-table.
    :return:  None
    """
    async with get_session() as session:
        sql = select(Users)
        result: ChunkedIteratorResult = await session.execute(sql)
        return result.scalars().all()
