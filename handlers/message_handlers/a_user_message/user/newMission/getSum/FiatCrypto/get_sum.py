from aiogram import Router
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from factories.factory import UserCallbackFactory
from filters.filters import IsDigit
from keyboard.keyboard_factory import Factories

from lexicon.lexicon import botMessages, backLexicon, getSum

from services.cryptoService import CryptoCheck

from states.states import FSMFiatCrypto

router: Router = Router()


@router.message(StateFilter(FSMFiatCrypto.get_sum), IsDigit(check_min=True))
async def check_the_correct_transaction_FC(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMFiatCrypto.check_validate_sum)
    await state.update_data(amount_from=float(message.text))
    state_data: dict[str:str] = await state.get_data()
    walletPercent = state_data["walletPercent"]
    amount_to: float = await CryptoCheck.transaction_amount(
        amount=state_data["amount_from"],
        currency_from=state_data["currency_from"],
        currency_to=state_data["currency_to"],
        margins=walletPercent,
    )
    await state.update_data(amount_to=amount_to)
    text = botMessages["checkTheCorrectTransaction"].format(
        name_net=state_data["currency_to"],
        address=state_data["user_requisites"],
        amount_from=state_data["amount_from"],
        currency_from=state_data["currency_from"],
        currency_to=state_data["currency_to"],
        amount_to=amount_to,
    )
    await message.answer(
        text=text,
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory,
            sizes=(2,),
            back="main",
            back_name=backLexicon["cancelLexicon"],
            **getSum
        ),
    )
