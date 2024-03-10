from aiogram import Router, Bot, exceptions, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from databaseAPI.commands.submissions_commands import SubmissionsAPI
from databaseAPI.commands.userCommands.user_commands import UserAPI
from databaseAPI.commands.walletAddress_commands import WalletAPI
from databaseAPI.tables import WalletAddress, Submissions, Users
from filters.filters import IsToken
from lexicon.lexicon import botMessages, startCallbackUser, profileUser, listMissions, choiceMethod, \
    backLexicon, minSum, receiptVerification, getSum, fiatOrCrypto, sendMission, changeStatus, writeFiatOrCrypto, \
    errorLexicon, revokeButton, kycVerificationLexicon, writeGetOrSend

from keyboard.keyboard_factory import Factories
from factories.factory import UserCallbackFactory, MissionCallbackFactory

from services.cryptoService import CryptoCheck
from services.dataService import JsonService
from services.qrCodeService import QRCodeService
from services.stateService import StateService
from services.submissionService import SubmissionService
from services.userService import UserService
from services.walletService import WalletService
from states.states import FSMFiatCrypto, FSMCryptoFiat, FSMCryptoCrypto, FSMVerify

router: Router = Router()


@router.callback_query(MissionCallbackFactory.filter(F.page == 'main'))
@router.callback_query(UserCallbackFactory.filter(F.page == 'main'))
async def main_handler(callback: CallbackQuery, state: FSMContext, callback_data: UserCallbackFactory) -> None:
    await state.clear()
    await callback.message.edit_text(
        text=botMessages['startMessageUser'],
        reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                     back_page=callback_data.page,
                                                     sizes=(2, 1, 2),
                                                     **startCallbackUser)
    )


@router.callback_query(UserCallbackFactory.filter(F.page == 'info'))
async def info_handler(callback: CallbackQuery, callback_data: UserCallbackFactory, bot: Bot) -> None:
    await callback.message.edit_text(text=botMessages['informationUser'].format(
        botName=(await bot.get_me()).username
    ), reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                    back=callback_data.back_page,
                                                    back_name=backLexicon['backMainMenu']))


@router.callback_query(UserCallbackFactory.filter(F.page == 'profile'))
async def profile_handler(callback: CallbackQuery, callback_data: UserCallbackFactory) -> None:
    user: Users = await UserAPI.select_user(user_id=callback.from_user.id)
    await callback.message.edit_text(text=botMessages['profileTextUser'].format(
        userID=user.UserId,
        KYCStatus=kycVerificationLexicon[user.KYC],
        dateRegistration=await UserService.format_date_string(date_string=str(user.DateTime))
    ),
        reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                     back_page=callback_data.page,
                                                     back='main',
                                                     sizes=(2,), **profileUser))


@router.callback_query(UserCallbackFactory.filter(F.page == 'statistics'))
async def statistics_handler(callback: CallbackQuery, callback_data: UserCallbackFactory) -> None:
    await callback.message.edit_text(text=botMessages['statisticTextUser'].format(
        **await UserService.statistic_user(user_id=callback.from_user.id)),
        reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                     back_page='main',
                                                     back=callback_data.back_page))


@router.callback_query(UserCallbackFactory.filter(F.page == 'missions'))
@router.callback_query(MissionCallbackFactory.filter(F.page == 'missions'))
async def missions_handler(callback: CallbackQuery, callback_data: UserCallbackFactory) -> None:
    await callback.message.edit_text(text=botMessages['missionsTextUser'],
                                     reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                                                  back_page=callback_data.page,
                                                                                  back='profile',
                                                                                  sizes=(3,),
                                                                                  **listMissions))


@router.callback_query(UserCallbackFactory.filter(F.page.in_({'wait', 'accepted', 'completed'})))
async def accepted_missions_handler(callback: CallbackQuery, callback_data: UserCallbackFactory) -> None:
    try:
        mission_status = callback_data.page.upper()
        missions_data: list[Submissions] = await (
            SubmissionsAPI.get_user_missions_by_status(mission_status=mission_status,
                                                       user_id=callback.from_user.id,
                                                       pagination=True,
                                                       offset=callback_data.mission_page))
        if missions_data:
            mission_count = await SubmissionsAPI.get_count_user_missions_by_status(mission_status=mission_status,
                                                                                   user_id=callback.from_user.id)
            text, preprocess_mission = await SubmissionService.preprocess_mission_data(mission_data=missions_data)
            await callback.message.edit_text(
                text=text,
                reply_markup=await Factories.create_fac_pagination_missions(factory=UserCallbackFactory,
                                                                            mission_status=callback_data.page,
                                                                            back_page=callback_data.page,
                                                                            back='missions',
                                                                            mission_count=mission_count,
                                                                            mission_page=callback_data.mission_page,
                                                                            **preprocess_mission))
        else:
            await callback.message.edit_text(text=errorLexicon['errorMission'],
                                             reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                                                          back_page=callback_data.page,
                                                                                          back='missions',
                                                                                          sizes=(3,),
                                                                                          **listMissions))
    except exceptions.TelegramBadRequest:
        pass
    finally:
        await callback.answer()


@router.callback_query(UserCallbackFactory.filter(F.page.in_({'rub-crypto', 'crypto-rub', 'crypto-crypto'})))
async def choice_rub_crypto(callback: CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext) -> None:
    await state.clear()
    typeWallet = callback_data.page.split('-')[1].upper()
    await state.update_data(typeTransaction=callback_data.page.upper())
    await StateService.set_states(state_name='currency_to', state_data=await state.get_data(), state=state)
    wallets_dict: dict[str: str] = await WalletService.get_wallets(func=WalletAPI.get_all_name_net_by_type,
                                                                   type_wallet=typeWallet)
    size: tuple[int, ...] = await WalletService.get_size_wallet(len_wallet=len(wallets_dict), count_any_button=1)
    await callback.message.edit_text(text=botMessages['choiceToken'].format(typeWallet=fiatOrCrypto[typeWallet],
                                                                            typeTransaction=writeGetOrSend['SEND']),
                                     reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                                                  back_page=callback_data.page,
                                                                                  back=callback_data.back_page,
                                                                                  sizes=size,
                                                                                  **wallets_dict))


@router.callback_query(UserCallbackFactory.filter(), IsToken(UserCallbackFactory),
                       StateFilter(FSMFiatCrypto.currency_to, FSMCryptoFiat.currency_to,
                                   FSMCryptoCrypto.currency_to))
async def get_wallet(callback: CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext) -> None:
    await state.update_data(currency_to=callback_data.page.upper())
    state_data: dict[str: str] = await state.get_data()
    await StateService.set_states(state_name='requisites', state_data=state_data, state=state)
    typeTransaction = state_data['typeTransaction'].split('-')[1]
    await callback.message.edit_text(
        text=botMessages['getAddressCrypto'].format(typeTransaction=writeFiatOrCrypto[typeTransaction]),
        reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                     back=callback_data.back_page,
                                                     back_page='main'))


@router.callback_query(UserCallbackFactory.filter(F.page.in_({'repeat', 'no'})),
                       StateFilter(FSMFiatCrypto.check_validate, FSMCryptoFiat.check_validate,
                                   FSMCryptoCrypto.check_validate))
async def repeat_get_wallet(callback: CallbackQuery, state: FSMContext) -> None:
    state_data: dict[str: str] = await state.get_data()
    typeTransaction = state_data['typeTransaction'].split('-')[1]
    await StateService.set_states(state_name='requisites', state_data=await state.get_data(), state=state)
    await callback.message.edit_text(text=botMessages['getAddressCrypto'].format(
        typeTransaction=writeFiatOrCrypto[typeTransaction]),
        reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                     back=state_data['typeTransaction'],
                                                     back_page='main'))


@router.callback_query(UserCallbackFactory.filter(F.page == 'choiceGetSum'),
                       StateFilter(FSMFiatCrypto.check_validate, FSMFiatCrypto.method,
                                   FSMCryptoFiat.check_validate, FSMCryptoFiat.method,
                                   FSMCryptoCrypto.check_validate, FSMCryptoCrypto.method))
async def choice_method_get_sum(callback: CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext) -> None:
    state_data = await state.get_data()
    typeTransaction = state_data['typeTransaction'].split('-')[0]
    if typeTransaction == 'CRYPTO':
        await StateService.set_states(state_name='type_crypto', state_data=await state.get_data(), state=state)
    else:
        await state.set_state(FSMFiatCrypto.type_fiat)
    wallets_dict: dict[str: str] = await WalletService.get_wallets(func=WalletAPI.get_all_name_net_by_type,
                                                                   type_wallet=typeTransaction)
    size: tuple[int, ...] = await WalletService.get_size_wallet(len_wallet=len(wallets_dict), count_any_button=1)
    await callback.message.edit_text(text=botMessages['choiceToken'].format(typeWallet=fiatOrCrypto[typeTransaction],
                                                                            typeTransaction=writeGetOrSend['GET']),
                                     reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                                                  back_page=callback_data.page,
                                                                                  back='main',
                                                                                  back_name=backLexicon[
                                                                                      'cancelLexicon'],
                                                                                  sizes=size,
                                                                                  **wallets_dict))


@router.callback_query(UserCallbackFactory.filter(F.page == 'back-method'),
                       StateFilter(FSMFiatCrypto.get_sum_crypto,
                                   FSMCryptoFiat.get_sum_crypto,
                                   FSMCryptoCrypto.get_sum_crypto,
                                   FSMFiatCrypto.method,
                                   FSMCryptoFiat.method,
                                   FSMCryptoCrypto.method,
                                   FSMFiatCrypto.get_sum,
                                   FSMCryptoFiat.get_sum,
                                   FSMCryptoCrypto.get_sum
                                   ))
@router.callback_query(UserCallbackFactory.filter(), IsToken(UserCallbackFactory),
                       StateFilter(FSMFiatCrypto.type_fiat, FSMFiatCrypto.get_sum,
                                   FSMCryptoFiat.type_crypto, FSMCryptoFiat.get_sum,
                                   FSMCryptoCrypto.type_crypto, FSMCryptoCrypto.get_sum))
async def save_type_fiat_transaction(callback: CallbackQuery,
                                     callback_data: UserCallbackFactory,
                                     state: FSMContext) -> None:
    state_data: dict[str: str] = await state.get_data()
    await StateService.set_states(state_name='method', state_data=state_data, state=state)
    if callback_data.page != 'back-method':
        if state_data['typeTransaction'].split('-')[0] == 'RUB':
            await state.update_data(typeFiat=callback_data.page.upper())
        else:
            await state.update_data(typeCrypto=callback_data.page.upper())
    await callback.message.edit_text(text=botMessages['choiceMethod'],
                                     reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                                                  back='choiceGetSum',
                                                                                  back_page=callback_data.page,
                                                                                  sizes=(3, 1),
                                                                                  back_name=backLexicon['backLexicon'],
                                                                                  **choiceMethod))


@router.callback_query(UserCallbackFactory.filter(F.page == 'crypto'),
                       StateFilter(FSMFiatCrypto.method, FSMFiatCrypto.check_validate_sum,
                                   FSMCryptoFiat.method, FSMCryptoFiat.check_validate_sum,
                                   FSMCryptoCrypto.method, FSMCryptoCrypto.check_validate_sum))
async def crypto_method(callback: CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext) -> None:
    await StateService.set_states(state_name='get_sum_crypto', state_data=await state.get_data(), state=state)
    wallets_dict: dict[str: str] = await WalletService.get_wallets(func=WalletAPI.get_all_name_net_by_type,
                                                                   type_wallet='CRYPTO')
    size: tuple[int, ...] = await WalletService.get_size_wallet(len_wallet=len(wallets_dict), count_any_button=1)
    await callback.message.edit_text(
        text=botMessages['choiceToken'].format(typeWallet=fiatOrCrypto['CRYPTO'],
                                               typeTransaction=writeGetOrSend['TRANSLATE']),
        reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                     back_page=callback_data.page,
                                                     back='back-method',
                                                     sizes=size,
                                                     **wallets_dict))


@router.callback_query(UserCallbackFactory.filter(), IsToken(UserCallbackFactory),
                       StateFilter(FSMCryptoFiat.method, FSMCryptoFiat.check_validate_sum,
                                   FSMCryptoFiat.get_sum_crypto,
                                   FSMCryptoCrypto.method, FSMCryptoCrypto.check_validate_sum,
                                   FSMCryptoCrypto.get_sum_crypto))
@router.callback_query(UserCallbackFactory.filter(F.page.in_({'rub', 'usd', 'repeatGetSum'})),
                       StateFilter(FSMCryptoFiat.method, FSMCryptoFiat.check_validate_sum,
                                   FSMCryptoCrypto.method, FSMCryptoCrypto.check_validate_sum))
async def rub_usd_method_CC_CF(callback: CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext) -> None:
    if callback_data.page != 'repeatGetSum':
        await state.update_data(currency_from=callback_data.page.upper())
    state_data: dict[str: str] = await state.get_data()
    work_wallet: WalletAddress = await WalletService.random_wallet(name_net=state_data['typeCrypto'])
    if state_data['currency_to'] == 'СПБ':
        state_data['currency_to'] = 'RUB'
    minimal_amount = await JsonService.get_specific_data(name_data='minSum')
    if state_data['currency_from'] != 'RUB':
        minimal_amount = await CryptoCheck.minimal_summa(minSum=minimal_amount,
                                                         currency_to=state_data['currency_to'],
                                                         currency_from=state_data['currency_from'])
    currency_rate: float = await CryptoCheck.currency_rate(currency_from=state_data['currency_from'],
                                                           currency_to=state_data['typeCrypto'],
                                                           margins=work_wallet.Percent)
    await state.update_data(work_walletRequisites=work_wallet.Address,
                            walletPercent=work_wallet.Percent,
                            walletId=work_wallet.Id,
                            WalletCurrency=work_wallet.NameNet)
    commission = await JsonService.get_specific_data(name_data='commissionSum')
    commission_amount: float = await CryptoCheck.transaction_amount(amount=commission,
                                                                    currency_from='USD',
                                                                    currency_to=state_data['typeCrypto'],
                                                                    margins=1)
    await callback.message.edit_text(text=botMessages['getSumCrypto'].format(min_sum=minimal_amount,
                                                                             currency_from=state_data['currency_from'],
                                                                             currency_to=state_data['typeCrypto'],
                                                                             currency_rate=currency_rate,
                                                                             commission=commission_amount),
                                     reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                                                  back_page=callback_data.page,
                                                                                  back_name=backLexicon['backLexicon'],
                                                                                  back='back-method',
                                                                                  **minSum))
    await StateService.set_states('get_sum', state_data=await state.get_data(), state=state)


@router.callback_query(UserCallbackFactory.filter(), IsToken(UserCallbackFactory),
                       StateFilter(FSMFiatCrypto.method, FSMFiatCrypto.check_validate_sum,
                                   FSMFiatCrypto.get_sum_crypto))
@router.callback_query(UserCallbackFactory.filter(F.page.in_({'rub', 'usd', 'repeatGetSum'})),
                       StateFilter(FSMFiatCrypto.method, FSMFiatCrypto.check_validate_sum))
async def rub_usd_method_FC(callback: CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext) -> None:
    if callback_data.page != 'repeatGetSum':
        await state.update_data(currency_from=callback_data.page.upper())
    state_data: dict[str: str] = await state.get_data()
    minimal_amount = await JsonService.get_specific_data(name_data='minSum')
    work_wallet: WalletAddress = await WalletService.random_wallet(name_net=state_data['typeFiat'])
    if state_data['currency_from'] != 'RUB':
        minimal_amount = await CryptoCheck.minimal_summa(minSum=minimal_amount,
                                                         currency_to=state_data['currency_to'],
                                                         currency_from=state_data['currency_from'])
    currency_rate: float = await CryptoCheck.currency_rate(currency_from=state_data['currency_from'],
                                                           currency_to=state_data['currency_to'],
                                                           margins=work_wallet.Percent)
    await state.update_data(work_walletRequisites=work_wallet.Address,
                            walletPercent=work_wallet.Percent,
                            walletId=work_wallet.Id,
                            WalletCurrency=work_wallet.NameNet)
    await callback.message.edit_text(text=botMessages['getSum'].format(min_sum=minimal_amount,
                                                                       currency_from=state_data['currency_from'],
                                                                       currency_to=state_data['currency_to'],
                                                                       currency_rate=currency_rate),
                                     reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                                                  back_page=callback_data.page,
                                                                                  back_name=backLexicon['backLexicon'],
                                                                                  back=state_data['typeFiat'],
                                                                                  **minSum))
    await state.set_state(FSMFiatCrypto.get_sum)


@router.callback_query(UserCallbackFactory.filter(F.page == 'minSum'), StateFilter(FSMCryptoFiat.get_sum,
                                                                                   FSMCryptoCrypto.get_sum))
async def set_minimal_amount_CC_CF(callback: CallbackQuery, state: FSMContext) -> None:
    state_data: dict[str: str] = await state.get_data()
    walletPercent = state_data['walletPercent']
    if state_data['currency_to'] == 'СПБ':
        state_data['currency_to'] = 'RUB'
    commission = await JsonService.get_specific_data(name_data='commissionSum')
    commission_amount: float = await CryptoCheck.transaction_amount(amount=commission,
                                                                    currency_from='USD',
                                                                    currency_to=state_data['currency_to'],
                                                                    margins=1)
    min_sum = await JsonService.get_specific_data(name_data='minSum')
    amount_to: float = await CryptoCheck.transaction_amount(amount=min_sum,
                                                            currency_from='RUB',
                                                            currency_to=state_data['currency_to'],
                                                            margins=walletPercent)
    amount_to -= commission_amount
    amount_from: float = await CryptoCheck.transaction_amount(amount=min_sum,
                                                              currency_from='RUB',
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
    await callback.message.edit_text(text=text, reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                                                             sizes=(2,),
                                                                                             back='main',
                                                                                             back_name=backLexicon[
                                                                                                 'cancelLexicon'],
                                                                                             **getSum))
    await StateService.set_states(state_name='check_validate_sum', state_data=state_data, state=state)


@router.callback_query(UserCallbackFactory.filter(F.page == 'minSum'), StateFilter(FSMFiatCrypto.get_sum))
async def set_minimal_amount_FC(callback: CallbackQuery, state: FSMContext) -> None:
    state_data: dict[str: str] = await state.get_data()
    minimal_amount = await JsonService.get_specific_data(name_data='minSum')
    if state_data['currency_from'] != 'RUB':
        minimal_amount = await CryptoCheck.minimal_summa(minSum=minimal_amount,
                                                         currency_to=state_data['currency_to'],
                                                         currency_from=state_data['currency_from'])
    await state.update_data(amount_from=minimal_amount)
    walletPercent = state_data['walletPercent']
    commission = await JsonService.get_specific_data(name_data='commissionSum')
    commission_amount: float = await CryptoCheck.transaction_amount(amount=commission,
                                                                    currency_from='USD',
                                                                    currency_to=state_data['currency_to'],
                                                                    margins=1)
    amount_to: float = await CryptoCheck.transaction_amount(amount=minimal_amount,
                                                            currency_from=state_data['currency_from'],
                                                            currency_to=state_data['currency_to'],
                                                            margins=walletPercent)
    amount_to -= commission_amount
    await state.update_data(amount_to=amount_to)
    text = botMessages['checkTheCorrectTransaction'].format(
        name_net=state_data['currency_to'],
        address=state_data['user_requisites'],
        amount_from=minimal_amount,
        currency_from=state_data['currency_from'],
        currency_to=state_data['currency_to'],
        amount_to=amount_to
    )
    await callback.message.edit_text(text=text,
                                     reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                                                  sizes=(2,),
                                                                                  back='main',
                                                                                  back_name=backLexicon[
                                                                                      'cancelLexicon'],
                                                                                  **getSum))
    await state.set_state(FSMFiatCrypto.check_validate_sum)


@router.callback_query(UserCallbackFactory.filter(F.page == 'getSum'),
                       StateFilter(FSMCryptoFiat.check_validate_sum, FSMCryptoCrypto.check_validate_sum))
async def receipt_verification_CC_CF(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    state_data: dict[str: str] = await state.get_data()
    file_path: str = await QRCodeService.create_crypto_payment_qrcode(
        amount=state_data['amount_from'],
        crypto_currency=state_data['typeCrypto'],
        address=state_data['work_walletRequisites'],
        description=f'UserId-{callback.from_user.id}'
    )
    photo: FSInputFile = FSInputFile(file_path)
    await callback.message.delete()
    await bot.send_photo(chat_id=callback.from_user.id, photo=photo)
    text = botMessages['receiptVerification'].format(
        amount_to=state_data['amount_to'],
        currency_to=state_data['currency_to'],
        amount_from=state_data['amount_from'],
        type_transaction=state_data['WalletCurrency'],
        work_wallet=state_data['work_walletRequisites']
    )
    await bot.send_message(chat_id=callback.from_user.id,
                           text=text,
                           reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                                        back='main',
                                                                        back_name=backLexicon[
                                                                            'cancelLexicon'],
                                                                        **receiptVerification))
    await StateService.set_states(state_name='money_sent', state_data=state_data, state=state)
    await QRCodeService.delete_file(file_name=file_path)


@router.callback_query(UserCallbackFactory.filter(F.page == 'getSum'), StateFilter(FSMFiatCrypto.check_validate_sum))
async def receipt_verification_FC(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(FSMFiatCrypto.money_sent)
    state_data: dict[str: str] = await state.get_data()
    rub_amount_from = await CryptoCheck.transaction_amount(amount=state_data['amount_from'],
                                                           currency_to='RUB',
                                                           currency_from=state_data['currency_from'])
    await state.update_data(amount_from=rub_amount_from)
    text = botMessages['receiptVerification'].format(
        amount_to=state_data['amount_to'],
        currency_to=state_data['currency_to'],
        amount_from=rub_amount_from,
        type_transaction=state_data['WalletCurrency'],
        work_wallet=state_data['work_walletRequisites']
    )
    await callback.message.edit_text(text=text,
                                     reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                                                  back='main',
                                                                                  back_name=backLexicon[
                                                                                      'cancelLexicon'],
                                                                                  **receiptVerification))


@router.callback_query(UserCallbackFactory.filter(F.page == 'sent'),
                       StateFilter(FSMFiatCrypto.money_sent, FSMCryptoFiat.money_sent,
                                   FSMCryptoCrypto.money_sent))
async def create_mission_FC(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    state_data: dict[str: str] = await state.get_data()
    walletCurrency: str = state_data['WalletCurrency']
    currency_to: str = state_data['currency_to']
    wallet_requisites: str = state_data['user_requisites']
    wallet_id: int = state_data['walletId']
    amount_to: float = state_data['amount_to']
    amount_from: int = state_data['amount_from']
    work_wallet: str = state_data['work_walletRequisites']
    user_obj: Users = await UserAPI.select_user(callback.from_user.id)
    admin_obj: Users | None = await UserService.random_admin()
    type_trans: str = state_data['typeTransaction'].replace('-', '/')
    mission_obj: Submissions = await SubmissionsAPI.add_application(user_id=user_obj.Id,
                                                                    address_id=wallet_id,
                                                                    currency_to=currency_to,
                                                                    amount_to=amount_to,
                                                                    amount_from=amount_from,
                                                                    typeTrans=type_trans,
                                                                    address_user=wallet_requisites)
    await callback.message.answer(text=botMessages['createMission'].format(
        mission_id=mission_obj.Id,
        user_requisites=wallet_requisites,
        amount=amount_to,
        currency_to=currency_to
    ),
        reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                     back='main',
                                                     back_name=backLexicon['backMainMenu']))
    if admin_obj:
        sendMission_copy = {**sendMission, **revokeButton}
        await bot.send_message(chat_id=admin_obj.UserId,
                               text=botMessages['sendMission'].format(
                                   currencyTo=currency_to,
                                   walletCurrency=walletCurrency,
                                   missionID=mission_obj.Id,
                                   adminID=mission_obj.AdminId,
                                   userID=callback.from_user.id,
                                   workWallet=work_wallet,
                                   userRequisites=wallet_requisites,
                                   amountFrom=amount_from,
                                   amountTo=amount_to,
                                   statusMission=changeStatus[mission_obj.Status.lower()].upper(),
                                   dataTime=mission_obj.DateTime
                               ),
                               reply_markup=await Factories.create_fac_mission(MissionCallbackFactory,
                                                                               mission_id=mission_obj.Id,
                                                                               back='main',
                                                                               back_name=backLexicon['backMainMenu'],
                                                                               sizes=(2, 1),
                                                                               **sendMission_copy))
    await state.clear()


@router.callback_query(MissionCallbackFactory.filter(F.page.isdigit()))
@router.callback_query(MissionCallbackFactory.filter(F.page == 'information'))
async def information_mission(callback: CallbackQuery, callback_data: MissionCallbackFactory) -> None:
    mission_obj, wallet_obj, user = await SubmissionsAPI.get_mission_data(mission_id=callback_data.mission_id)
    delete_mission = {
        f'delete-{mission_obj.Id}': revokeButton['revoke']
    } if mission_obj.Status == 'WAIT' else {}
    await callback.message.edit_text(text=botMessages['informationMissionUser'].format(
        missionID=mission_obj.Id,
        adminID=mission_obj.AdminId,
        userRequisites=mission_obj.AddressUser,
        workWallet=wallet_obj.Address,
        amountFrom=mission_obj.AmountFrom,
        NameNet=wallet_obj.NameNet,
        amountTo=mission_obj.AmountTo,
        currencyTo=mission_obj.CurrencyTo,
        statusMission=changeStatus[mission_obj.Status.lower()].upper(),
        dataTime=mission_obj.DateTime,
    ),
        reply_markup=await Factories.create_fac_mission(MissionCallbackFactory,
                                                        mission_id=callback_data.mission_id,
                                                        back='missions',
                                                        back_name=backLexicon['backMission'],
                                                        sizes=(1, 1),
                                                        **delete_mission))


@router.callback_query(MissionCallbackFactory.filter(F.page.regexp(r'^delete-\d+$')))
async def delete_user_mission(callback: CallbackQuery, callback_data: MissionCallbackFactory) -> None:
    mission_id: str = callback_data.page.split('-')[1]
    await SubmissionsAPI.delete_mission_by_id(mission_id=int(mission_id))
    await callback.message.edit_text(text=botMessages['deleteMissionUser'].format(missionID=mission_id),
                                     reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                                                  back_page=callback_data.page,
                                                                                  back='profile',
                                                                                  sizes=(3,),
                                                                                  **listMissions))


@router.callback_query(UserCallbackFactory.filter(F.page == 'verify'))
async def user_verify(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(FSMVerify.get_photo)
    await callback.message.delete()
    verif_number: int = await UserService.verif_number()
    photo: FSInputFile = FSInputFile('src/img/verifExample.png')
    await callback.message.answer_photo(photo=photo, caption=botMessages['verif'].format(
        verifNumber=verif_number
    ))
    await state.update_data(verifNumber=verif_number)
