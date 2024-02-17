from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from databaseAPI.commands.userCommands.admin_commands import get_workType, count_adminsWork, update_workType
from databaseAPI.commands.walletAddress_commands import count_wallets, add_wallet
from databaseAPI.commands.submissions_commands import get_all_missions_wait
from filters.filters import IsAdmin
from lexicon.lexicon import botMessages, startCallbackAdmin, settingsMenu, workType, missions, walletsMenu, \
    checkCorrectAddWallet, successfullyMessage

from keyboard.keyboard_factory import create_fac_menu
from factories.factory import AdminCallbackFactory

from magic_filter import F

from services import logger
from services.wallets_service import get_wallets, get_size_wallet
from states.states import FSMAddWallet

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
    admin_work_type: bool = await get_workType(user_id=callback.from_user.id)
    if callback_data.page == 'workType':
        admin_work_type = await update_workType(user_id=callback.from_user.id, work_type=admin_work_type)
    count_wait_missions: int = len(await get_all_missions_wait(status='WAIT'))
    count_wallet: int = await count_wallets()
    count_admin_work: int = await count_adminsWork()
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
    wallets_dict: dict[str: str] = await get_wallets()
    wallets_menu: dict[str: str] = walletsMenu.copy()
    if wallets_dict:
        wallets_menu = {**{key: wallets_dict[key] for key in sorted(wallets_dict)}, **wallets_menu}
    size: tuple[int, ...] = await get_size_wallet(len_wallet=len_wallet) if (len_wallet :=
                                                                             len(wallets_dict)) > 1 else (1, 1, 1)
    await callback.message.edit_text(text=botMessages['walletsMenu'],
                                     reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                        back_page=callback_data.page,
                                                                        back='settings',
                                                                        sizes=size,
                                                                        **wallets_menu))


@router.callback_query(AdminCallbackFactory.filter(F.page == 'addWallet'), IsAdmin())
async def add_wallet_handler(callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(FSMAddWallet.crypto_to)
    await callback.message.edit_text(text=botMessages['addWallet'],
                                     reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                        back=callback_data.back_page))


@router.callback_query(AdminCallbackFactory.filter(F.page == 'no'), StateFilter(FSMAddWallet.type_wallet), IsAdmin())
async def repeat_add_wallet(callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(FSMAddWallet.crypto_to)
    await callback.message.edit_text(text=botMessages['addWallet'],
                                     reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                        back=callback_data.back_page))


@router.callback_query(AdminCallbackFactory.filter(F.page == 'repeat'), IsAdmin())
async def repeat_get_crypto_address(callback: CallbackQuery, callback_data: AdminCallbackFactory,
                                    state: FSMContext) -> None:
    now_state: str = await state.get_state()
    text = 'aaa'
    if now_state == FSMAddWallet.type_wallet:
        text: str = botMessages['getNameNet']
        await state.set_state(FSMAddWallet.address)
    elif now_state == FSMAddWallet.address:
        text: str = botMessages['addWallet']
        await state.set_state(FSMAddWallet.crypto_to)
    await callback.message.edit_text(text=text,
                                     reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                        back='wallets',
                                                                        back_name=botMessages['backWallets']))


@router.callback_query(AdminCallbackFactory.filter(F.page.in_({'crypto', 'rub'})),
                       StateFilter(FSMAddWallet.type_wallet),
                       IsAdmin())
async def check_add_wallet_data(callback: CallbackQuery, callback_data: AdminCallbackFactory,
                                state: FSMContext) -> None:
    await state.update_data(walletType=callback_data.page)
    await state.set_state(FSMAddWallet.check_correct)
    state_data: dict[str: str] = await state.get_data()
    name_net: str = state_data['crypto_to']
    address: str = state_data['address']
    wallet_type: str = callback_data.page.upper()
    await callback.message.edit_text(text=botMessages['checkDataAddWallet'].format(nameNet=name_net,
                                                                                   address=address,
                                                                                   walletType=wallet_type),
                                     reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                        back='wallets',
                                                                        back_name=botMessages['backWallets'],
                                                                        sizes=(2, 1),
                                                                        **checkCorrectAddWallet))


@router.callback_query(AdminCallbackFactory.filter(F.page == 'yes'), StateFilter(FSMAddWallet.check_correct), IsAdmin())
async def add_wallet_handler(callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext) -> None:
    state_data: dict[str: str] = await state.get_data()
    name_net: str = state_data['crypto_to'].upper()
    address: str = state_data['address']
    wallet_type: str = state_data['walletType'].upper()
    await add_wallet(name_net=name_net, address=address, type_wallet=wallet_type)
    await callback.message.edit_text(text=successfullyMessage['addWallet'].format(nameNet=name_net,
                                                                                  address=address,
                                                                                  walletType=wallet_type),
                                     reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                        back='wallets',
                                                                        back_name=botMessages['backWallets']))
    await state.clear()
