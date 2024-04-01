from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from databaseAPI.models import Wallets
from databaseAPI.models.models import TypesWallet
from filters.filters import IsToken
from lexicon.lexicon import (
    botMessages,
    choiceMethod,
    backLexicon,
    fiatOrCrypto,
    writeGetOrSend,
)

from keyboard.keyboard_factory import Factories
from factories.factory import UserCallbackFactory

from services.stateService import StateService
from services.walletService import WalletService
from states.states import FSMFiatCrypto, FSMCryptoFiat, FSMCryptoCrypto

router: Router = Router()


@router.callback_query(
    UserCallbackFactory.filter(F.page == "back-method"),
    StateFilter(
        FSMFiatCrypto.get_sum_crypto,
        FSMCryptoFiat.get_sum_crypto,
        FSMCryptoCrypto.get_sum_crypto,
        FSMFiatCrypto.method,
        FSMCryptoFiat.method,
        FSMCryptoCrypto.method,
        FSMFiatCrypto.get_sum,
        FSMCryptoFiat.get_sum,
        FSMCryptoCrypto.get_sum,
    ),
)
@router.callback_query(
    UserCallbackFactory.filter(),
    IsToken(UserCallbackFactory),
    StateFilter(
        FSMFiatCrypto.type_fiat,
        FSMFiatCrypto.get_sum,
        FSMCryptoFiat.type_crypto,
        FSMCryptoFiat.get_sum,
        FSMCryptoCrypto.type_crypto,
        FSMCryptoCrypto.get_sum,
    ),
)
async def save_type_fiat_transaction(
    callback: CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext
) -> None:
    state_data: dict[str:str] = await state.get_data()
    await StateService.set_states(
        state_name="method", state_data=state_data, state=state
    )
    if callback_data.page != "back-method":
        if state_data["typeTransaction"].split("-")[0] == "RUB":
            await state.update_data(typeFiat=callback_data.page.upper())
        else:
            await state.update_data(typeCrypto=callback_data.page.upper())
    await callback.message.edit_text(
        text=botMessages["choiceMethod"],
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory,
            back="choiceGetSum",
            back_page=callback_data.page,
            sizes=(3, 1),
            back_name=backLexicon["backLexicon"],
            **choiceMethod,
        ),
    )


@router.callback_query(
    UserCallbackFactory.filter(F.page == "crypto"),
    StateFilter(
        FSMFiatCrypto.method,
        FSMFiatCrypto.check_validate_sum,
        FSMCryptoFiat.method,
        FSMCryptoFiat.check_validate_sum,
        FSMCryptoCrypto.method,
        FSMCryptoCrypto.check_validate_sum,
    ),
)
async def crypto_method(
    callback: CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext
) -> None:
    await StateService.set_states(
        state_name="get_sum_crypto", state_data=await state.get_data(), state=state
    )
    wallets_dict: dict[str:str] = await WalletService.get_wallets(
        Wallets.NameNet, typeWallet=TypesWallet.crypto
    )
    size: tuple[int, ...] = await WalletService.get_size_wallet(
        len_wallet=len(wallets_dict), count_any_button=1
    )
    await callback.message.edit_text(
        text=botMessages["choiceToken"].format(
            typeWallet=fiatOrCrypto["CRYPTO"],
            typeTransaction=writeGetOrSend["TRANSLATE"],
        ),
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory,
            back_page=callback_data.page,
            back="back-method",
            sizes=size,
            **wallets_dict,
        ),
    )
