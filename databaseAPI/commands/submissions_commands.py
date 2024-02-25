from sqlalchemy import func, select, update
from sqlalchemy.engine.result import ChunkedIteratorResult
from sqlalchemy.exc import IntegrityError

from databaseAPI.database import get_session
from databaseAPI.tables.submissionsTable import Submissions
from databaseAPI.tables.usersTable import Users
from services import logger


async def select_count_user_missions(user_id: int) -> int:
    async with get_session() as session:
        sql: str = select(func.count(Submissions.Id)).join(Users).where(
            Users.UserId == user_id)
        count_chunk: ChunkedIteratorResult = await session.execute(sql)
        return count_chunk.scalar()


async def add_application(user_id: int,
                          address_id: int,
                          amount: int | float,
                          typeTrans: str,
                          address_user: str) -> Submissions:
    async with get_session() as session:
        submission_object: Submissions = Submissions(
            UserId=user_id,
            AddressId=address_id,
            Amount=amount,
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


async def get_all_missions_wait(status: str = 'WAIT', offset: int = 0) -> list[Submissions]:
    async with get_session() as session:
        if not offset:
            sql = select(Submissions).where(
                Submissions.Status == status
            )
        else:
            sql = select(Submissions).where(
                Submissions.Status == status
            ).limit(8).offset(offset * 8)
        result: ChunkedIteratorResult = await session.execute(sql)
        return result.scalars().all()


async def update_mission_accepted(submission_id: int, status: str) -> None:
    async with get_session() as session:
        sql = update(Submissions).where(
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
