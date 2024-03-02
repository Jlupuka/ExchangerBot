from sqlalchemy import func, select, update, delete
from sqlalchemy.engine.result import ChunkedIteratorResult
from sqlalchemy.exc import IntegrityError

from databaseAPI.database import get_session
from databaseAPI.tables import WalletAddress
from databaseAPI.tables.submissionsTable import Submissions
from databaseAPI.tables.usersTable import Users
from services import logger


class SubmissionsAPI:
    @staticmethod
    async def select_count_user_missions(user_id: int) -> int:
        async with get_session() as session:
            sql: str = select(func.count(Submissions.Id)).join(Users).where(
                Users.UserId == user_id)
            count_chunk: ChunkedIteratorResult = await session.execute(sql)
            return count_chunk.scalar()

    @staticmethod
    async def add_application(user_id: int,
                              address_id: int,
                              amount_to: int | float,
                              amount_from: int | float,
                              currency_to: str,
                              typeTrans: str,
                              address_user: str) -> Submissions:
        async with get_session() as session:
            submission_object: Submissions = Submissions(
                UserId=user_id,
                AddressId=address_id,
                AmountTo=amount_to,
                AmountFrom=amount_from,
                CurrencyTo=currency_to,
                TypeTrans=typeTrans,
                AddressUser=address_user
            )
            session.add(submission_object)
            try:
                await session.commit()
                return submission_object
            except IntegrityError as IE:
                logger.error(f"Indentation error in function '{__name__}': {IE}")
                await session.rollback()

    @staticmethod
    async def get_count_missions_by_status(mission_status: str) -> int:
        async with get_session() as session:
            sql: str = select(func.count(Submissions.Id)).where(
                       Submissions.Status == mission_status)
            count_chunk: ChunkedIteratorResult = await session.execute(sql)
            return count_chunk.scalar()

    @staticmethod
    async def update_mission_status(submission_id: int, status: str) -> None:
        async with get_session() as session:
            sql: str = update(Submissions).where(
                Submissions.Id == submission_id
            ).values(
                Status=status
            )
            try:
                await session.execute(sql)
                await session.commit()
                return None
            except IntegrityError as IE:
                logger.error(f"Indentation error in function '{__name__}': {IE}")
                await session.rollback()

    @staticmethod
    async def get_mission_data(mission_id: int) -> tuple[Submissions, WalletAddress, Users]:
        async with get_session() as session:
            sql: str = select(Submissions, WalletAddress, Users).join(WalletAddress).join(Users).where(
                Submissions.Id == mission_id)
            mission_chunk: ChunkedIteratorResult = await session.execute(sql)
            mission, wallet, user = mission_chunk.fetchone()
            return mission, wallet, user

    @staticmethod
    async def get_missions_by_status(mission_status: str, offset: int = 0,
                                     pagination: bool = False) -> list[Submissions]:
        async with get_session() as session:
            if pagination:
                sql: str = select(Submissions).where(
                    Submissions.Status == mission_status).limit(8).offset(offset * 8)
            else:
                sql = select(Submissions).where(
                    Submissions.Status == mission_status)
            mission_chunk: ChunkedIteratorResult = await session.execute(sql)
            return mission_chunk.scalars().all()

    @staticmethod
    async def update_admin_id(submission_id: int, admin_id: int | None) -> None:
        async with get_session() as session:
            sql: str = update(Submissions).where(
                Submissions.Id == submission_id
            ).values(
                AdminId=admin_id
            )
            try:
                await session.execute(sql)
                await session.commit()
                return None
            except IntegrityError as IE:
                logger.error(f"Indentation error in function '{__name__}': {IE}")
                await session.rollback()

    @staticmethod
    async def delete_mission_by_id(mission_id: int) -> None:
        async with get_session() as session:
            sql: str = delete(Submissions).where(
                Submissions.Id == mission_id
            )
            try:
                await session.execute(sql)
                await session.commit()
                return None
            except IntegrityError as IE:
                logger.error(f"Indentation error in function '{__name__}': {IE}")
                await session.rollback()