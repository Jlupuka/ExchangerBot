from aiogram import Router
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from factories.factory import UserCallbackFactory
from filters.filters import IsCryptoAddress
from keyboard.keyboard_factory import Factories

from lexicon.lexicon import (
    botMessages,
    checkCorrectAddress,
    repeatAddress,
    errorLexicon,
    backLexicon,
)
from services.cardService import CardCheck
from services.stateService import StateService
from states.states import FSMFiatCrypto, FSMCryptoFiat, FSMCryptoCrypto

router: Router = Router()


@router.message(
    StateFilter(
        FSMFiatCrypto.requisites, FSMCryptoFiat.requisites, FSMCryptoCrypto.requisites
    ),
    IsCryptoAddress(),
)
async def new_mission(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    requisites = message.text
    if state_data["currency_to"] == "СПБ":
        requisites = await CardCheck.preprocess_phone(phone=requisites)
    await state.update_data(user_requisites=requisites)
    await StateService.set_states(
        state_name="check_validate", state_data=state_data, state=state
    )
    await message.answer(
        text=botMessages["checkCorrectAddress"].format(
            net=state_data["currency_to"].upper(), wallet_address=requisites
        ),
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory,
            back="main",
            back_name=backLexicon["cancelLexicon"],
            sizes=(2, 1),
            **checkCorrectAddress
        ),
    )


@router.message(
    StateFilter(
        FSMFiatCrypto.requisites, FSMCryptoFiat.requisites, FSMCryptoCrypto.requisites
    )
)
async def error_address(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    await StateService.set_states(
        state_name="check_validate", state_data=state_data, state=state
    )
    await message.answer(
        text=errorLexicon["errorAddress"].format(
            net=state_data["currency_to"], wallet_address=message.text
        ),
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory,
            back="main",
            back_name=backLexicon["cancelLexicon"],
            **repeatAddress
        ),
    )
