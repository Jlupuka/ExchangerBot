from typing import NoReturn, Union

from aiogram import Router, Bot, exceptions
from aiogram import F
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile

from databaseAPI.commands.submissions_commands import SubmissionsAPI
from databaseAPI.tables import Submissions
from filters.filters import IsAdmin
from lexicon.lexicon import (
    botMessages,
    errorLexicon,
    backLexicon,
    sendMission,
    changeStatus,
    listMissions,
    revokeButton,
)

from keyboard.keyboard_factory import Factories
from factories.factory import (
    AdminCallbackFactory,
    MissionCallbackFactory,
)

from services.qrCodeService import QRCodeService

from services.submissionService import SubmissionService

router: Router = Router()


@router.callback_query(
    MissionCallbackFactory.filter(F.page.isdigit()), IsAdmin(checkAdminWork=True)
)
async def mission_data(
    callback: CallbackQuery,
    callback_data: MissionCallbackFactory,
    state: FSMContext,
    bot: Bot,
) -> NoReturn:
    await state.clear()
    await callback.message.delete()
    sendMission_copy: dict[str:str] = sendMission.copy()
    mission_obj, wallet_obj, user = await SubmissionsAPI.get_mission_data(
        mission_id=callback_data.mission_id
    )
    if mission_obj:
        if mission_obj.Status != "COMPLETED":
            sendMission_copy = {**sendMission, **revokeButton}
        if (
            mission_obj.TypeTrans.split("/")[1] == "CRYPTO"
            and mission_obj.Status != "COMPLETED"
        ):
            file_path: str = await QRCodeService.create_crypto_payment_qrcode(
                amount=mission_obj.AmountFrom,
                crypto_currency=mission_obj.CurrencyTo,
                address=mission_obj.AddressUser,
                description=f"UserId-{user.UserId}",
            )
            photo: FSInputFile = FSInputFile(file_path)
            message = await bot.send_photo(chat_id=callback.from_user.id, photo=photo)
            await state.update_data(photoId=message.message_id)
            await QRCodeService.delete_file(file_name=file_path)
        await bot.send_message(
            chat_id=callback.from_user.id,
            text=botMessages["sendMission"].format(
                currencyTo=mission_obj.CurrencyTo,
                missionID=mission_obj.Id,
                adminID=mission_obj.AdminId,
                userID=user.UserId,
                workWallet=wallet_obj.Address,
                userRequisites=mission_obj.AddressUser,
                amountFrom=mission_obj.AmountFrom,
                walletCurrency=wallet_obj.NameNet,
                amountTo=mission_obj.AmountTo,
                statusMission=changeStatus[mission_obj.Status.lower()].upper(),
                dataTime=mission_obj.DateTime,
            ),
            reply_markup=await Factories.create_fac_mission(
                MissionCallbackFactory,
                mission_id=mission_obj.Id,
                back="missions",
                back_name=backLexicon["backMission"],
                sizes=(2, 1) if len(sendMission_copy) > 1 else (1, 1),
                **sendMission_copy,
            ),
        )


@router.callback_query(
    or_f(
        MissionCallbackFactory.filter(F.page == "missions"),
        AdminCallbackFactory.filter(F.page == "missions"),
    ),
    IsAdmin(checkAdminWork=True),
)
async def get_missions_type(
    callback: CallbackQuery,
    callback_data: Union[AdminCallbackFactory, MissionCallbackFactory],
    state: FSMContext,
    bot: Bot,
) -> NoReturn:
    if (photo_id := (await state.get_data()).get("photoId")) is not None:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=photo_id)
        await state.update_data(photoId=None)

    await callback.message.edit_text(
        text=botMessages["missionsText"].format(
            missionsCount=await SubmissionService.get_count_each_missions()
        ),
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory,
            back_page=callback_data.page,
            back="settings",
            sizes=(3,),
            **listMissions,
        ),
    )


@router.callback_query(
    AdminCallbackFactory.filter(F.page.in_({"accepted", "completed", "wait"})),
    IsAdmin(checkAdminWork=True),
)
async def missions_return(
    callback: CallbackQuery,
    callback_data: AdminCallbackFactory,
    state: FSMContext,
    bot: Bot,
) -> NoReturn:
    if (photo_id := (await state.get_data()).get("photoId")) is not None:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=photo_id)
        await state.update_data(photoId=None)
    try:
        mission_status = callback_data.page.upper()
        missions_data: list[Submissions] = await SubmissionsAPI.get_missions_by_status(
            mission_status=mission_status,
            pagination=True,
            offset=callback_data.mission_page,
        )
        if missions_data:
            mission_count = len(missions_data)
            mission_count_total = await SubmissionsAPI.get_count_missions_by_status(
                mission_status=mission_status
            )
            text, preprocess_mission = await SubmissionService.preprocess_mission_data(
                mission_data=missions_data
            )
            await callback.message.edit_text(
                text=text,
                reply_markup=await Factories.create_fac_pagination_missions(
                    factory=AdminCallbackFactory,
                    mission_status=callback_data.page,
                    back_page=callback_data.page,
                    back="missions",
                    mission_count=mission_count,
                    mission_count_total=mission_count_total,
                    mission_page=callback_data.mission_page,
                    **preprocess_mission,
                ),
            )
        else:
            await callback.message.edit_text(
                text=errorLexicon["errorMission"],
                reply_markup=await Factories.create_fac_menu(
                    AdminCallbackFactory,
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
