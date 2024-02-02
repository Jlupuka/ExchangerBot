from aiogram import Bot
from aiogram.types import BotCommand
from logging import Logger

from lexicon.lexicon import LexiconCommands


async def load_main_command(bot: Bot, logger: Logger) -> None:
    main_commands: list = [
        BotCommand(
            command=command,
            description=description
        )
        for command, description in LexiconCommands.items()
    ]
    await bot.set_my_commands(main_commands)
    logger.debug('Uploaded the main commands')
