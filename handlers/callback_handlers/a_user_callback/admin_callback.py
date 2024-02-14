from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from databaseAPI.commands.userCommands.admin_commands import get_workType, count_adminsWork, update_workType
from databaseAPI.commands.walletAddress_commands import count_wallets
from databaseAPI.commands.submissions_commands import get_all_missions_wait
from filters.filters import IsAdmin
from lexicon.lexicon import botMessages, startCallbackAdmin, settingsMenu, workType, missions

from keyboard.keyboard_factory import create_fac_menu
from factories.factory import AdminCallbackFactory

from magic_filter import F

from services import logger

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
                                                                        back_page=callback_data.page,
                                                                        back='main',
                                                                        sizes=(1, 2, 1) if admin_work_type else (2, 1),
                                                                        **buttons))


@router.callback_query(AdminCallbackFactory.filter(F.page == 'wallets'), IsAdmin())
async def wallets_handler(callback: CallbackQuery, callback_data: AdminCallbackFactory) -> None:
    pass