from aiogram import Router
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from factories.factory import AdminCallbackFactory
from filters.filters import IsAdmin, IsDigit
from keyboard.keyboard_factory import Factories

from lexicon.lexicon import (
    botMessages,
    errorLexicon,
    repeatGetPercent,
    backLexicon,
    checkPercent,
)

from states.states import FSMPercentEdit

router: Router = Router()


@router.message(
    StateFilter(FSMPercentEdit.get_percent), IsDigit(check_percent=True), IsAdmin()
)
async def get_percent(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMPercentEdit.check_percent)
    await state.update_data(percent=float(message.text))
    await message.answer(
        text=botMessages["getPercent"].format(percent=message.text),
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory,
            back="addressEdit",
            back_name=backLexicon["cancelLexicon"],
            **checkPercent
        ),
    )


@router.message(StateFilter(FSMPercentEdit.get_percent), IsAdmin())
async def error_get_percent(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMPercentEdit.check_percent)
    await message.answer(
        text=errorLexicon["IsDigitPercent"].format(digit=message.text),
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory,
            sizes=(2,),
            back="addressEdit",
            back_name=backLexicon["cancelLexicon"],
            **repeatGetPercent
        ),
    )
