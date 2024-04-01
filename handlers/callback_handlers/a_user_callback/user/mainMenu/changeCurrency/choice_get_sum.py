from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from databaseAPI.models import Wallets
from databaseAPI.models.models import TypesWallet

from lexicon.lexicon import botMessages, backLexicon, fiatOrCrypto, writeGetOrSend

from keyboard.keyboard_factory import Factories
from factories.factory import UserCallbackFactory
from services.stateService import StateService

from services.walletService import WalletService
from states.states import FSMFiatCrypto, FSMCryptoFiat, FSMCryptoCrypto

router: Router = Router()


@router.callback_query(
    UserCallbackFactory.filter(F.page == "choiceGetSum"),
    StateFilter(
        FSMFiatCrypto.check_validate,
        FSMFiatCrypto.method,
        FSMCryptoFiat.check_validate,
        FSMCryptoFiat.method,
        FSMCryptoCrypto.check_validate,
        FSMCryptoCrypto.method,
    ),
)
async def choice_method_get_sum(
    callback: CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext
) -> None:
    state_data = await state.get_data()
    typeTransaction = state_data["typeTransaction"].split("-")[0]
    if typeTransaction == "CRYPTO":
        await StateService.set_states(
            state_name="type_crypto", state_data=await state.get_data(), state=state
        )
    else:
        await state.set_state(FSMFiatCrypto.type_fiat)
    wallets_dict: dict[str:str] = await WalletService.get_wallets(
        Wallets.NameNet, typeWallet=TypesWallet[typeTransaction.lower()]
    )
    size: tuple[int, ...] = await WalletService.get_size_wallet(
        len_wallet=len(wallets_dict), count_any_button=1
    )
    await callback.message.edit_text(
        text=botMessages["choiceToken"].format(
            typeWallet=fiatOrCrypto[typeTransaction],
            typeTransaction=writeGetOrSend["GET"],
        ),
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory,
            back_page=callback_data.page,
            back="main",
            back_name=backLexicon["cancelLexicon"],
            sizes=size,
            **wallets_dict,
        ),
    )
