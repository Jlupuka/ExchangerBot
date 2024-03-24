from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from factories.factory import AdminCallbackFactory
from filters.filters import IsAdmin
from keyboard.keyboard_factory import Factories

from lexicon.lexicon import botMessages, startCallbackAdmin

router: Router = Router()


@router.message(Command(commands=["start"]), IsAdmin())
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text=botMessages["startMessageAdmin"],
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory, sizes=(2, 2), back_page="main", **startCallbackAdmin
        ),
    )
