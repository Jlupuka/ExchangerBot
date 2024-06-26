from aiogram import Router, F

from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from databaseAPI.models import Wallets
from databaseAPI.models.models import TypesWallet
from lexicon.lexicon import (
    botMessages,
    fiatOrCrypto,
    writeGetOrSend,
)

from keyboard.keyboard_factory import Factories
from factories.factory import UserCallbackFactory
from services.stateService import StateService

from services.walletService import WalletService

router: Router = Router()


@router.callback_query(
    UserCallbackFactory.filter(
        F.page.in_({"rub-crypto", "crypto-rub", "crypto-crypto"})
    )
)
async def choice_rub_crypto(
    callback: CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext
) -> None:
    await state.clear()
    typeWallet = callback_data.page.split("-")[1]
    await state.update_data(typeTransaction=callback_data.page.upper())
    await StateService.set_states(
        state_name="currency_to", state_data=await state.get_data(), state=state
    )
    wallets_dict: dict[str:str] = await WalletService.get_wallets(
        Wallets.NameNet, typeWallet=TypesWallet[typeWallet]
    )
    size: tuple[int, ...] = await WalletService.get_size_wallet(
        len_wallet=len(wallets_dict), count_any_button=1
    )
    await callback.message.edit_text(
        text=botMessages["choiceToken"].format(
            typeWallet=fiatOrCrypto[typeWallet.upper()],
            typeTransaction=writeGetOrSend["SEND"],
        ),
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory,
            back_page=callback_data.page,
            back=callback_data.back_page,
            sizes=size,
            **wallets_dict,
        ),
    )
