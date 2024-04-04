import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.middlewares.request_logging import RequestLogging
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.methods import GetUpdates
from redis.asyncio.client import Redis

from config.config import Config, load_config
from config.mainCommands import load_main_command
from databaseAPI.database import create_base
from databaseAPI.models import Submissions, Users, Wallets
from services import logger
from services.JsonService import JsonService
from services.service import LoadService


async def main() -> None:
    config: Config = load_config()

    redis: Redis = Redis(host=config.Redis.HOST, port=config.Redis.PORT)

    storge: RedisStorage = RedisStorage(redis=redis)

    bot_properties: DefaultBotProperties = DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )

    bot: Bot = Bot(token=config.TelegramBot.TOKEN, default=bot_properties)
    dp: Dispatcher = Dispatcher(storage=storge, redis=redis)

    await create_base()

    await JsonService.load_copy_json()

    await load_main_command(logger=logger, bot=bot)

    await LoadService.load_router(dp=dp)

    await LoadService.load_middlewares(dp=dp)
    bot.session.middleware(RequestLogging(ignore_methods=[GetUpdates]))

    logger.info("Starting bot")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
