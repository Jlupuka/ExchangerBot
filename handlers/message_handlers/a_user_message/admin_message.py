from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from factories.factory import AdminCallbackFactory, MissionCallbackFactory
from filters.filters import IsAdmin, CheckState, IsDigit
from keyboard.keyboard_factory import Factories

from lexicon.lexicon import botMessages, startCallbackAdmin, errorLexicon, repeatAddress, walletType, \
    repeatGetPercent, backLexicon, checkPercent, revokeMission, yesLexicon
from services.cardService import CardCheck
from services.cryptoService import CryptoCheck
from services.dataService import JsonService
from states.states import FSMAddWallet, FSMPercentEdit, FSMRevokeMission, FSMEditPatterns, FSMEditMinSum

router = Router()


@router.message(Command(commands=['start']), IsAdmin())
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text=botMessages['startMessageAdmin'],
        reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                     sizes=(2, 2),
                                                     back_page='main',
                                                     **startCallbackAdmin)
    )


@router.message(StateFilter(FSMAddWallet.currency_to), IsAdmin())
async def get_crypto_to(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMAddWallet.address)
    patterns = await JsonService.get_token_patterns()
    if message.text.lower() in patterns.keys():
        await state.update_data(currency_to=message.text.lower())
        await message.answer(text=botMessages['getNameNet'],
                             reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                                          back='wallets',
                                                                          back_name=backLexicon['backLexicon']))
    else:
        await message.answer(text=errorLexicon['errorToken'].format(net=message.text),
                             reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                                          back='wallets',
                                                                          back_name=backLexicon['cancelLexicon'],
                                                                          **repeatAddress))


@router.message(StateFilter(FSMAddWallet.address), CheckState('currency_to'), IsAdmin())
async def get_token_address(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMAddWallet.type_wallet)
    state_data: dict[str: str] = await state.get_data()
    token: str = state_data['currency_to']
    address: str = message.text
    if (await CryptoCheck.validate_crypto_address(token=token, address=address))[0]:
        if token.lower() == 'спб':
            address = await CardCheck.preprocess_phone(phone=address)
        await state.update_data(address=address)
        await message.answer(text=botMessages['getWalletType'],
                             reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                                          back='wallets',
                                                                          back_name=backLexicon['cancelLexicon'],
                                                                          sizes=(2, 1),
                                                                          **walletType))
    else:
        await message.answer(text=errorLexicon['errorAddress'].format(net=token, wallet_address=address),
                             reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                                          back='wallets',
                                                                          back_name=backLexicon['cancelLexicon'],
                                                                          **repeatAddress))


@router.message(StateFilter(FSMPercentEdit.get_percent), IsDigit(check_percent=True), IsAdmin())
async def get_percent(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMPercentEdit.check_percent)
    await state.update_data(percent=float(message.text))
    await message.answer(text=botMessages['getPercent'].format(percent=message.text),
                         reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                                      back='addressEdit',
                                                                      back_name=backLexicon['cancelLexicon'],
                                                                      **checkPercent))


@router.message(StateFilter(FSMPercentEdit.get_percent), IsAdmin())
async def error_get_percent(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMPercentEdit.check_percent)
    await message.answer(text=errorLexicon['IsDigit'].format(digit=message.text),
                         reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                                      sizes=(2,),
                                                                      back='addressEdit',
                                                                      back_name=backLexicon['cancelLexicon'],
                                                                      **repeatGetPercent))


@router.message(StateFilter(FSMRevokeMission.message), IsAdmin())
async def sure_revoke_mission(message: Message, state: FSMContext, bot: Bot) -> None:
    await state.set_state(FSMRevokeMission.sure)
    await state.update_data(typeRevoke='WithMessage', messageRevoke=message.text)
    message_id = (await state.get_data())['messageID']
    mission_id: int = (await state.get_data())['missionID']
    await message.answer(text=botMessages['sureRevokeWithMessage'].format(
        missionID=mission_id, messageRevoke=message.text),
        reply_markup=await Factories.create_fac_mission(MissionCallbackFactory,
                                                        mission_id=mission_id,
                                                        back=mission_id,
                                                        back_name=backLexicon['backLexicon'],
                                                        sizes=(1, 1),
                                                        **revokeMission))
    await bot.delete_message(chat_id=message.from_user.id, message_id=message_id)
    await message.delete()


@router.message(StateFilter(FSMEditPatterns.get_token_name), IsAdmin())
async def get_pattern(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMEditPatterns.get_pattern)
    await state.update_data(token=message.text)
    await message.answer(text=botMessages['getPattern'].format(
        token=message.text
    ), reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                    back='settings',
                                                    back_name=backLexicon['cancelLexicon']))


@router.message(StateFilter(FSMEditPatterns.get_pattern), IsAdmin())
async def get_pattern(message: Message, state: FSMContext) -> None:
    await state.update_data(pattern=message.text)
    await state.set_state(FSMEditPatterns.check_sure)
    token = (await state.get_data())['token']
    await message.answer(text=botMessages['sureAddedPattern'].format(
        token=token,
        pattern=message.text
    ), reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                    back='settings',
                                                    back_name=backLexicon['cancelLexicon'],
                                                    **yesLexicon))


@router.message(StateFilter(FSMEditMinSum.get_sum), IsDigit(), IsAdmin())
async def sure_update_min_sum(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMEditMinSum.check_sure)
    await state.update_data(minSum=float(message.text))
    await message.answer(text=botMessages['sureUpdateMinSum'].format(
        minSum=float(message.text)
    ), reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                    back='settings',
                                                    back_name=backLexicon['cancelLexicon'],
                                                    **yesLexicon))
