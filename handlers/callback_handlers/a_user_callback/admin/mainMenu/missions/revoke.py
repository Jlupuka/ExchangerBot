from aiogram import Router, Bot
from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from databaseAPI.commands.submissions_commands import SubmissionsAPI
from databaseAPI.models import Submissions, Users
from filters.filters import IsAdmin
from lexicon.lexicon import (
    botMessages,
    errorLexicon,
    backLexicon,
    revokeMission,
)

from keyboard.keyboard_factory import Factories
from factories.factory import (
    AdminCallbackFactory,
    MissionCallbackFactory,
    UserCallbackFactory,
)
from states.states import FSMRevokeMission

router: Router = Router()


@router.callback_query(
    MissionCallbackFactory.filter(F.page == "revoke"), IsAdmin(checkAdminWork=True)
)
async def check_revoke_mission(
    callback: CallbackQuery,
    callback_data: MissionCallbackFactory,
    state: FSMContext,
    bot: Bot,
) -> None:
    if (photo_id := (await state.get_data()).get("photoId")) is not None:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=photo_id)
        await state.update_data(photoId=None)
    mission_obj: Submissions = (
        await SubmissionsAPI.select_missions(
            False, None, 0, *(Submissions,), Id=callback_data.mission_id
        )
    )[0]
    if mission_obj.AdminId is None or mission_obj.AdminId == callback.from_user.id:
        await state.set_state(FSMRevokeMission.sure)
        await state.update_data(typeRevoke="SIMPLE")
        await callback.message.edit_text(
            text=botMessages["sureRevoke"].format(missionID=callback_data.mission_id),
            reply_markup=await Factories.create_fac_mission(
                MissionCallbackFactory,
                mission_id=callback_data.mission_id,
                back=callback_data.mission_id,
                back_name=backLexicon["backLexicon"],
                sizes=(1, 1),
                **revokeMission,
            ),
        )
    else:
        await callback.answer(text=errorLexicon["anotherAdminTakeMiss"])


@router.callback_query(
    MissionCallbackFactory.filter(F.page == "revokeWithMessage"),
    IsAdmin(checkAdminWork=True),
)
async def get_message_to_revoke(
    callback: CallbackQuery,
    callback_data: MissionCallbackFactory,
    state: FSMContext,
    bot: Bot,
) -> None:
    if (photo_id := (await state.get_data()).get("photoId")) is not None:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=photo_id)
        await state.update_data(photoId=None)
    mission_obj: Submissions = (
        await SubmissionsAPI.select_missions(
            False, None, 0, *(Submissions,), Id=callback_data.mission_id
        )
    )[0]
    if mission_obj.AdminId is None or mission_obj.AdminId == callback.from_user.id:
        await state.set_state(FSMRevokeMission.message)
        await state.update_data(
            missionID=callback_data.mission_id, messageID=callback.message.message_id
        )
        await callback.message.edit_text(
            text=botMessages["getMessageToRevoke"],
            reply_markup=await Factories.create_fac_mission(
                MissionCallbackFactory,
                mission_id=callback_data.mission_id,
                back=callback_data.mission_id,
            ),
        )
    else:
        await callback.answer(text=errorLexicon["anotherAdminTakeMiss"])


@router.callback_query(
    MissionCallbackFactory.filter(F.page == "YesRevokeMission"),
    StateFilter(FSMRevokeMission.sure),
    IsAdmin(checkAdminWork=True),
)
async def revoke_mission(
    callback: CallbackQuery,
    callback_data: MissionCallbackFactory,
    state: FSMContext,
    bot: Bot,
) -> None:
    state_data = await state.get_data()
    mission_obj, user = (
        await SubmissionsAPI.select_missions(
            False, None, 0, *(Submissions, Users), Id=callback_data.mission_id
        )
    )[0]
    type_revoke = state_data["typeRevoke"]
    message = state_data.get("messageRevoke", None)
    await callback.message.edit_text(
        text=(
            botMessages["revokeSimpleA"]
            if type_revoke == "SIMPLE"
            else botMessages["revokeWithTextA"].format(messageRevoke=message)
        ),
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory, back="missions", back_name=backLexicon["backMission"]
        ),
    )
    await bot.send_message(
        chat_id=user.UserId,
        text=(
            botMessages["revokeSimpleU"].format(missionID=mission_obj.Id)
            if type_revoke == "SIMPLE"
            else botMessages["revokeWithTextU"].format(
                missionID=mission_obj.Id, messageRevoke=message
            )
        ),
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory, back="missions", back_name=backLexicon["backMission"]
        ),
    )
    await SubmissionsAPI.delete_mission_by_id(mission_id=mission_obj.Id)
    await state.clear()
