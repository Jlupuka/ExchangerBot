from aiogram import Router
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from factories.factory import AdminCallbackFactory
from filters.filters import IsAdmin, CheckState
from keyboard.keyboard_factory import Factories

from lexicon.lexicon import (
    botMessages,
    errorLexicon,
    repeatAddress,
    walletType,
    backLexicon,
)
from services.cardService import CardCheck
from services.cryptoService import CryptoCheck
from services.dataService import JsonService
from states.states import FSMAddWallet

router: Router = Router()


@router.message(StateFilter(FSMAddWallet.currency_to), IsAdmin())
async def get_crypto_to(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMAddWallet.address)
    patterns = await JsonService.get_token_patterns()
    if message.text.lower() in patterns.keys():
        await state.update_data(currency_to=message.text.lower())
        await message.answer(
            text=botMessages["getNameNet"],
            reply_markup=await Factories.create_fac_menu(
                AdminCallbackFactory,
                back="wallets",
                back_name=backLexicon["backLexicon"],
            ),
        )
    else:
        await message.answer(
            text=errorLexicon["errorToken"].format(net=message.text),
            reply_markup=await Factories.create_fac_menu(
                AdminCallbackFactory,
                back="wallets",
                back_name=backLexicon["cancelLexicon"],
                **repeatAddress
            ),
        )


@router.message(StateFilter(FSMAddWallet.address), CheckState("currency_to"), IsAdmin())
async def get_token_address(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMAddWallet.type_wallet)
    state_data: dict[str:str] = await state.get_data()
    token: str = state_data["currency_to"]
    address: str = message.text
    if (await CryptoCheck.validate_crypto_address(token=token, address=address))[0]:
        if token.lower() == "спб":
            address = await CardCheck.preprocess_phone(phone=address)
        await state.update_data(address=address)
        await message.answer(
            text=botMessages["getWalletType"],
            reply_markup=await Factories.create_fac_menu(
                AdminCallbackFactory,
                back="wallets",
                back_name=backLexicon["cancelLexicon"],
                sizes=(2, 1),
                **walletType
            ),
        )
    else:
        await message.answer(
            text=errorLexicon["errorAddress"].format(net=token, wallet_address=address),
            reply_markup=await Factories.create_fac_menu(
                AdminCallbackFactory,
                back="wallets",
                back_name=backLexicon["cancelLexicon"],
                **repeatAddress
            ),
        )
