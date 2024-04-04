from datetime import timedelta
from typing import Sequence, Any, Union, Type
from sqlalchemy import func, select, distinct, Select, RowMapping, Update, update, Row
from sqlalchemy.engine.result import ChunkedIteratorResult
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import joinedload

from databaseAPI.database import get_session
from databaseAPI.models import Wallets, Submissions, Users
from databaseAPI.models.models import Statuses
from services import logger


class SubmissionsAPI:
    @staticmethod
    async def add_application(**kwargs: dict[str:Any]) -> Submissions:
        """
        Adds  data to the mnemonics table
        :param kwargs: (dict[str:Any]) Information about mnemonics
        :return: MnemonicWallets
        """
        async with get_session() as session:
            submission_object: Submissions = Submissions(**kwargs)
            session.add(submission_object)
            try:
                await session.flush()
                await session.commit()
                return submission_object
            except IntegrityError as IE:
                logger.error(f"Indentation error in function '{__name__}': {IE}")
                await session.rollback()

    @staticmethod
    async def update_mission(
        submission_id: int, **kwargs: dict[str:Any]
    ) -> Submissions:
        """
        By the mission id, updates it with the passed parameters
        :param submission_id: (int) mission id
        :param kwargs: (dict[str:Any]) Mission Parameters
        :return: Submissions
        """
        async with get_session() as session:
            sql: Update = (
                update(Submissions)
                .where(Submissions.Id == submission_id)
                .values(**kwargs)
                .returning(Submissions)
            )
            try:
                submission: Submissions = (await session.scalars(sql)).one()
                await session.commit()
                return submission
            except IntegrityError as IE:
                logger.error(f"Indentation error in function '{__name__}': {IE}")
                await session.rollback()

    @staticmethod
    async def select_missions(
        pagination: bool,
        user_id: Union[int, None] = None,
        offset: int = 0,
        *args: Type[Union[Wallets, Users, Submissions]],
        **kwargs: dict[str:Any],
    ) -> Union[Sequence[Union[Row[Any], RowMapping, Any]], Submissions]:
        """
        Returns data on the specified parameters from the Submissions table
        :param pagination: (bool)
        :param user_id: (Union[int, None]) user id
        :param offset: (int) if pagination true
        :param args: (Type[Union[Wallets, Users, Submissions]])
        :param kwargs: (dict[str:Any]) Information about mission
        :return: Union[Sequence[Union[Row[Any], RowMapping, Any]], Submissions]
        """
        async with get_session() as session:
            sql: Select = (
                select(*args)
                .options(joinedload(Submissions.wallet))
                .options(joinedload(Submissions.user))
                .join(Wallets, Submissions.wallet)
                .join(Users, Submissions.user)
                .where(
                    *[
                        getattr(Submissions, __key) == __value
                        for __key, __value in kwargs.items()
                    ]
                )
            )
            if user_id:
                sql: Select = sql.where(Users.UserId == user_id)
            mission_chunk: ChunkedIteratorResult = await session.execute(
                sql.limit(8).offset(offset * 8) if pagination else sql
            )
            try:
                result = (
                    mission_chunk.all()
                    if len(args) > 1
                    else mission_chunk.scalars().all()
                )
                return result
            except NoResultFound as NRF:
                logger.error(f"Indentation error in function '{__name__}': {NRF}")
                await session.rollback()

    @staticmethod
    async def delete_mission_by_id(mission_id: int) -> None:
        """
        Deletes a mission by its ID
        :param mission_id: (int)
        :return:
        """
        async with get_session() as session:
            submission: Submissions = await session.get(Submissions, mission_id)
            try:
                await session.delete(submission)
                await session.commit()
                return None
            except IntegrityError as IE:
                logger.error(f"Indentation error in function '{__name__}': {IE}")
                await session.rollback()

    @staticmethod
    async def get_statistic_data() -> dict[str:Any]:
        """
        Returns statistics on the mission
        :return: dict[str:Any]
        """
        async with get_session() as session:
            now = func.now()
            queries = {
                "newUserToDay": select(func.count()).where(Users.created_at == now),
                "newUserToWeek": select(func.count()).where(
                    Users.created_at >= now - timedelta(weeks=1)
                ),
                "newUserToMonth": select(func.count()).where(
                    Users.created_at >= now - timedelta(days=30)
                ),
                "UserTotal": select(func.count(Users.Id)),
                "countExchangeUser": select(func.count(distinct(Submissions.UserId))),
                "exchangeToDay": select(func.count()).where(
                    Submissions.created_at >= now - timedelta(days=1),
                    Submissions.Status == Statuses.completed,
                ),
                "exchangeToWeek": select(func.count()).where(
                    Submissions.created_at >= now - timedelta(weeks=1),
                    Submissions.Status == Statuses.completed,
                ),
                "exchangeToMonth": select(func.count()).where(
                    Submissions.created_at >= now - timedelta(days=30),
                    Submissions.Status == Statuses.completed,
                ),
                "exchangeTotal": select(func.count()).where(
                    Submissions.Status == Statuses.completed
                ),
                "topWorker": select(Users.UserId)
                .join_from(Submissions, Submissions.admin)
                .filter(Submissions.AdminId is not None)
                .group_by(Users.UserId)
                .order_by(func.count().desc())
                .limit(1),
                "topExchangerUserID": select(Users.UserId)
                .join_from(Submissions, Submissions.user)
                .filter(Submissions.Status == Statuses.completed)
                .group_by(Users.UserId)
                .order_by(func.count().desc())
                .limit(1),
                "topTypeExchange": select(Submissions.TypeTrans)
                .group_by(Submissions.TypeTrans)
                .order_by(func.count().desc())
                .limit(1),
                "topTypeCurrency": select(Submissions.CurrencyTo)
                .group_by(Submissions.CurrencyTo)
                .order_by(func.count().desc())
                .limit(1),
            }
            results = dict()
            for key, query in queries.items():
                result: ChunkedIteratorResult = await session.execute(query)
                results[key] = result.scalar()
            results["topTypeExchange"] = (
                results["topTypeExchange"].value if results["topTypeExchange"] else None
            )
            return results
