from aiogram import Router
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from factories.factory import AdminCallbackFactory
from filters.filters import IsAdmin, IsDigit
from keyboard.keyboard_factory import Factories

from lexicon.lexicon import botMessages, errorLexicon, backLexicon, yesLexicon

from states.states import FSMEditMinSum


router: Router = Router()


@router.message(StateFilter(FSMEditMinSum.get_sum), IsDigit(), IsAdmin())
async def sure_update_min_sum(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMEditMinSum.check_sure)
    await state.update_data(minSum=float(message.text))
    await message.answer(
        text=botMessages["sureUpdateMinSum"].format(minSum=float(message.text)),
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory,
            back="settings",
            back_name=backLexicon["cancelLexicon"],
            **yesLexicon
        ),
    )


@router.message(StateFilter(FSMEditMinSum.get_sum), IsAdmin())
async def error_update_min_sum(message: Message) -> None:
    await message.answer(
        text=errorLexicon["IsDigitMinSum"].format(digit=message.text),
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory,
            back="settings",
            back_name=backLexicon["cancelLexicon"],
        ),
    )
