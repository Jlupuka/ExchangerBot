from typing import Union
from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from dataTemplates.data_templates import WalletTRX
from lexicon.lexicon import botMessages, backLexicon, receiptVerification

from keyboard.keyboard_factory import Factories
from factories.factory import UserCallbackFactory
from services.JsonService import JsonService
from services.dataTemplatesService import DataTemplatesService

from services.qrCodeService import QRCodeService
from services.stateService import StateService
from states.states import FSMCryptoFiat, FSMCryptoCrypto

router: Router = Router()


@router.callback_query(
    UserCallbackFactory.filter(F.page == "getSum"),
    StateFilter(
        FSMCryptoFiat.check_validate_mnemonic_sum,
        FSMCryptoCrypto.check_validate_mnemonic_sum,
    ),
)
async def receipt_verification_CC_CF(
    callback: CallbackQuery, state: FSMContext, bot: Bot
) -> None:
    state_data: dict[str:str] = await state.get_data()
    wallet_template = await DataTemplatesService.select_crypto_data_templates(
        token=state_data["typeCrypto"]
    )
    wallet_data: Union[WalletTRX] = wallet_template(**state_data["WalletData"])
    file_path: str = await QRCodeService.create_crypto_payment_qrcode(
        amount=state_data["amount_from"],
        crypto_currency=state_data["typeCrypto"],
        address=wallet_data.base58check_address,
        description=f"UserId-{callback.from_user.id}",
    )
    photo: FSInputFile = FSInputFile(file_path)
    await callback.message.delete()
    await bot.send_photo(chat_id=callback.from_user.id, photo=photo)
    text = botMessages["receiptVerification"].format(
        amount_to=state_data["amount_to"],
        currency_to=state_data["currency_to"],
        amount_from=state_data["amount_from"],
        type_transaction=state_data["WalletCurrency"],
        work_wallet=wallet_data.base58check_address,
    )
    await bot.send_message(
        chat_id=callback.from_user.id,
        text=text,
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory,
            back="main",
            back_name=backLexicon["cancelLexicon"],
            **receiptVerification,
        ),
    )
    await StateService.set_states(
        state_name="money_sent_mnemonic", state_data=state_data, state=state
    )
    await JsonService.save_work_wallets_data(
        token=state_data["typeCrypto"], wallet_data=wallet_data
    )
    await QRCodeService.delete_file(file_name=file_path)
