import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.middlewares.request_logging import RequestLogging
from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram.enums.parse_mode import ParseMode
from aiogram.methods import GetUpdates

from databaseAPI.tables import *  # Для создания базы данных (да-да...)

from services.service import LoadService

from config.config import Config, load_config
from config.mainCommands import load_main_command

from databaseAPI.database import create_base

from services import logger


async def main() -> None:
    # Подгружаем конфиг
    config: Config = load_config()

    redis: Redis = Redis(host=config.Redis.HOST, port=config.Redis.PORT)

    storge: RedisStorage = RedisStorage(redis=redis)

    # Создаем объекты бота и диспетчера
    bot: Bot = Bot(token=config.TelegramBot.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp: Dispatcher = Dispatcher(storage=storge)

    # Создаем базу данных
    await create_base()

    # # Создаем копки menu
    await load_main_command(logger=logger, bot=bot)

    # Подключаем роутеры
    await LoadService.load_router(dp=dp)

    # Подключаем мидлвари
    await LoadService.load_middlewares(dp=dp)
    bot.session.middleware(RequestLogging(ignore_methods=[GetUpdates]))

    logger.info('Starting bot')

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
