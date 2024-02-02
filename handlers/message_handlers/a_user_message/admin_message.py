from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from filters.filters import IsAdmin
from keyboard.keyboard_factory import create_fac_menu

from lexicon.lexicon import botMessages, startCallbackAdmin

router = Router()


@router.message(Command(commands=['start']), IsAdmin())
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text=botMessages['startMessageAdmin'],
        reply_markup=await create_fac_menu(sizes=(2, 2), **startCallbackAdmin)
    )
