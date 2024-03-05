from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from factories.factory import UserCallbackFactory
from filters.filters import IsCryptoAddress, IsDigit
from keyboard.keyboard_factory import Factories

from lexicon.lexicon import botMessages, startCallbackUser, checkCorrectAddress, repeatAddress, errorLexicon, \
    backLexicon, getSum, repeatGetSum
from services import logger
from services.cardService import CardCheck
from services.cryptoService import CryptoCheck, commission_sum
from services.stateService import StateService
from states.states import FSMFiatCrypto, FSMCryptoFiat, FSMCryptoCrypto

router = Router()


@router.message(Command(commands=['start', 'cancel']))
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text=botMessages['startMessageAdmin'],
        reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                     back_page='main',
                                                     sizes=(2, 1, 2), **startCallbackUser)
    )


@router.message(StateFilter(FSMFiatCrypto.requisites, FSMCryptoFiat.requisites, FSMCryptoCrypto.requisites),
                IsCryptoAddress())
async def add_mission(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    requisites = message.text
    if state_data['currency_to'] == 'СПБ':
        requisites = await CardCheck.preprocess_phone(phone=requisites)
    await state.update_data(user_requisites=requisites)
    await StateService.set_states(state_name='check_validate', state_data=state_data, state=state)
    logger.debug(state_data)
    await message.answer(text=botMessages['checkCorrectAddress'].format(net=state_data['currency_to'].upper(),
                                                                        wallet_address=requisites),
                         reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                                      back='main',
                                                                      back_name=backLexicon['cancelLexicon'],
                                                                      sizes=(2, 1),
                                                                      **checkCorrectAddress
                                                                      ))


@router.message(StateFilter(FSMFiatCrypto.requisites))
async def error_address(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMFiatCrypto.check_validate)
    state_data = await state.get_data()
    logger.debug(state_data)
    await message.answer(text=errorLexicon['errorAddress'].format(net=state_data['currency_to'],
                                                                  wallet_address=message.text),
                         reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                                      back='main',
                                                                      back_name=backLexicon['cancelLexicon'],
                                                                      **repeatAddress
                                                                      ))


@router.message(StateFilter(FSMCryptoFiat.get_sum, FSMCryptoCrypto.get_sum), IsDigit(check_min=True))
async def check_the_correct_transaction_CC_CF(message: Message, state: FSMContext) -> None:
    await state.update_data(amount_from=float(message.text))
    state_data: dict[str: str] = await state.get_data()
    walletPercent = state_data['walletPercent']
    if state_data['currency_to'] == 'СПБ':
        state_data['currency_to'] = 'RUB'
    commission_amount: float = await CryptoCheck.transaction_amount(amount=commission_sum,
                                                                    currency_from='USD',
                                                                    currency_to=state_data['currency_to'],
                                                                    margins=1)
    amount_to: float = await CryptoCheck.transaction_amount(amount=state_data['amount_from'],
                                                            currency_from=state_data['currency_from'],
                                                            currency_to=state_data['currency_to'],
                                                            margins=walletPercent)
    amount_to -= commission_amount
    amount_from: float = await CryptoCheck.transaction_amount(amount=state_data['amount_from'],
                                                              currency_from=state_data['currency_from'],
                                                              currency_to=state_data['typeCrypto'],
                                                              margins=1)
    await state.update_data(amount_to=amount_to, amount_from=amount_from)
    text = botMessages['checkTheCorrectTransaction'].format(
        name_net=state_data['currency_to'],
        address=state_data['user_requisites'],
        amount_from=amount_from,
        currency_from=state_data['typeCrypto'],
        currency_to=state_data['currency_to'],
        amount_to=amount_to
    )
    await message.answer(text=text, reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                                                 sizes=(2,),
                                                                                 back='main',
                                                                                 back_name=backLexicon['cancelLexicon'],
                                                                                 **getSum))
    await StateService.set_states(state_name='check_validate_sum', state_data=state_data, state=state)


@router.message(StateFilter(FSMFiatCrypto.get_sum), IsDigit(check_min=True))
async def check_the_correct_transaction_FC(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMFiatCrypto.check_validate_sum)
    await state.update_data(amount_from=float(message.text))
    state_data: dict[str: str] = await state.get_data()
    walletPercent = state_data['walletPercent']
    amount_to: float = await CryptoCheck.transaction_amount(amount=state_data['amount_from'],
                                                            currency_from=state_data['currency_from'],
                                                            currency_to=state_data['currency_to'],
                                                            margins=walletPercent)
    await state.update_data(amount_to=amount_to)
    text = botMessages['checkTheCorrectTransaction'].format(
        name_net=state_data['currency_to'],
        address=state_data['user_requisites'],
        amount_from=state_data['amount_from'],
        currency_from=state_data['currency_from'],
        currency_to=state_data['currency_to'],
        amount_to=amount_to
    )
    await message.answer(text=text, reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                                                 sizes=(2,),
                                                                                 back='main',
                                                                                 back_name=backLexicon['cancelLexicon'],
                                                                                 **getSum))


@router.message(StateFilter(FSMFiatCrypto.get_sum, FSMCryptoCrypto.get_sum, FSMCryptoFiat.get_sum),
                IsDigit(check_min=False))
async def failed_the_minimum_test(message: Message, state: FSMContext) -> None:
    state_data: dict[str: str] = await state.get_data()
    await message.answer(text=errorLexicon['getSum_minimal'].format(amount=message.text,
                                                                    currency_from=state_data['currency_from']),
                         reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                                      back='main',
                                                                      back_name=backLexicon['cancelLexicon'],
                                                                      **repeatGetSum))
    await StateService.set_states(state_name='check_validate_sum', state_data=state_data, state=state)


@router.message(StateFilter(FSMFiatCrypto.get_sum))
async def failed_the_digit_test(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMFiatCrypto.check_validate_sum)
    await message.answer(text=errorLexicon['IsDigit'].format(digit=message.text),
                         reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                                      back='main',
                                                                      back_name=backLexicon['cancelLexicon'],
                                                                      **repeatGetSum))
