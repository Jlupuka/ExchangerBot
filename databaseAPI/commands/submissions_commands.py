from sqlalchemy import func, select
from sqlalchemy.engine.result import ChunkedIteratorResult

from databaseAPI.database import get_session
from databaseAPI.tables.walletAddressTable import WalletAddress
from databaseAPI.tables.usersTable import Users


async def select_count_user_missions(user_id: int) -> int:
    async with get_session() as session:
        sql: str = select(func.count(WalletAddress.Id)).join(Users).where(
            Users.UserId == user_id)
        count_chunk: ChunkedIteratorResult = await session.execute(sql)
        return count_chunk.scalar()
