from services import logger

from sqlalchemy import func, select
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


async def get_all_wallets() -> list:
    async with get_session() as session:
        sql: str = select(WalletAddress.NameNet)
        nets_chunk: ChunkedIteratorResult = await session.execute(sql)
        return nets_chunk.scalars().all()


async def add_wallet(name_net: str, address: str) -> None:
    async with get_session() as session:
        wallet_object: WalletAddress = WalletAddress(
            NameNet=name_net,
            Address=address
        )
        session.add(wallet_object)
        try:
            await session.commit()
            return None
        except IntegrityError as IE:
            logger.error(f"Indentation error in function '{__name__}': {IE}")
            await session.rollback()
