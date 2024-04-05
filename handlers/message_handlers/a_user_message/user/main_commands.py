from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from factories.factory import UserCallbackFactory

from keyboard.keyboard_factory import Factories

from lexicon.lexicon import botMessages, startCallbackUser


router: Router = Router()


@router.message(Command(commands=["start", "cancel", "help"]))
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text=botMessages["startMessageUser"],
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory, back_page="main", sizes=(2, 1, 2), **startCallbackUser
        ),
    )
