from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from factories.factory import AdminCallbackFactory
from filters.filters import IsAdmin, CheckState, IsDigitPercent
from keyboard.keyboard_factory import create_fac_menu

from lexicon.lexicon import botMessages, startCallbackAdmin, errorLexicon, repeatAddress, walletType, \
    repeatGetPercent, backLexicon, getPercent
from services.cryptoService import CryptoCheck, token_patterns
from states.states import FSMAddWallet, FSMPercentEdit

router = Router()


@router.message(Command(commands=['start']), IsAdmin())
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text=botMessages['startMessageAdmin'],
        reply_markup=await create_fac_menu(AdminCallbackFactory,
                                           sizes=(2, 2),
                                           back_page='main',
                                           **startCallbackAdmin)
    )


@router.message(StateFilter(FSMAddWallet.crypto_to), IsAdmin())
async def get_crypto_to(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMAddWallet.address)
    if message.text.lower() in token_patterns.keys():
        await state.update_data(crypto_to=message.text.lower())
        await message.answer(text=botMessages['getNameNet'],
                             reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                back='wallets',
                                                                back_name=backLexicon['backLexicon']))
    else:
        await message.answer(text=errorLexicon['errorToken'].format(net=message.text),
                             reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                back='wallets',
                                                                back_name=backLexicon['cancelLexicon'],
                                                                **repeatAddress))


@router.message(StateFilter(FSMAddWallet.address), CheckState('crypto_to'), IsAdmin())
async def get_crypto_address(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMAddWallet.type_wallet)
    state_data: dict[str: str] = await state.get_data()
    crypto_token: str = state_data['crypto_to'].lower()
    address: str = message.text
    if (await CryptoCheck.validate_crypto_address(crypto=crypto_token, address=address))[0]:
        await state.update_data(address=address)
        await message.answer(text=botMessages['getWalletType'],
                             reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                back='wallets',
                                                                back_name=backLexicon['cancelLexicon'],
                                                                sizes=(2, 1),
                                                                **walletType))
    else:
        await message.answer(text=errorLexicon['errorAddress'].format(net=crypto_token, wallet_address=address),
                             reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                back='wallets',
                                                                back_name=backLexicon['cancelLexicon'],
                                                                **repeatAddress))


@router.message(StateFilter(FSMPercentEdit.get_percent), IsDigitPercent(), IsAdmin())
async def get_percent(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMPercentEdit.check_percent)
    await state.update_data(percent=float(message.text))
    await message.answer(text=botMessages['getPercent'].format(percent=message.text),
                         reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                            back='addressEdit',
                                                            back_name=backLexicon['cancelLexicon'],
                                                            **getPercent))


@router.message(StateFilter(FSMPercentEdit.get_percent), IsAdmin())
async def error_get_percent(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMPercentEdit.check_percent)
    await message.answer(text=errorLexicon['getPercent'].format(percent=message.text),
                         reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                            sizes=(2,),
                                                            back='addressEdit',
                                                            back_name=backLexicon['cancelLexicon'],
                                                            **repeatGetPercent))
