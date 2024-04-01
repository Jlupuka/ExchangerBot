from aiogram import Router
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from factories.factory import UserCallbackFactory
from filters.filters import IsDigit
from keyboard.keyboard_factory import Factories

from lexicon.lexicon import errorLexicon, backLexicon, repeatGetSum

from services.stateService import StateService
from states.states import FSMFiatCrypto, FSMCryptoFiat, FSMCryptoCrypto

router: Router = Router()


@router.message(
    StateFilter(FSMFiatCrypto.get_sum, FSMCryptoCrypto.get_sum, FSMCryptoFiat.get_sum),
    IsDigit(check_min=False),
)
async def failed_the_minimum_test(message: Message, state: FSMContext) -> None:
    state_data: dict[str:str] = await state.get_data()
    await message.answer(
        text=errorLexicon["getSum_minimal"].format(
            amount=message.text, currency_from=state_data["currency_from"]
        ),
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory,
            back="main",
            back_name=backLexicon["cancelLexicon"],
            **repeatGetSum
        ),
    )
    await StateService.set_states(
        state_name="check_validate_sum", state_data=state_data, state=state
    )


@router.message(StateFilter(FSMFiatCrypto.get_sum))
async def failed_the_digit_test(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMFiatCrypto.check_validate_sum)
    await message.answer(
        text=errorLexicon["IsDigit"].format(digit=message.text),
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory,
            back="main",
            back_name=backLexicon["cancelLexicon"],
            **repeatGetSum
        ),
    )
