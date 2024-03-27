from typing import NoReturn

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from databaseAPI.commands.submissions_commands import SubmissionsAPI
from databaseAPI.commands.userCommands.admin_commands import AdminAPI
from databaseAPI.commands.walletAddress_commands import WalletAPI
from databaseAPI.models import Users, Submissions
from databaseAPI.models.models import Statuses
from factories.factory import AdminCallbackFactory
from filters.filters import IsAdmin
from keyboard.keyboard_factory import Factories
from lexicon.lexicon import settingsMenu, workType, missions, botMessages

router: Router = Router()


@router.callback_query(
    AdminCallbackFactory.filter(F.page.in_({"settings", "workType"})), IsAdmin()
)
async def settings_handler(
    callback: CallbackQuery,
    callback_data: AdminCallbackFactory,
    state: FSMContext,
    user: Users,
) -> NoReturn:
    await state.clear()
    admin_work_type: bool = user.WorkType
    if callback_data.page == "workType":
        admin_work_type: bool = (
            await AdminAPI.update_user(
                user_id=callback.from_user.id, WorkType=not admin_work_type
            )
        ).WorkType
    count_wait_missions: int = len(
        await SubmissionsAPI.select_missions(
            False, None, 0, *(Submissions,), Status=Statuses.wait
        )
    )
    count_wallet: int = await WalletAPI.count_wallets()
    count_admin_work: int = await AdminAPI.count_adminsWork()
    buttons: dict[str:str] = settingsMenu.copy()
    buttons["workType"] = workType[not admin_work_type]
    if admin_work_type:
        buttons.update(**missions)
    await callback.message.edit_text(
        text=botMessages["settingsText"].format(
            workType=workType[admin_work_type],
            countMissions=count_wait_missions,
            countWallets=count_wallet,
            adminsWork=count_admin_work,
        ),
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory,
            back_page="settings",
            back="main",
            sizes=(1, 2, 1) if admin_work_type else (2, 1),
            **buttons,
        ),
    )
