from aiogram import Router, Bot
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from databaseAPI.commands.submissions_commands import SubmissionsAPI
from databaseAPI.commands.userCommands.user_commands import UserAPI
from databaseAPI.commands.walletAddress_commands import WalletAPI
from databaseAPI.tables import WalletAddress, Submissions, Users
from filters.filters import IsToken
from lexicon.lexicon import botMessages, startCallbackUser, profileUser, listMissionsUser, choiceMethod, \
    backLexicon, minSum, receiptVerification, getSum, fiatOrCrypto, sendMission

from keyboard.keyboard_factory import create_fac_menu, create_fac_mission
from factories.factory import UserCallbackFactory, MissionCallbackFactory

from magic_filter import F

from services import logger
from services.cryptoService import CryptoCheck, min_sum
from services.userService import UserService
from services.walletService import get_wallets, get_size_wallet, random_wallet
from states.states import FSMFiatCrypto, FSMCryptoFiat, FSMCryptoCrypto

router: Router = Router()


@router.callback_query(UserCallbackFactory.filter(F.page == 'main'))
async def main_handler(callback: CallbackQuery, state: FSMContext, callback_data: UserCallbackFactory) -> None:
    await state.clear()
    await callback.message.edit_text(
        text=botMessages['startMessageUser'],
        reply_markup=await create_fac_menu(UserCallbackFactory,
                                           back_page=callback_data.page,
                                           sizes=(2, 1, 2),
                                           **startCallbackUser)
    )


@router.callback_query(UserCallbackFactory.filter(F.page == 'info'))
async def info_handler(callback: CallbackQuery) -> None:
    # TODO: Сделать информационный текст о боте
    await callback.answer()


@router.callback_query(UserCallbackFactory.filter(F.page == 'profile'))
async def profile_handler(callback: CallbackQuery, callback_data: UserCallbackFactory) -> None:
    await callback.message.edit_text(text=botMessages['profileTextUser'],
                                     reply_markup=await create_fac_menu(UserCallbackFactory,
                                                                        back_page=callback_data.page,
                                                                        back='main',
                                                                        sizes=(2,), **profileUser))


@router.callback_query(UserCallbackFactory.filter(F.page == 'statistics'))
async def statistics_handler(callback: CallbackQuery, callback_data: UserCallbackFactory) -> None:
    await callback.message.edit_text(text=botMessages['statisticTextUser'],
                                     reply_markup=await create_fac_menu(UserCallbackFactory,
                                                                        back_page='main',
                                                                        back=callback_data.back_page))


@router.callback_query(UserCallbackFactory.filter(F.page == 'missions'))
async def missions_handler(callback: CallbackQuery, callback_data: UserCallbackFactory) -> None:
    await callback.message.edit_text(text=botMessages['missionsTextUser'],
                                     reply_markup=await create_fac_menu(UserCallbackFactory,
                                                                        back_page=callback_data.page,
                                                                        back='profile',
                                                                        sizes=(3,),
                                                                        **listMissionsUser))


@router.callback_query(UserCallbackFactory.filter(F.page == 'accepted'))
async def accepted_missions_handler(callback: CallbackQuery, callback_data: UserCallbackFactory) -> None:
    # TODO: Реализовать запрос к БД, для получения данных по заявкам. Так же сделать обработку\очистку
    #  данных под бота тг
    await callback.message.edit_text(text=botMessages['informationMissions'],
                                     reply_markup=await create_fac_menu(UserCallbackFactory,
                                                                        back_page='missions',
                                                                        back=callback_data.back_page,
                                                                        sizes=(3,),
                                                                        **listMissionsUser))


@router.callback_query(UserCallbackFactory.filter(F.page == 'completed'))
async def completed_missions_handler(callback: CallbackQuery, callback_data: UserCallbackFactory) -> None:
    # TODO: Реализовать запрос к БД, для получения данных по заявкам. Так же сделать обработку\очистку
    #  данных под бота тг
    await callback.message.edit_text(text=botMessages['informationMissions'],
                                     reply_markup=await create_fac_menu(UserCallbackFactory,
                                                                        back_page='missions',
                                                                        back=callback_data.back_page,
                                                                        sizes=(3,),
                                                                        **listMissionsUser))


@router.callback_query(UserCallbackFactory.filter(F.page == 'waiting'))
async def waiting_missions_handler(callback: CallbackQuery, callback_data: UserCallbackFactory) -> None:
    # TODO: Реализовать запрос к БД, для получения данных по заявкам. Так же сделать обработку\очистку
    #  данных под бота тг
    await callback.message.edit_text(text=botMessages['informationMissions'],
                                     reply_markup=await create_fac_menu(UserCallbackFactory,
                                                                        back_page='missions',
                                                                        back=callback_data.back_page,
                                                                        sizes=(3,),
                                                                        **listMissionsUser))


@router.callback_query(UserCallbackFactory.filter(F.page == 'rub-crypto'))
async def choice_rub_crypto(callback: CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(FSMFiatCrypto.currency_to)
    wallets_dict: dict[str: str] = await get_wallets(func=WalletAPI.get_all_name_net_by_type, type_wallet='CRYPTO')
    size: tuple[int, ...] = await get_size_wallet(len_wallet=len(wallets_dict), count_any_button=1)
    await callback.message.edit_text(text=botMessages['choiceToken'].format(typeWallet=fiatOrCrypto['crypto']),
                                     reply_markup=await create_fac_menu(UserCallbackFactory,
                                                                        back_page=callback_data.page,
                                                                        back=callback_data.back_page,
                                                                        sizes=size,
                                                                        **wallets_dict))


@router.callback_query(UserCallbackFactory.filter(), IsToken(UserCallbackFactory),
                       StateFilter(FSMFiatCrypto.currency_to))
async def get_wallet(callback: CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext) -> None:
    await state.update_data(currency_to=callback_data.page.upper())
    logger.debug(await state.get_data())
    await state.set_state(FSMFiatCrypto.requisites)
    await callback.message.edit_text(text=botMessages['getAddressCrypto'],
                                     reply_markup=await create_fac_menu(UserCallbackFactory,
                                                                        back=callback_data.back_page,
                                                                        back_page='main'))


@router.callback_query(UserCallbackFactory.filter(F.page.in_({'repeat', 'no'})),
                       StateFilter(FSMFiatCrypto.check_validate))
async def repeat_get_wallet(callback: CallbackQuery, state: FSMContext) -> None:
    logger.debug(await state.get_data())
    await state.set_state(FSMFiatCrypto.requisites)
    await callback.message.edit_text(text=botMessages['getAddressCrypto'],
                                     reply_markup=await create_fac_menu(UserCallbackFactory,
                                                                        back='rub-crypto',
                                                                        back_page='main'))


@router.callback_query(UserCallbackFactory.filter(F.page == 'yes'),
                       StateFilter(FSMFiatCrypto.check_validate, FSMFiatCrypto.get_sum))
async def choice_method_get_sum(callback: CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext) -> None:
    await state.set_state(FSMFiatCrypto.type_fiat)
    wallets_dict: dict[str: str] = await get_wallets(func=WalletAPI.get_all_name_net_by_type, type_wallet='RUB')
    size: tuple[int, ...] = await get_size_wallet(len_wallet=len(wallets_dict), count_any_button=1)
    await callback.message.edit_text(text=botMessages['choiceToken'].format(typeWallet=fiatOrCrypto['fiat']),
                                     reply_markup=await create_fac_menu(UserCallbackFactory,
                                                                        back_page=callback_data.page,
                                                                        back='main',
                                                                        sizes=size,
                                                                        **wallets_dict))


@router.callback_query(UserCallbackFactory.filter(), IsToken(UserCallbackFactory), StateFilter(FSMFiatCrypto.type_fiat))
async def save_type_fiat_transaction(callback: CallbackQuery,
                                     callback_data: UserCallbackFactory,
                                     state: FSMContext) -> None:
    await state.set_state(FSMFiatCrypto.method)
    await state.update_data(typeFiat=callback_data.page.upper())
    await callback.message.edit_text(text=botMessages['choiceMethod'],
                                     reply_markup=await create_fac_menu(UserCallbackFactory,
                                                                        back='main',
                                                                        sizes=(3, 1),
                                                                        back_name=backLexicon['cancelLexicon'],
                                                                        **choiceMethod))


@router.callback_query(UserCallbackFactory.filter(F.page.in_({'rub', 'usd', 'repeatGetSum'})),
                       StateFilter(FSMFiatCrypto.method, FSMFiatCrypto.check_validate_sum))
async def rub_usd_method(callback: CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext) -> None:
    if callback_data.page != 'repeatGetSum':
        await state.update_data(currency_from=callback_data.page.upper())
    await state.set_state(FSMFiatCrypto.get_sum)
    state_data: dict[str: str] = await state.get_data()
    minimal_amount = min_sum
    work_wallet: WalletAddress = await random_wallet(name_net=state_data['typeFiat'])
    if state_data['currency_from'] != 'RUB':
        minimal_amount = await CryptoCheck.minimal_summa(minSum=min_sum,
                                                         currency_to=state_data['currency_to'],
                                                         currency_from=state_data['currency_from'])
    currency_rate: float = await CryptoCheck.currency_rate(currency_from=state_data['currency_from'],
                                                           currency_to=state_data['currency_to'],
                                                           margins=work_wallet.Percent)
    await state.update_data(work_walletRequisites=work_wallet.Address,
                            walletPercent=work_wallet.Percent,
                            walletId=work_wallet.Id)
    await callback.message.edit_text(text=botMessages['getSum'].format(min_sum=minimal_amount,
                                                                       currency_from=state_data['currency_from'],
                                                                       currency_to=state_data['currency_to'],
                                                                       currency_rate=currency_rate),
                                     reply_markup=await create_fac_menu(UserCallbackFactory,
                                                                        back='yes',
                                                                        **minSum))


@router.callback_query(UserCallbackFactory.filter(F.page == 'minSum'), StateFilter(FSMFiatCrypto.get_sum))
async def check_the_correct_transaction(callback: CallbackQuery, state: FSMContext) -> None:
    state_data: dict[str: str] = await state.get_data()
    await state.set_state(FSMFiatCrypto.check_validate_sum)
    minimal_amount = min_sum
    if state_data['currency_from'] != 'RUB':
        minimal_amount = await CryptoCheck.minimal_summa(minSum=min_sum,
                                                         currency_to=state_data['currency_to'],
                                                         currency_from=state_data['currency_from'])
    await state.update_data(amount_from=minimal_amount)
    walletPercent = state_data['walletPercent']
    amount_to: float = await CryptoCheck.transaction_amount(amount=minimal_amount,
                                                            currency_from=state_data['currency_from'],
                                                            currency_to=state_data['currency_to'],
                                                            margins=walletPercent)
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
                                     reply_markup=await create_fac_menu(UserCallbackFactory,
                                                                        sizes=(2,),
                                                                        back='main',
                                                                        back_name=backLexicon['cancelLexicon'],
                                                                        **getSum))


@router.callback_query(UserCallbackFactory.filter(F.page == 'getSum'), StateFilter(FSMFiatCrypto.check_validate_sum))
async def receipt_verification(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(FSMFiatCrypto.money_sent)
    state_data: dict[str: str] = await state.get_data()
    rub_amount_from = await CryptoCheck.transaction_amount(amount=state_data['amount_from'],
                                                           currency_to='RUB',
                                                           currency_from=state_data['currency_from'])
    await state.update_data(amount_from=rub_amount_from)
    text = botMessages['receiptVerification'].format(
        amount_to=state_data['amount_to'],
        currency_to=state_data['currency_to'].upper(),
        amount_from=rub_amount_from,
        type_transaction='RUB',
        work_wallet=state_data['work_walletRequisites']
    )
    await callback.message.edit_text(text=text,
                                     reply_markup=await create_fac_menu(UserCallbackFactory,
                                                                        back='main',
                                                                        back_name=backLexicon['cancelLexicon'],
                                                                        **receiptVerification))


@router.callback_query(UserCallbackFactory.filter(F.page == 'sent'), StateFilter(FSMFiatCrypto.money_sent))
async def create_mission(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    state_data: dict[str: str] = await state.get_data()
    currency_to: str = state_data['currency_to']
    wallet_requisites: str = state_data['user_requisites']
    wallet_id: int = state_data['walletId']
    amount_to: float = state_data['amount_to']
    amount_from: int = state_data['amount_from']
    work_wallet: str = state_data['work_walletRequisites']
    user_obj: Users = await UserAPI.select_user(callback.from_user.id)
    admin_obj: Users | None = await UserService.random_admin()
    type_trans = None
    match await state.get_state():
        case FSMFiatCrypto.money_sent:
            type_trans = 'RUB/CRYPTO'
        case FSMCryptoFiat.money_sent:
            type_trans = 'CRYPTO/RUB'
        case FSMCryptoCrypto.money_sent:
            type_trans = 'CRYPTO/CRYPTO'
    mission_obj: Submissions = await SubmissionsAPI.add_application(user_id=user_obj.Id,
                                                                    address_id=wallet_id,
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
        reply_markup=await create_fac_menu(UserCallbackFactory,
                                           back='main',
                                           back_name=backLexicon['backMainMenu']))
    if admin_obj:
        copy_sendMission = sendMission.copy()
        copy_sendMission['changeStatus'] = sendMission['changeStatus'].format(
            statusMission=mission_obj.Status
        )
        await bot.send_message(chat_id=admin_obj.UserId,
                               text=botMessages['sendMission'].format(
                                   currencyTo=currency_to,
                                   missionID=mission_obj.Id,
                                   userID=callback.from_user.id,
                                   workWallet=work_wallet,
                                   userRequisites=wallet_requisites,
                                   amountFrom=amount_from,
                                   amountTo=amount_to,
                                   statusMission=mission_obj.Status,
                                   dataTime=mission_obj.DateTime
                               ),
                               reply_markup=await create_fac_mission(MissionCallbackFactory,
                                                                     mission_id=mission_obj.Id,
                                                                     back='main',
                                                                     back_name=backLexicon['backMainMenu'],
                                                                     sizes=(2, 1),
                                                                     **copy_sendMission))
    await state.clear()
