from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import declarative_base, sessionmaker

from contextlib import asynccontextmanager

from sqlalchemy.engine import URL

from config.config import Config, load_config

from services.settingsLogger import logger

config: Config = load_config()

Base = declarative_base()
url = URL.create(
    drivername='postgresql+asyncpg',
    username=config.DataBase.USER,
    password=config.DataBase.PASSWORD,
    host=config.DataBase.HOST,
    port=config.DataBase.PORT,
    database=config.DataBase.NAME
)

engine: AsyncEngine = create_async_engine(
    url,
    future=True,
)


async def create_base() -> None:
    """
    Creates tables in the database
    :return: None
    """
    async with engine.begin() as connection:
        logger.debug('Creating tables in the Database')
        await connection.run_sync(Base.metadata.create_all)
        logger.info('Successfully created tables for the Database')


@asynccontextmanager
async def get_session() -> None:
    """
    Provides a convenient way to create and manage database
    :return: None
    """
    try:
        async with sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)() as session:
            yield session
    except Exception as ex:
        await session.rollback()
        logger.error(f"Indentation error in function '{__name__}': {ex}")
        raise
    finally:
        logger.debug('Closed session!')
        await session.close()
