from typing import NoReturn

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from lexicon.lexicon import botMessages, backLexicon, getSum

from keyboard.keyboard_factory import Factories
from factories.factory import UserCallbackFactory

from services.cryptoService import CryptoCheck
from services.dataService import JsonService
from services.stateService import StateService
from states.states import FSMCryptoFiat, FSMCryptoCrypto

router: Router = Router()


@router.callback_query(
    UserCallbackFactory.filter(F.page == "minSum"),
    StateFilter(FSMCryptoFiat.get_sum, FSMCryptoCrypto.get_sum),
)
async def set_minimal_amount_CC_CF(
    callback: CallbackQuery, state: FSMContext
) -> NoReturn:
    state_data: dict[str:str] = await state.get_data()
    walletPercent = state_data["walletPercent"]
    if state_data["currency_to"] == "СПБ":
        state_data["currency_to"] = "RUB"
    commission = await JsonService.get_specific_data(name_data="commissionSum")
    commission_amount: float = await CryptoCheck.transaction_amount(
        amount=commission,
        currency_from="USD",
        currency_to=state_data["currency_to"],
        margins=1,
    )
    min_sum = await JsonService.get_specific_data(name_data="minSum")
    amount_to: float = await CryptoCheck.transaction_amount(
        amount=min_sum,
        currency_from="RUB",
        currency_to=state_data["currency_to"],
        margins=walletPercent,
    )
    amount_to -= commission_amount
    amount_from: float = await CryptoCheck.transaction_amount(
        amount=min_sum,
        currency_from="RUB",
        currency_to=state_data["typeCrypto"],
        margins=1,
    )
    await state.update_data(amount_to=amount_to, amount_from=amount_from)
    text = botMessages["checkTheCorrectTransaction"].format(
        name_net=state_data["currency_to"],
        address=state_data["user_requisites"],
        amount_from=amount_from,
        currency_from=state_data["typeCrypto"],
        currency_to=state_data["currency_to"],
        amount_to=amount_to,
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory,
            sizes=(2,),
            back="main",
            back_name=backLexicon["cancelLexicon"],
            **getSum,
        ),
    )
    await StateService.set_states(
        state_name="check_validate_sum", state_data=state_data, state=state
    )
