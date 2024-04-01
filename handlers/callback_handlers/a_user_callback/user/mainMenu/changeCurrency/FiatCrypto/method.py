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
from services.JsonService import JsonService
from services.walletService import WalletService
from states.states import FSMFiatCrypto

router: Router = Router()


@router.callback_query(
    UserCallbackFactory.filter(),
    IsToken(UserCallbackFactory),
    StateFilter(
        FSMFiatCrypto.method,
        FSMFiatCrypto.check_validate_sum,
        FSMFiatCrypto.get_sum_crypto,
    ),
)
@router.callback_query(
    UserCallbackFactory.filter(F.page.in_({"rub", "usd", "repeatGetSum"})),
    StateFilter(FSMFiatCrypto.method, FSMFiatCrypto.check_validate_sum),
)
async def method_FC(
    callback: CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext
) -> None:
    if callback_data.page != "repeatGetSum":
        await state.update_data(currency_from=callback_data.page.upper())
    state_data: dict[str:str] = await state.get_data()
    minimal_amount = await JsonService.get_specific_data(name_data="minSum")
    work_wallet: Wallets = await WalletService.random_wallet(
        NameNet=state_data["typeFiat"], Status=True
    )
    if state_data["currency_from"] != "RUB":
        minimal_amount = await CryptoCheck.minimal_summa(
            minSum=minimal_amount,
            currency_to=state_data["currency_to"],
            currency_from=state_data["currency_from"],
        )
    currency_rate: float = await CryptoCheck.currency_rate(
        currency_from=state_data["currency_from"],
        currency_to=state_data["currency_to"],
        margins=work_wallet.Percent,
    )
    await state.update_data(
        work_walletRequisites=work_wallet.Address,
        walletPercent=work_wallet.Percent,
        walletId=work_wallet.Id,
        WalletCurrency=work_wallet.NameNet,
    )
    await callback.message.edit_text(
        text=botMessages["getSum"].format(
            min_sum=minimal_amount,
            currency_from=state_data["currency_from"],
            currency_to=state_data["currency_to"],
            currency_rate=(
                format(currency_rate, ".7f") if currency_rate < 1 else currency_rate
            ),
        ),
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory,
            back_page=callback_data.page,
            back_name=backLexicon["backLexicon"],
            back=state_data["typeFiat"],
            **minSum,
        ),
    )
    await state.set_state(FSMFiatCrypto.get_sum)
