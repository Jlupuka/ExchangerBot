from sqlalchemy.engine import ChunkedIteratorResult

from services import logger

from databaseAPI.commands.userCommands.user_commands import UserAPI

from sqlalchemy import update, select, func
from sqlalchemy.exc import IntegrityError, NoResultFound

from databaseAPI.database import get_session
from databaseAPI.tables.usersTable import Users


class AdminAPI:
    @staticmethod
    async def check_admin(user_id: int, check_admin: bool) -> bool:
        """
        Checking the user for an admin
        :param check_admin: bool
        :param user_id: int
        :return: bool
        """
        user: Users = await UserAPI.select_user(user_id=user_id)
        return user.Admin if check_admin is False else user.Admin and user.WorkType

    @staticmethod
    async def make_admin(user_id: int) -> None:
        """
        Changes a user's privilege to administrator
        :param user_id: int
        :return: None
        """
        async with get_session() as session:
            sql = update(Users).where(Users.UserId == user_id).values(Admin=True)
            try:
                await session.execute(sql)
                await session.commit()
                return None
            except IntegrityError as IE:
                logger.error(f"Indentation error in function '{__name__}': {IE}")
                session.rollback()

    @staticmethod
    async def get_workType(user_id: int) -> bool:
        async with get_session() as session:
            sql = select(Users).where(Users.UserId == user_id)
            user_chunk: ChunkedIteratorResult = await session.execute(sql)
            user_scalar: Users = user_chunk.scalars().one()
            try:
                return user_scalar.WorkType
            except NoResultFound as NRF:
                logger.error(f"Indentation error in function '{__name__}': {NRF}")
                await session.rollback()

    @staticmethod
    async def count_adminsWork() -> int:
        async with get_session() as session:
            sql: str = select(func.count(Users.Id)).where(
                Users.Admin is True, Users.WorkType is True
            )
            count_chunk: ChunkedIteratorResult = await session.execute(sql)
            count: int = count if (count := count_chunk.scalar()) else 0
            return count

    @staticmethod
    async def update_workType(user_id: int, work_type: bool) -> bool:
        async with get_session() as session:
            sql: str = (
                update(Users)
                .where(Users.UserId == user_id)
                .values(WorkType=not work_type)
            )
            try:
                await session.execute(sql)
                await session.commit()
                return not work_type
            except IntegrityError as IE:
                logger.error(f"Indentation error in function '{__name__}': {IE}")
                await session.rollback()

    @staticmethod
    async def select_all_admins() -> list[Users] | None:
        async with get_session() as session:
            sql: str = select(Users).where(Users.Admin is True, Users.WorkType is True)
            admins_chunk: ChunkedIteratorResult = await session.execute(sql)
            admins: list[Users] = admins_chunk.scalars().all()
            return admins if admins else None

    @staticmethod
    async def update_kyc(user_id: int, typeKYC: bool) -> None:
        async with get_session() as session:
            sql: str = update(Users).where(Users.UserId == user_id).values(KYC=typeKYC)
            try:
                await session.execute(sql)
                await session.commit()
                return
            except IntegrityError as IE:
                logger.error(f"Indentation error in function '{__name__}': {IE}")
                await session.rollback()
