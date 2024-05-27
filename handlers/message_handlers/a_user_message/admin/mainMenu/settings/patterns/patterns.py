from aiogram import Router
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from factories.factory import AdminCallbackFactory
from filters.filters import IsAdmin
from keyboard.keyboard_factory import Factories

from lexicon.lexicon import botMessages, backLexicon, yesLexicon

from states.states import FSMEditPatterns

router: Router = Router()


@router.message(StateFilter(FSMEditPatterns.get_token_name), IsAdmin())
async def get_token_name(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMEditPatterns.get_pattern)
    await state.update_data(token=message.text.lower())
    await message.answer(
        text=botMessages["getPattern"].format(token=message.text.lower()),
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory,
            back="settings",
            back_name=backLexicon["cancelLexicon"],
        ),
    )


@router.message(StateFilter(FSMEditPatterns.get_pattern), IsAdmin())
async def get_pattern(message: Message, state: FSMContext) -> None:
    await state.update_data(pattern=message.text)
    await state.set_state(FSMEditPatterns.check_sure)
    token = (await state.get_data())["token"]
    await message.answer(
        text=botMessages["sureAddedPattern"].format(token=token, pattern=message.text),
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory,
            back="settings",
            back_name=backLexicon["cancelLexicon"],
            **yesLexicon
        ),
    )
