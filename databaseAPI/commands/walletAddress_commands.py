from services import logger

from sqlalchemy import func, select, delete, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.engine.result import ChunkedIteratorResult

from databaseAPI.database import get_session
from databaseAPI.tables.walletAddressTable import WalletAddress


async def count_wallets() -> int:
    async with get_session() as session:
        sql: str = func.count(WalletAddress.Id)
        count_chunk: ChunkedIteratorResult = await session.execute(sql)
        count: int = count if (count := count_chunk.scalar()) else 0
        logger.info(f'Number of wallets in the database: {count}')
        return count


async def get_all_name_net_wallets() -> set[str]:
    async with get_session() as session:
        sql: str = select(WalletAddress.NameNet)
        nets_chunk: ChunkedIteratorResult = await session.execute(sql)
        return set(nets_chunk.scalars().all())


async def add_wallet(name_net: str, address: str, type_wallet: str) -> None | bool:
    if not await get_wallets_data(address=address):
        async with get_session() as session:
            wallet_object: WalletAddress = WalletAddress(
                NameNet=name_net,
                Address=address,
                typeWallet=type_wallet
            )
            session.add(wallet_object)
            try:
                await session.commit()
                return None
            except IntegrityError as IE:
                logger.error(f"Indentation error in function '{__name__}': {IE}")
                await session.rollback()
    return False


async def get_wallets_data(name_net: str = None, address: str = None) -> list[tuple[int, str]]:
    async with get_session() as session:
        sql: str = select(WalletAddress).where(
            WalletAddress.NameNet == name_net
            if name_net
            else
            WalletAddress.Address == address
        )
        wallets_data: ChunkedIteratorResult = await session.execute(sql)
        return [(wallet.Id, wallet.Address) for wallet in wallets_data.scalars().all()]


async def delete_wallet(wallet_id: int) -> None:
    async with get_session() as session:
        sql: str = delete(WalletAddress).where(
            WalletAddress.Id == wallet_id
        )
        try:
            await session.execute(sql)
            await session.commit()
            return None
        except IntegrityError as IE:
            logger.error(f"Indentation error in function '{__name__}': {IE}")
            await session.rollback()


async def get_wallet_data(wallet_id: int, get_data: str = None) -> float | WalletAddress:
    async with get_session() as session:
        sql: str = select(WalletAddress).where(
            WalletAddress.Id == wallet_id
        )
        wallet_chunk: ChunkedIteratorResult = await session.execute(sql)
        wallet: WalletAddress = wallet_chunk.scalars().one()
        try:
            return getattr(wallet, get_data) if get_data else wallet
        except NoResultFound as NRF:
            logger.error(f"Indentation error in function '{__name__}': {NRF}")
            await session.rollback()


async def update_work_type_wallet(wallet_id: int, work_type: bool) -> bool:
    async with get_session() as session:
        sql: str = update(WalletAddress).where(
            WalletAddress.Id == wallet_id
        ).values(
            Status=work_type
        )
        try:
            await session.execute(sql)
            await session.commit()
            return work_type
        except IntegrityError as IE:
            logger.error(f"Indentation error in function '{__name__}': {IE}")
            await session.rollback()


async def update_percent(wallet_id: int, percent: float) -> None:
    async with get_session() as session:
        sql: str = update(WalletAddress).where(
            WalletAddress.Id == wallet_id
        ).values(
            Percent=percent
        )
        try:
            await session.execute(sql)
            await session.commit()
            return None
        except IntegrityError as IE:
            logger.error(f"Indentation error in function '{__name__}': {IE}")
            await session.rollback()
