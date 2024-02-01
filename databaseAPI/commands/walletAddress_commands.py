from services import logger

from sqlalchemy import update, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine.result import ChunkedIteratorResult

from databaseAPI.database import get_session
from databaseAPI.tables.submissionsTable import Submissions


async def add_application(user_id: int,
                          address_id: int,
                          amount: int,
                          typetrans: str,
                          address_user: str) -> None:
    async with get_session() as session:
        submission_object: Submissions = Submissions(
            UserId=user_id,
            AddressId=address_id,
            Amount=amount,
            TypeTrans=typetrans,
            AddressUser=address_user
        )
        session.add(submission_object)
        try:
            await session.commit()
            return None
        except IntegrityError as IE:
            logger.error(f"Indentation error in function '{__name__}': {IE}")
            await session.rollback()


async def get_all_missons_wait(status: str = 'WAIT', offset: int = 0) -> list[Submissions]:
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