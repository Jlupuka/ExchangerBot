from typing import NoReturn

from aiogram import Router, Bot
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from databaseAPI.commands.submissions_commands import SubmissionsAPI
from filters.filters import IsAdmin
from lexicon.lexicon import (
    botMessages,
    errorLexicon,
    backLexicon,
    changeStatus,
    checkMark,
    informationMissionUser,
)

from keyboard.keyboard_factory import Factories
from factories.factory import MissionCallbackFactory
from services import logger

router: Router = Router()


@router.callback_query(
    MissionCallbackFactory.filter(
        F.page.in_({"wait", "accepted", "completed", "changeStatus"})
    ),
    IsAdmin(checkAdminWork=True),
)
async def get_missions(
    callback: CallbackQuery,
    callback_data: MissionCallbackFactory,
    state: FSMContext,
    bot: Bot,
) -> NoReturn:
    if (photo_id := (await state.get_data()).get("photoId")) is not None:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=photo_id)
        await state.update_data(photoId=None)
    if callback_data.page != callback_data.back_page:
        mission_obj, _, user = await SubmissionsAPI.get_mission_data(
            mission_id=callback_data.mission_id
        )
        if mission_obj.AdminId is None or mission_obj.AdminId == callback.from_user.id:
            oldStatus = mission_obj.Status
            if callback_data.page != "changeStatus":
                await SubmissionsAPI.update_mission_status(
                    submission_id=callback_data.mission_id,
                    status=callback_data.page.upper(),
                )
                mission_obj.Status = callback_data.page.upper()
            copy_changeStatus = changeStatus.copy()
            copy_changeStatus[mission_obj.Status.lower()] = (
                f'{mission_obj.Status} {checkMark["yes"]}'
            )
            await callback.message.edit_text(
                text=botMessages["changeStatus"].format(
                    missionID=mission_obj.Id, statusMission=mission_obj.Status
                ),
                reply_markup=await Factories.create_fac_mission(
                    MissionCallbackFactory,
                    mission_id=callback_data.mission_id,
                    back=callback_data.mission_id,
                    back_name=backLexicon["backLexicon"],
                    back_page=callback_data.page,
                    sizes=(3, 1),
                    **copy_changeStatus,
                ),
            )
            if callback_data.page in {
                "wait",
                "accepted",
                "completed",
            }:  # Notifying the user
                await bot.send_message(
                    chat_id=user.UserId,
                    text=botMessages["changeStatusUser"].format(
                        missionID=mission_obj.Id,
                        statusMission=changeStatus[mission_obj.Status.lower()].upper(),
                    ),
                    reply_markup=await Factories.create_fac_mission(
                        MissionCallbackFactory,
                        mission_id=callback_data.mission_id,
                        back="main",
                        back_name=backLexicon["backMainMenu"],
                        sizes=(1, 1),
                        **informationMissionUser,
                    ),
                )
                await SubmissionsAPI.update_admin_id(
                    submission_id=mission_obj.Id,
                    admin_id=(
                        None if callback_data.page == "wait" else callback.from_user.id
                    ),
                )
                logger.info(
                    "userID=%s, adminID=%s, oldStatus=%s, newStatus=%s",
                    user.UserId,
                    callback.from_user.id,
                    oldStatus,
                    mission_obj.Status,
                )
        elif mission_obj.AdminId != callback.from_user.id:
            copy_changeStatus = changeStatus.copy()
            copy_changeStatus[mission_obj.Status.lower()] = (
                f'{mission_obj.Status} {checkMark["yes"]}'
            )
            await callback.message.edit_text(
                text=errorLexicon["anotherAdminTakeMiss"],
                reply_markup=await Factories.create_fac_mission(
                    MissionCallbackFactory,
                    mission_id=callback_data.mission_id,
                    back=callback_data.mission_id,
                    back_name=backLexicon["backLexicon"],
                    back_page=callback_data.page,
                    sizes=(3, 1),
                    **copy_changeStatus,
                ),
            )

    await callback.answer()
