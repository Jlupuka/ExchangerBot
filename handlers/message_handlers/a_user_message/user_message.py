from aiogram import Router, F, Bot
from aiogram.enums import ContentType
from aiogram.types import Message, PhotoSize, FSInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from config import config
from factories.factory import UserCallbackFactory
from filters.filters import IsCryptoAddress, IsDigit
from keyboard.keyboard_factory import Factories

from lexicon.lexicon import botMessages, startCallbackUser, checkCorrectAddress, repeatAddress, errorLexicon, \
    backLexicon, getSum, repeatGetSum, kycVerifyCheckAdmin
from services.cardService import CardCheck
from services.cryptoService import CryptoCheck
from services.dataService import JsonService
from services.stateService import StateService
from states.states import FSMFiatCrypto, FSMCryptoFiat, FSMCryptoCrypto, FSMVerify

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
    await message.answer(text=botMessages['checkCorrectAddress'].format(net=state_data['currency_to'].upper(),
                                                                        wallet_address=requisites),
                         reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                                      back='main',
                                                                      back_name=backLexicon['cancelLexicon'],
                                                                      sizes=(2, 1),
                                                                      **checkCorrectAddress
                                                                      ))


@router.message(StateFilter(FSMFiatCrypto.requisites, FSMCryptoFiat.requisites, FSMCryptoCrypto.requisites))
async def error_address(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    await StateService.set_states(state_name='check_validate', state_data=state_data, state=state)
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
    commission = await JsonService.get_specific_data(name_data='commissionSum')
    commission_amount: float = await CryptoCheck.transaction_amount(amount=commission,
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


@router.message(F.content_type == ContentType.PHOTO, StateFilter(FSMVerify.get_photo))
async def verif_user(message: Message, state: FSMContext, bot: Bot) -> None:
    verif_number: int = (await state.get_data())['verifNumber']
    admin_id: int = config.load_config().AdminId.ADMINID[0]
    photo: PhotoSize = message.photo[0]
    await bot.send_photo(chat_id=admin_id, photo=photo.file_id, caption=botMessages['sendVerifPhotoAdmin'].format(
        userID=message.from_user.id,
        verifNumber=verif_number,
    ),
                         reply_markup=await Factories.create_kyc_fac(user_id=message.from_user.id,
                                                                     verif_number=verif_number,
                                                                     **kycVerifyCheckAdmin))
    await message.answer(text=botMessages['sendVerifPhoto'])
    await state.clear()


@router.message(StateFilter(FSMVerify.get_photo))
async def error_verif_user(message: Message, state: FSMContext) -> None:
    photo: FSInputFile = FSInputFile('src/img/verifExample.png')
    verif_number: int = (await state.get_data())['verifNumber']
    await message.answer_photo(photo=photo, caption=errorLexicon['errorSendVerifPhoto'].format(
        contentType=message.content_type,
        numberVerif=verif_number
    ))
