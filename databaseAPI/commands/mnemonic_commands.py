from typing import Any, Sequence, Union

from sqlalchemy import select, Select, ChunkedIteratorResult
from sqlalchemy.orm import InstrumentedAttribute, joinedload

from services import logger
from sqlalchemy.exc import IntegrityError, NoResultFound
from databaseAPI.database import get_session
from databaseAPI.models.models import MnemonicWallets


class MnemonicAPI:
    @staticmethod
    async def add_mnemonic(**kwargs: dict[str:Any]) -> MnemonicWallets:
        async with get_session() as session:
            mnemonic_obj: MnemonicWallets = MnemonicWallets(**kwargs)
            session.add(mnemonic_obj)
            try:
                await session.flush()
                await session.commit()
                return mnemonic_obj
            except IntegrityError as IE:
                logger.error(f"Indentation error in function '{__name__}': {IE}")
                await session.rollback()

    @staticmethod
    async def select_mnemonic(
        *args: Union[MnemonicWallets, InstrumentedAttribute[MnemonicWallets]],
        **kwargs: dict[str:Any],
    ) -> Union[Sequence[MnemonicWallets], MnemonicWallets]:
        async with get_session() as session:
            sql: Select = (
                select(*args)
                .options(joinedload(MnemonicWallets.wallet))
                .where(
                    *[
                        getattr(MnemonicWallets, __key) == __value
                        for __key, __value in kwargs.items()
                    ]
                )
            )

            try:
                mnemonic_chunk: ChunkedIteratorResult = await session.execute(sql)
                result = (
                    mnemonic_chunk.all()
                    if len(args) > 1
                    else mnemonic_chunk.scalars().all()
                )
                return result
            except NoResultFound as NRF:
                logger.error(f"Indentation error in function '{__name__}': {NRF}")
                await session.rollback()
