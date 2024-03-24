from typing import NoReturn

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from lexicon.lexicon import botMessages, backLexicon, receiptVerification

from keyboard.keyboard_factory import Factories
from factories.factory import UserCallbackFactory

from services.cryptoService import CryptoCheck

from states.states import FSMFiatCrypto

router: Router = Router()


@router.callback_query(
    UserCallbackFactory.filter(F.page == "getSum"),
    StateFilter(FSMFiatCrypto.check_validate_sum),
)
async def receipt_verification_FC(
    callback: CallbackQuery, state: FSMContext
) -> NoReturn:
    await state.set_state(FSMFiatCrypto.money_sent)
    state_data: dict[str:str] = await state.get_data()
    rub_amount_from = await CryptoCheck.transaction_amount(
        amount=state_data["amount_from"],
        currency_to="RUB",
        currency_from=state_data["currency_from"],
    )
    await state.update_data(amount_from=rub_amount_from)
    text = botMessages["receiptVerification"].format(
        amount_to=state_data["amount_to"],
        currency_to=state_data["currency_to"],
        amount_from=rub_amount_from,
        type_transaction=state_data["WalletCurrency"],
        work_wallet=state_data["work_walletRequisites"],
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory,
            back="main",
            back_name=backLexicon["cancelLexicon"],
            **receiptVerification,
        ),
    )
