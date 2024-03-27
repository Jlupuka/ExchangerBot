from typing import NoReturn

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from databaseAPI.models import Wallets
from filters.filters import IsToken
from lexicon.lexicon import botMessages, backLexicon, minSum

from keyboard.keyboard_factory import Factories
from factories.factory import UserCallbackFactory

from services.cryptoService import CryptoCheck
from services.dataService import JsonService
from services.stateService import StateService
from services.walletService import WalletService
from states.states import FSMCryptoFiat, FSMCryptoCrypto

router: Router = Router()


@router.callback_query(
    UserCallbackFactory.filter(),
    IsToken(UserCallbackFactory),
    StateFilter(
        FSMCryptoFiat.method,
        FSMCryptoFiat.check_validate_sum,
        FSMCryptoFiat.get_sum_crypto,
        FSMCryptoCrypto.method,
        FSMCryptoCrypto.check_validate_sum,
        FSMCryptoCrypto.get_sum_crypto,
    ),
)
@router.callback_query(
    UserCallbackFactory.filter(F.page.in_({"rub", "usd", "repeatGetSum"})),
    StateFilter(
        FSMCryptoFiat.method,
        FSMCryptoFiat.check_validate_sum,
        FSMCryptoCrypto.method,
        FSMCryptoCrypto.check_validate_sum,
    ),
)
async def method_CC_CF(
    callback: CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext
) -> NoReturn:
    if callback_data.page != "repeatGetSum":
        await state.update_data(currency_from=callback_data.page.upper())
    state_data: dict[str:str] = await state.get_data()
    work_wallet: Wallets = await WalletService.random_wallet(
        name_net=state_data["typeCrypto"]
    )
    if state_data["currency_to"] == "СПБ":
        state_data["currency_to"] = "RUB"
    minimal_amount = await JsonService.get_specific_data(name_data="minSum")
    if state_data["currency_from"] != "RUB":
        minimal_amount = await CryptoCheck.minimal_summa(
            minSum=minimal_amount,
            currency_to=state_data["currency_to"],
            currency_from=state_data["currency_from"],
        )
    currency_rate: float = await CryptoCheck.currency_rate(
        currency_from=state_data["currency_from"],
        currency_to=state_data["typeCrypto"],
        margins=work_wallet.Percent,
    )
    await state.update_data(
        work_walletRequisites=work_wallet.Address,
        walletPercent=work_wallet.Percent,
        walletId=work_wallet.Id,
        WalletCurrency=work_wallet.NameNet,
    )
    commission = await JsonService.get_specific_data(name_data="commissionSum")
    commission_amount: float = await CryptoCheck.transaction_amount(
        amount=commission,
        currency_from="USD",
        currency_to=state_data["typeCrypto"],
        margins=1,
    )
    await callback.message.edit_text(
        text=botMessages["getSumCrypto"].format(
            min_sum=minimal_amount,
            currency_from=state_data["currency_from"],
            currency_to=state_data["typeCrypto"],
            currency_rate=format(currency_rate, '.7f') if currency_rate < 1 else currency_rate,
            commission=commission_amount,
        ),
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory,
            back_page=callback_data.page,
            back_name=backLexicon["backLexicon"],
            back="back-method",
            **minSum,
        ),
    )
    await StateService.set_states(
        "get_sum", state_data=await state.get_data(), state=state
    )
