from aiogram import Router
from aiogram.types import Message

from lexicon.lexicon import botMessages

router = Router()


@router.message()
async def send_any_message(message: Message) -> None:
    await message.delete()
    await message.answer(
        text=botMessages['anyMessage']
    )
