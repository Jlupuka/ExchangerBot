from typing import Any, Sequence, Union

from sqlalchemy.orm import joinedload, InstrumentedAttribute

from databaseAPI.models.models import TypesWallet
from services import logger

from sqlalchemy import select, Select, Delete, delete, update, Update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.engine.result import ChunkedIteratorResult

from databaseAPI.database import get_session
from databaseAPI.models import Wallets


class WalletAPI:
    @staticmethod
    async def add_wallet(
        name_net: str, address: str, type_wallet: TypesWallet
    ) -> Union[Wallets, bool]:
        """
        Adds wallet data to the Wallets table
        :param name_net: (str)
        :param address: (str)
        :param type_wallet: (TypesWallet)
        :return: Union[Wallets, bool]
        """
        if not await WalletAPI.select_wallets(Address=address):
            async with get_session() as session:
                wallet_object: Wallets = Wallets(
                    NameNet=name_net, Address=address, typeWallet=type_wallet
                )
                session.add(wallet_object)
                try:
                    await session.flush()
                    await session.commit()
                    return wallet_object
                except IntegrityError as IE:
                    logger.error(f"Indentation error in function '{__name__}': {IE}")
                    await session.rollback()
        return False

    @staticmethod
    async def select_wallets(
        *args: (Union[Wallets, InstrumentedAttribute[Wallets]]),
        special_filter: tuple[bool] = None,
        mnemonic: bool = False,
        **kwargs: dict[str:Any],
    ) -> Union[Sequence[Wallets], Wallets]:
        """
        Returns data on the specified parameters from the Wallets table
        :param args: (Union[Wallets, InstrumentedAttribute[Wallets]])
        :param special_filter: (tuple[bool]) example - (Wallets.MnemonicId is not None,)
        :param mnemonic: (bool) Do I need to get mnemonic
        :param kwargs: (dict[str:Any]) Information about wallet
        :return:
        """
        async with get_session() as session:
            args = [Wallets] if not args else args
            sql: Select = select(*args).where(
                *[
                    getattr(Wallets, __key) == __value
                    for __key, __value in kwargs.items()
                ]
            )
            if mnemonic:
                sql: Select = sql.options(joinedload(Wallets.mnemonic))
            try:
                wallets: ChunkedIteratorResult = await session.execute(
                    sql.where(*special_filter) if special_filter else sql
                )
                return wallets.scalars().all()
            except NoResultFound as NRF:
                logger.error(f"Indentation error in function '{__name__}': {NRF}")
                await session.rollback()

    @staticmethod
    async def delete_wallet(wallet_id: int) -> None:
        """
        Deletes a wallet by its ID
        :param wallet_id: (int)
        :return:
        """
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
        """
        By the wallet id, updates it with the passed parameters
        :param wallet_id: (int) wallet id
        :param kwargs: (dict[str:Any]) Wallet Parameters
        :return: Wallets
        """
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
