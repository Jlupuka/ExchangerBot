from typing import Any, Sequence

from sqlalchemy import select, Select, Update, update

from services import logger

from sqlalchemy.exc import IntegrityError, NoResultFound

from databaseAPI.database import get_session
from databaseAPI.models.models import Users
from config.config import load_config, Config

config: Config = load_config()


class UserAPI:
    @staticmethod
    async def __add_user(user_id: int) -> Users:
        """
        Add a user to the database
        :param user_id:
        :return: None
        """
        async with get_session() as session:
            admin_flag = user_id in config.AdminId.ADMINID
            user_object: Users = Users(
                UserId=user_id, Admin=admin_flag, KYC=True if admin_flag else False
            )
            session.add(user_object)
            try:
                await session.commit()
                logger.info(f"Added user. user_id={user_id}")
                return user_object
            except IntegrityError as IE:
                logger.error(f"Indentation error in function '{__name__}': {IE}")
                await session.rollback()

    @staticmethod
    async def select_user(**kwargs: dict[str:Any]) -> Sequence[Users]:
        """
        Retrieve user data by user_id
        :param kwargs:
        :return: Users | None
        """
        async with get_session() as session:
            sql: Select = select(Users).where(
                *[getattr(Users, __key) == __value for __key, __value in kwargs.items()]
            )
            try:
                return (await session.execute(sql)).scalars().all()
            except NoResultFound as NRF:
                logger.error(f"Indentation error in function '{__name__}': {NRF}")
                await session.rollback()

    @staticmethod
    async def update_user(user_id: int, **kwargs: dict[str:Any]) -> Users:
        async with get_session() as session:
            sql: Update = (
                update(Users)
                .where(Users.UserId == user_id)
                .values(**kwargs)
                .returning(Users)
            )
            try:
                user: Users = (await session.scalars(sql)).one()
                await session.commit()
                return user
            except NoResultFound as NRF:
                logger.error(f"Indentation error in function '{__name__}': {NRF}")
                await session.rollback()

    @staticmethod
    async def check_user(user_id: int) -> Users:
        """
        Check, if there is no user - add to the database, otherwise - nothing
        :param user_id:
        :return: None
        """
        user: Sequence[Users] = await UserAPI.select_user(UserId=user_id)
        if not user:
            user: Users = await UserAPI.__add_user(user_id=user_id)
        return user[0]
