from services import logger

from sqlalchemy import func, select, delete
from sqlalchemy.exc import IntegrityError
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


async def get_all_wallets() -> set[str]:
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
