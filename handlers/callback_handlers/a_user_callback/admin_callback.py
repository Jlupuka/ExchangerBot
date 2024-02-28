from aiogram import Router
from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from databaseAPI.commands.userCommands.admin_commands import AdminAPI
from databaseAPI.commands.walletAddress_commands import WalletAPI
from databaseAPI.commands.submissions_commands import SubmissionsAPI
from databaseAPI.tables import WalletAddress
from filters.filters import IsAdmin, IsToken
from lexicon.lexicon import botMessages, startCallbackAdmin, settingsMenu, workType, missions, walletsMenu, \
    checkCorrectAddWallet, successfullyMessage, addressMenu, sureLexicon, addressDelete, errorLexicon, addressEdit, \
    statusWork, backLexicon

from keyboard.keyboard_factory import create_fac_menu
from factories.factory import AdminCallbackFactory

from services import logger
from services.walletService import get_wallets, get_size_wallet, preprocess_wallets
from states.states import FSMAddWallet, FSMPercentEdit

router: Router = Router()


@router.callback_query(AdminCallbackFactory.filter(F.page == 'main'), IsAdmin())
async def start_handler_admin(callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        text=botMessages['startMessageAdmin'],
        reply_markup=await create_fac_menu(AdminCallbackFactory,
                                           sizes=(2, 2),
                                           back_page=callback_data.page,
                                           **startCallbackAdmin)
    )


@router.callback_query(AdminCallbackFactory.filter(F.page == 'statistics'), IsAdmin())
async def statistics_handler(callback: CallbackQuery, callback_data: AdminCallbackFactory) -> None:
    logger.info(callback_data)
    await callback.message.edit_text(text=botMessages['statisticTextUser'],
                                     reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                        back=callback_data.back_page))


@router.callback_query(AdminCallbackFactory.filter(F.page.in_({'settings', 'workType'})), IsAdmin())
async def settings_handler(callback: CallbackQuery, callback_data: AdminCallbackFactory) -> None:
    admin_work_type: bool = await AdminAPI.get_workType(user_id=callback.from_user.id)
    if callback_data.page == 'workType':
        admin_work_type = await AdminAPI.update_workType(user_id=callback.from_user.id, work_type=admin_work_type)
    count_wait_missions: int = len(await SubmissionsAPI.get_all_missions_wait(status='WAIT'))
    count_wallet: int = await WalletAPI.count_wallets()
    count_admin_work: int = await AdminAPI.count_adminsWork()
    buttons: dict[str: str] = settingsMenu.copy()
    buttons['workType'] = workType[not admin_work_type]
    if admin_work_type:
        buttons.update(**missions)
    await callback.message.edit_text(text=botMessages['settingsText'].format(workType=workType[admin_work_type],
                                                                             countMissions=count_wait_missions,
                                                                             countWallets=count_wallet,
                                                                             adminsWork=count_admin_work),
                                     reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                        back_page=callback_data.back_page,
                                                                        back='main',
                                                                        sizes=(1, 2, 1) if admin_work_type else (2, 1),
                                                                        **buttons))


@router.callback_query(AdminCallbackFactory.filter(F.page == 'wallets'), IsAdmin())
async def wallets_handler(callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext) -> None:
    await state.clear()
    wallets_dict: dict[str: str] = await get_wallets(func=WalletAPI.get_all_name_net_wallets)
    wallets_menu: dict[str: str] = walletsMenu.copy()
    if wallets_dict:
        wallets_menu = {**{key: wallets_dict[key] for key in sorted(wallets_dict)}, **wallets_menu}
    size: tuple[int, ...] = await get_size_wallet(len_wallet=len_wallet, count_any_button=2) if (len_wallet :=
                                                                                                 len(wallets_dict)
                                                                                                 ) > 1 else (1, 1, 1)
    await callback.message.edit_text(text=botMessages['walletsMenu'],
                                     reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                        back_page=callback_data.page,
                                                                        back='settings',
                                                                        sizes=size,
                                                                        **wallets_menu))


@router.callback_query(AdminCallbackFactory.filter(F.page == 'addWallet'), IsAdmin())
async def add_wallet_handler(callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(FSMAddWallet.currency_to)
    await callback.message.edit_text(text=botMessages['addWallet'],
                                     reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                        back=callback_data.back_page))


@router.callback_query(AdminCallbackFactory.filter(F.page == 'no'), StateFilter(FSMAddWallet.type_wallet), IsAdmin())
async def repeat_add_wallet(callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(FSMAddWallet.currency_to)
    await callback.message.edit_text(text=botMessages['addWallet'],
                                     reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                        back=callback_data.back_page))


@router.callback_query(AdminCallbackFactory.filter(F.page == 'repeat'), IsAdmin())
async def repeat_get_crypto_address(callback: CallbackQuery, state: FSMContext) -> None:
    now_state: str = await state.get_state()
    text = 'aaa'
    if now_state == FSMAddWallet.type_wallet:
        text: str = botMessages['getNameNet']
        await state.set_state(FSMAddWallet.address)
    elif now_state == FSMAddWallet.address:
        text: str = botMessages['addWallet']
        await state.set_state(FSMAddWallet.currency_to)
    await callback.message.edit_text(text=text,
                                     reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                        back='wallets',
                                                                        back_name=backLexicon['backLexicon']))


@router.callback_query(AdminCallbackFactory.filter(F.page.in_({'crypto', 'rub'})),
                       StateFilter(FSMAddWallet.type_wallet),
                       IsAdmin())
async def check_add_wallet_data(callback: CallbackQuery, callback_data: AdminCallbackFactory,
                                state: FSMContext) -> None:
    await state.update_data(walletType=callback_data.page)
    await state.set_state(FSMAddWallet.check_correct)
    state_data: dict[str: str] = await state.get_data()
    name_net: str = state_data['currency_to']
    address: str = state_data['address']
    wallet_type: str = callback_data.page.upper()
    await callback.message.edit_text(text=botMessages['checkDataAddWallet'].format(nameNet=name_net,
                                                                                   address=address,
                                                                                   walletType=wallet_type),
                                     reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                        back='wallets',
                                                                        back_name=backLexicon['backLexicon'],
                                                                        sizes=(2, 1),
                                                                        **checkCorrectAddWallet))


@router.callback_query(AdminCallbackFactory.filter(F.page == 'yes'), StateFilter(FSMAddWallet.check_correct), IsAdmin())
async def add_wallet_handler(callback: CallbackQuery, state: FSMContext) -> None:
    state_data: dict[str: str] = await state.get_data()
    name_net: str = state_data['currency_to'].upper()
    address: str = state_data['address']
    wallet_type: str = state_data['walletType'].upper()
    response = await WalletAPI.add_wallet(name_net=name_net, address=address, type_wallet=wallet_type)
    if response is None:
        await callback.message.edit_text(text=successfullyMessage['addWallet'].format(nameNet=name_net,
                                                                                      address=address,
                                                                                      walletType=wallet_type),
                                         reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                            back='wallets',
                                                                            back_name=backLexicon['backLexicon']))
    else:
        await callback.message.edit_text(text=errorLexicon['WalletExist'].format(nameNet=name_net,
                                                                                 address=address,
                                                                                 walletType=wallet_type),
                                         reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                            back='wallets',
                                                                            back_name=backLexicon['backLexicon']))
    await state.clear()


@router.callback_query(AdminCallbackFactory.filter(), IsToken(AdminCallbackFactory), IsAdmin())
async def print_wallets(callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext) -> None:
    await state.clear()
    await state.update_data(name_net=callback_data.page)
    wallets_list: list[tuple[int, str]] = await WalletAPI.get_wallets_data(name_net=callback_data.page.upper())
    text, wallets_dict = await preprocess_wallets(wallets=wallets_list)
    await state.update_data(**wallets_dict)
    await callback.message.edit_text(text=text,
                                     reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                        back='wallets',
                                                                        back_page=callback_data.page,
                                                                        sizes=await get_size_wallet(
                                                                            len_wallet=len(wallets_dict),
                                                                            count_any_button=1),
                                                                        **wallets_dict))


@router.callback_query(AdminCallbackFactory.filter(F.page.regexp(r'^id-\d+$')), IsAdmin())
async def address_menu(callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext) -> None:
    await state.update_data(token=callback_data.page)
    state_data = await state.get_data()
    await callback.message.edit_text(text=botMessages['addressMenu'],
                                     reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                        back=state_data['name_net'],
                                                                        back_page=callback_data.page,
                                                                        sizes=(2, 1),
                                                                        **addressMenu))


@router.callback_query(AdminCallbackFactory.filter(F.page == 'deleteAddress'), StateFilter(None), IsAdmin())
async def delete_address_menu(callback: CallbackQuery, callback_data: AdminCallbackFactory) -> None:
    sureDelete_copy = sureLexicon.copy()
    sureDelete_copy[callback_data.back_page] = sureDelete_copy.pop('no')
    await callback.message.edit_text(text=botMessages['sureDelete'],
                                     reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                        sizes=(2,),
                                                                        **sureDelete_copy))


@router.callback_query(AdminCallbackFactory.filter(F.page == 'yes'), StateFilter(None), IsAdmin())
async def delete_address(callback: CallbackQuery, state: FSMContext) -> None:
    state_data = await state.get_data()
    address_id = int(state_data['token'].split('-')[1])
    await WalletAPI.delete_wallet(wallet_id=address_id)
    await callback.message.edit_text(text=botMessages['deleteAddress'].format(wallet=state_data[state_data['token']]),
                                     reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                        **addressDelete))


@router.callback_query(AdminCallbackFactory.filter(F.page.in_({'statusWork', 'addressEdit'})),
                       StateFilter(None, FSMPercentEdit.check_percent), IsAdmin())
async def address_edit(callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext) -> None:
    await state.set_state(None)
    state_data = await state.get_data()
    wallet_id = int(state_data['token'].split('-')[1])
    wallet_data: WalletAddress = await WalletAPI.get_wallet_data(wallet_id=wallet_id)
    status_work = wallet_data.Status
    percent = wallet_data.Percent
    address = wallet_data.Address
    address_edit_copy = addressEdit.copy()
    if callback_data.page == 'statusWork':
        status_work = await WalletAPI.update_work_type_wallet(wallet_id=wallet_id, work_type=not status_work)
    address_edit_copy['statusWork'] = statusWork[not status_work]
    await callback.message.edit_text(text=botMessages['addressEdit'].format(address=address,
                                                                            percent=percent,
                                                                            workType=statusWork[status_work]),
                                     reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                        back_page=callback_data.back_page,
                                                                        back=state_data['token'],
                                                                        sizes=(2, 1),
                                                                        **address_edit_copy))


@router.callback_query(AdminCallbackFactory.filter(F.page.in_({'percentEdit', 'repeatGetPercent'})),
                       StateFilter(None, FSMPercentEdit.check_percent), IsAdmin())
async def percent_edit(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(FSMPercentEdit.get_percent)
    state_data: dict[str: str] = await state.get_data()
    back_page: str = state_data['token']
    await callback.message.edit_text(text=botMessages['percentEdit'],
                                     reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                        back=back_page,
                                                                        back_name=backLexicon['cancelLexicon']))


@router.callback_query(AdminCallbackFactory.filter(F.page == 'yes'),
                       StateFilter(FSMPercentEdit.check_percent), IsAdmin())
async def update_percent_wallet(callback: CallbackQuery,
                                state: FSMContext) -> None:
    await state.set_state(None)
    state_data = await state.get_data()
    wallet_id = int(state_data['token'].split('-')[1])
    percent = state_data['percent']
    await WalletAPI.update_percent(wallet_id=wallet_id, percent=percent)
    await callback.message.edit_text(text=botMessages['completedEditPercent'].format(percent=percent),
                                     reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                        back=state_data['token'],
                                                                        back_name=backLexicon['backLexicon']))
