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


async def create_base():
    async with engine.begin() as connection:
        logger.debug('Создаем таблицы в Базе Данных')
        await connection.run_sync(Base.metadata.create_all)
        logger.info('Успешно создали таблицы для Базы Данных')


@asynccontextmanager
async def get_session():
    try:
        async with sessionmaker(engine, class_=AsyncSession)() as session:
            yield session
    except Exception as ex:
        await session.rollback()
        logger.error(f'Ошибка! {ex}')
        raise
    finally:
        logger.debug('Закрыли запрос!')
        await session.close()
