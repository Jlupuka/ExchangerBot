from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from factories.factory import UserCallbackFactory
from keyboard.keyboard_factory import create_fac_menu

from lexicon.lexicon import botMessages, startCallbackUser

router = Router()


@router.message(Command(commands=['start']))
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text=botMessages['startMessageAdmin'],
        reply_markup=await create_fac_menu(UserCallbackFactory, back_page='main', sizes=(2, 1, 2), **startCallbackUser)
    )
