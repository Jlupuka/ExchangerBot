from typing import Any, Sequence

from databaseAPI.models.models import TypesWallet
from services import logger

from sqlalchemy import func, select, Select, Delete, delete, update, Update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.engine.result import ChunkedIteratorResult

from databaseAPI.database import get_session
from databaseAPI.models import Wallets


class WalletAPI:
    @staticmethod
    async def count_wallets() -> int:
        async with get_session() as session:
            sql: str = func.count(Wallets.Id)
            count_chunk: ChunkedIteratorResult = await session.execute(sql)
            count: int = count_chunk.scalar()
            return count

    @staticmethod
    async def get_all_name_net_wallets() -> set[str]:
        async with get_session() as session:
            sql: Select = select(Wallets.NameNet)
            nets_chunk: ChunkedIteratorResult = await session.execute(sql)
            return set(nets_chunk.scalars().all())

    @staticmethod
    async def add_wallet(
        name_net: str, address: str, type_wallet: TypesWallet
    ) -> None | bool:
        if not await WalletAPI.select_wallets(Address=address):
            async with get_session() as session:
                wallet_object: Wallets = Wallets(
                    NameNet=name_net, Address=address, typeWallet=type_wallet
                )
                session.add(wallet_object)
                try:
                    await session.commit()
                    return None
                except IntegrityError as IE:
                    logger.error(f"Indentation error in function '{__name__}': {IE}")
                    await session.rollback()
        return False

    @staticmethod
    async def select_wallets(
        *args: str,
        **kwargs: dict[str:Any],
    ) -> Sequence[Wallets]:
        async with get_session() as session:
            args = (
                [Wallets]
                if not args
                else [
                    getattr(Wallets, table) for table in args if hasattr(Wallets, table)
                ]
            )
            sql: Select = select(*args).where(
                *[
                    getattr(Wallets, __key) == __value
                    for __key, __value in kwargs.items()
                ]
            )
            try:
                wallets: ChunkedIteratorResult = await session.execute(sql)
                return wallets.scalars().all()
            except NoResultFound as NRF:
                logger.error(f"Indentation error in function '{__name__}': {NRF}")
                await session.rollback()

    @staticmethod
    async def delete_wallet(wallet_id: int) -> None:
        async with get_session() as session:
            sql: Delete = delete(Wallets).where(Wallets.Id == wallet_id)
            try:
                await session.execute(sql)
                await session.commit()
                return None
            except IntegrityError as IE:
                logger.error(f"Indentation error in function '{__name__}': {IE}")
                await session.rollback()

    @staticmethod
    async def update_wallet(wallet_id: int, **kwargs) -> Wallets:
        async with get_session() as session:
            sql: Update = (
                update(Wallets)
                .where(Wallets.Id == wallet_id)
                .values(**kwargs)
                .returning(Wallets)
            )
            try:
                wallet: Wallets = await session.scalars(sql)
                await session.commit()
                return wallet
            except IntegrityError as IE:
                logger.error(f"Indentation error in function '{__name__}': {IE}")
                await session.rollback()

    @staticmethod
    async def get_all_name_net_by_type(type_wallet: str) -> set[str] | bool:
        async with get_session() as session:
            sql: Select = select(Wallets.NameNet).where(
                Wallets.typeWallet == type_wallet
            )
            wallet_chunk: ChunkedIteratorResult = await session.execute(sql)
            wallet_scalar: Sequence[Wallets] = wallet_chunk.scalars().all()
            try:
                return set(wallet_scalar) if wallet_scalar else False
            except NoResultFound as NRF:
                logger.error(f"Indentation error in function '{__name__}': {NRF}")
                await session.rollback()

    @staticmethod
    async def get_wallets_for_mission(
        name_net: str, work_type: bool = True
    ) -> Sequence[Wallets]:
        async with get_session() as session:
            sql: Select = select(Wallets).where(
                Wallets.NameNet == name_net, Wallets.Status == work_type
            )
            wallets_chunk: ChunkedIteratorResult = await session.execute(sql)
            wallets_scalar: Sequence[Wallets] = wallets_chunk.scalars().all()
            try:
                return wallets_scalar if wallets_scalar else False
            except NoResultFound as NRF:
                logger.error(f"Indentation error in function '{__name__}': {NRF}")
                await session.rollback()
