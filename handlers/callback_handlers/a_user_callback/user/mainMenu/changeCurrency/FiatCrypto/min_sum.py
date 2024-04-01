from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from lexicon.lexicon import botMessages, backLexicon, getSum

from keyboard.keyboard_factory import Factories
from factories.factory import UserCallbackFactory

from services.cryptoService import CryptoCheck
from services.JsonService import JsonService
from states.states import FSMFiatCrypto

router: Router = Router()


@router.callback_query(
    UserCallbackFactory.filter(F.page == "minSum"), StateFilter(FSMFiatCrypto.get_sum)
)
async def set_minimal_amount_FC(callback: CallbackQuery, state: FSMContext) -> None:
    state_data: dict[str:str] = await state.get_data()
    minimal_amount = await JsonService.get_specific_data(name_data="minSum")
    if state_data["currency_from"] != "RUB":
        minimal_amount = await CryptoCheck.minimal_summa(
            minSum=minimal_amount,
            currency_to=state_data["currency_to"],
            currency_from=state_data["currency_from"],
        )
    await state.update_data(amount_from=minimal_amount)
    walletPercent = state_data["walletPercent"]
    commission = await JsonService.get_specific_data(name_data="commissionSum")
    commission_amount: float = await CryptoCheck.transaction_amount(
        amount=commission,
        currency_from="USD",
        currency_to=state_data["currency_to"],
        margins=1,
    )
    amount_to: float = await CryptoCheck.transaction_amount(
        amount=minimal_amount,
        currency_from=state_data["currency_from"],
        currency_to=state_data["currency_to"],
        margins=walletPercent,
    )
    amount_to -= commission_amount
    await state.update_data(amount_to=amount_to)
    text = botMessages["checkTheCorrectTransaction"].format(
        name_net=state_data["currency_to"],
        address=state_data["user_requisites"],
        amount_from=minimal_amount,
        currency_from=state_data["currency_from"],
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
    await state.set_state(FSMFiatCrypto.check_validate_sum)
