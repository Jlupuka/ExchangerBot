from typing import NoReturn, Sequence, Any

from aiogram import Router, exceptions, F
from aiogram.types import CallbackQuery
from sqlalchemy import RowMapping, Row

from databaseAPI.commands.submissions_commands import SubmissionsAPI
from databaseAPI.models import Submissions, Wallets
from databaseAPI.models.models import Statuses
from lexicon.lexicon import (
    botMessages,
    listMissions,
    errorLexicon,
    revokeButton,
    changeStatus,
    backLexicon,
)

from keyboard.keyboard_factory import Factories
from factories.factory import UserCallbackFactory, MissionCallbackFactory
from services.submissionService import SubmissionService

router: Router = Router()


@router.callback_query(UserCallbackFactory.filter(F.page == "missions"))
@router.callback_query(MissionCallbackFactory.filter(F.page == "missions"))
async def missions_handler(
    callback: CallbackQuery, callback_data: UserCallbackFactory
) -> NoReturn:
    await callback.message.edit_text(
        text=botMessages["missionsTextUser"],
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory,
            back_page=callback_data.page,
            back="profile",
            sizes=(3,),
            **listMissions,
        ),
    )


@router.callback_query(
    UserCallbackFactory.filter(F.page.in_({"wait", "accepted", "completed"}))
)
async def accepted_missions_handler(
    callback: CallbackQuery, callback_data: UserCallbackFactory
) -> NoReturn:
    try:
        mission_status: Statuses = Statuses[callback_data.page]
        missions_data: Sequence[Row | RowMapping | Any] = (
            await SubmissionsAPI.select_missions(
                True,
                callback.from_user.id,
                callback_data.mission_page,
                *(Submissions,),
                Status=mission_status,
            )
        )
        if missions_data:
            mission_count: int = len(missions_data)
            text, preprocess_mission = await SubmissionService.preprocess_mission_data(
                mission_data=missions_data
            )
            await callback.message.edit_text(
                text=text,
                reply_markup=await Factories.create_fac_pagination_missions(
                    factory=UserCallbackFactory,
                    mission_status=callback_data.page,
                    back_page=callback_data.page,
                    back="missions",
                    mission_count=mission_count,
                    mission_page=callback_data.mission_page,
                    **preprocess_mission,
                ),
            )
        else:
            await callback.message.edit_text(
                text=errorLexicon["errorMission"],
                reply_markup=await Factories.create_fac_menu(
                    UserCallbackFactory,
                    back_page=callback_data.page,
                    back="missions",
                    sizes=(3,),
                    **listMissions,
                ),
            )
    except exceptions.TelegramBadRequest:
        pass
    finally:
        await callback.answer()


@router.callback_query(MissionCallbackFactory.filter(F.page.isdigit()))
@router.callback_query(MissionCallbackFactory.filter(F.page == "information"))
async def information_mission(
    callback: CallbackQuery, callback_data: MissionCallbackFactory
) -> NoReturn:
    mission_obj, wallet_obj = await SubmissionsAPI.select_missions(
        False,
        None,
        0,
        *(Submissions, Wallets),
        Id=callback_data.mission_id
    )
    delete_mission = (
        {f"delete-{mission_obj.Id}": revokeButton["revoke"]}
        if mission_obj.Status == Statuses.wait
        else {}
    )
    await callback.message.edit_text(
        text=botMessages["informationMissionUser"].format(
            missionID=mission_obj.Id,
            adminID=mission_obj.AdminId,
            userRequisites=mission_obj.AddressUser,
            workWallet=wallet_obj.Address,
            amountFrom=mission_obj.AmountFrom,
            NameNet=wallet_obj.NameNet,
            amountTo=mission_obj.AmountTo,
            currencyTo=mission_obj.CurrencyTo,
            statusMission=changeStatus[mission_obj.Status.value.lower()].upper(),
            dataTime=mission_obj.created_at,
        ),
        reply_markup=await Factories.create_fac_mission(
            MissionCallbackFactory,
            mission_id=callback_data.mission_id,
            back="missions",
            back_name=backLexicon["backMission"],
            sizes=(1, 1),
            **delete_mission,
        ),
    )


@router.callback_query(MissionCallbackFactory.filter(F.page.regexp(r"^delete-\d+$")))
async def delete_user_mission(
    callback: CallbackQuery, callback_data: MissionCallbackFactory
) -> NoReturn:
    mission_id: str = callback_data.page.split("-")[1]
    await SubmissionsAPI.delete_mission_by_id(mission_id=int(mission_id))
    await callback.message.edit_text(
        text=botMessages["deleteMissionUser"].format(missionID=mission_id),
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory,
            back_page=callback_data.page,
            back="profile",
            sizes=(3,),
            **listMissions,
        ),
    )
