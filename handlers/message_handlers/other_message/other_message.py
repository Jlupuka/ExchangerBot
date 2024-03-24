from aiogram import Router
from aiogram.types import Message

from lexicon.lexicon import botMessages
from services import logger

router = Router()


@router.message()
async def send_any_message(message: Message) -> None:
    await message.delete()
    await message.answer(text=botMessages["anyMessage"])
    logger.info("userID=%s, messageText=(%s)", message.from_user.id, message.text)
