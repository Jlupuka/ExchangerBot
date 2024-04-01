from aiogram import Router
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from config.config import load_config
from databaseAPI.commands.mnemonic_commands import MnemonicAPI
from databaseAPI.commands.walletAddress_commands import WalletAPI
from databaseAPI.models.models import TypesWallet, Wallets
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
from services.cryptoWalletAPIService import CryptoWalletAPIService
from services.JsonService import JsonService
from services.walletService import WalletService
from states.states import FSMAddWallet

router: Router = Router()


@router.message(StateFilter(FSMAddWallet.currency_to), IsAdmin())
async def get_token_to(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMAddWallet.address)
    patterns = await JsonService.get_token_patterns()
    if message.text.lower() in patterns.keys():
        await state.update_data(currency_to=message.text.lower())
        if await WalletService.check_token(token=message.text):
            await state.set_state(FSMAddWallet.mnemonic)
            await message.answer(
                text=botMessages["getMnemonicNet"].format(token=message.text.upper()),
                reply_markup=await Factories.create_fac_menu(
                    AdminCallbackFactory,
                    back="wallets",
                    back_name=backLexicon["backLexicon"],
                ),
            )
        else:
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
                **repeatAddress,
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
                **walletType,
            ),
        )
    else:
        await message.answer(
            text=errorLexicon["errorAddress"].format(net=token, wallet_address=address),
            reply_markup=await Factories.create_fac_menu(
                AdminCallbackFactory,
                back="wallets",
                back_name=backLexicon["cancelLexicon"],
                **repeatAddress,
            ),
        )


@router.message(
    StateFilter(FSMAddWallet.mnemonic), CheckState("currency_to"), IsAdmin()
)
async def get_mnemonic(message: Message, state: FSMContext) -> None:
    token: str = (await state.get_data())["currency_to"].upper()
    try:
        client, crypto_api = await CryptoWalletAPIService.get_api_and_client(
            token=token, private_key=message.text
        )
        address = crypto_api.address
        secret_key = load_config().SecretKey.SECRETKEY
        wallet: Wallets = await WalletAPI.add_wallet(
            name_net=token, address=address, type_wallet=TypesWallet.crypto
        )
        if wallet:
            await MnemonicAPI.add_mnemonic(
                WalletId=wallet.Id,
                EncryptMnemonic=await WalletService.encrypt_private_key(
                    private_key=message.text, secret_key=secret_key
                ),
            )
            await message.answer(
                text=botMessages["addMnemonic"].format(token=token, address=address),
                reply_markup=await Factories.create_fac_menu(
                    AdminCallbackFactory,
                    back="wallets",
                    back_name=backLexicon["backLexicon"],
                ),
            )
        else:
            await message.answer(
                text=errorLexicon["WalletExist"].format(
                    nameNet=token, address=address, walletType=TypesWallet.crypto.value
                ),
                reply_markup=await Factories.create_fac_menu(
                    AdminCallbackFactory,
                    back="wallets",
                    back_name=backLexicon["backLexicon"],
                ),
            )
    except ValueError:
        await message.answer(
            text=errorLexicon["addMnemonic"].format(token=token, mnemonic=message.text),
            reply_markup=await Factories.create_fac_menu(
                AdminCallbackFactory,
                back="wallets",
                back_name=backLexicon["backLexicon"],
            ),
        )
    await state.clear()
