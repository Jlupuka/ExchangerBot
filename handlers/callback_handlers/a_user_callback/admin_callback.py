from aiogram import Router, Bot, exceptions
from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, BotName

from databaseAPI.commands.userCommands.admin_commands import AdminAPI
from databaseAPI.commands.walletAddress_commands import WalletAPI
from databaseAPI.commands.submissions_commands import SubmissionsAPI
from databaseAPI.tables import WalletAddress, Submissions
from filters.filters import IsAdmin, IsToken
from lexicon.lexicon import botMessages, startCallbackAdmin, settingsMenu, workType, missions, walletsMenu, \
    checkCorrectAddWallet, successfullyMessage, addressMenu, sureLexicon, addressDelete, errorLexicon, addressEdit, \
    statusWork, backLexicon, sendMission, changeStatus, checkMark, informationMissionUser, listMissions, \
    revokeMission, revokeButton, startCallbackUser

from keyboard.keyboard_factory import Factories
from factories.factory import AdminCallbackFactory, MissionCallbackFactory, UserCallbackFactory, KYCCallbackFactory
from services import logger
from services.qrCodeService import QRCodeService

from services.submissionService import SubmissionService
from services.userService import UserService
from services.walletService import WalletService
from states.states import FSMAddWallet, FSMPercentEdit, FSMRevokeMission

router: Router = Router()


@router.callback_query(MissionCallbackFactory.filter(F.page == 'main'), IsAdmin())
@router.callback_query(AdminCallbackFactory.filter(F.page == 'main'), IsAdmin())
async def start_handler_admin(callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        text=botMessages['startMessageAdmin'],
        reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                     sizes=(2, 2),
                                                     back_page=callback_data.page,
                                                     **startCallbackAdmin)
    )


@router.callback_query(AdminCallbackFactory.filter(F.page == 'statistics'), IsAdmin())
async def statistics_handler(callback: CallbackQuery, callback_data: AdminCallbackFactory, bot: Bot) -> None:
    data: dict[str: int | float | str] = await SubmissionsAPI.get_statistic_data()
    gain_statistic: dict[str: int | float | str] = await UserService.statistic_admin()
    result = {**data, **gain_statistic}
    bot_name: BotName = await bot.get_my_name()
    await bot.get_me()
    await callback.message.edit_text(text=botMessages['statisticAdmin'].format(**result, botName=bot_name.name),
                                     reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                                                  back=callback_data.back_page))


@router.callback_query(AdminCallbackFactory.filter(F.page.in_({'settings', 'workType'})), IsAdmin())
async def settings_handler(callback: CallbackQuery, callback_data: AdminCallbackFactory) -> None:
    admin_work_type: bool = await AdminAPI.get_workType(user_id=callback.from_user.id)
    if callback_data.page == 'workType':
        admin_work_type = await AdminAPI.update_workType(user_id=callback.from_user.id, work_type=admin_work_type)
    count_wait_missions: int = len(await SubmissionsAPI.get_missions_by_status(mission_status='WAIT'))
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
                                     reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                                                  back_page=callback_data.back_page,
                                                                                  back='main',
                                                                                  sizes=(1, 2, 1)
                                                                                  if admin_work_type
                                                                                  else (2, 1),
                                                                                  **buttons))


@router.callback_query(AdminCallbackFactory.filter(F.page == 'wallets'), IsAdmin())
async def wallets_handler(callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext) -> None:
    await state.clear()
    wallets_dict: dict[str: str] = await WalletService.get_wallets(func=WalletAPI.get_all_name_net_wallets)
    wallets_menu: dict[str: str] = walletsMenu.copy()
    if wallets_dict:
        wallets_menu = {**{key: wallets_dict[key] for key in sorted(wallets_dict)}, **wallets_menu}
    size: tuple[int, ...] = await WalletService.get_size_wallet(len_wallet=len_wallet,
                                                                count_any_button=2) \
        if (len_wallet := len(wallets_dict)) > 1 else (1, 1, 1)
    await callback.message.edit_text(text=botMessages['walletsMenu'],
                                     reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                                                  back_page=callback_data.page,
                                                                                  back='settings',
                                                                                  sizes=size,
                                                                                  **wallets_menu))


@router.callback_query(AdminCallbackFactory.filter(F.page == 'no'), StateFilter(FSMAddWallet.type_wallet), IsAdmin())
@router.callback_query(AdminCallbackFactory.filter(F.page == 'addWallet'), IsAdmin())
async def add_wallet_handler(callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(FSMAddWallet.currency_to)
    await callback.message.edit_text(text=botMessages['addWallet'],
                                     reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
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
                                     reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
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
                                     reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
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
                                         reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                                                      back='wallets',
                                                                                      back_name=backLexicon[
                                                                                          'backLexicon']))
    else:
        await callback.message.edit_text(text=errorLexicon['WalletExist'].format(nameNet=name_net,
                                                                                 address=address,
                                                                                 walletType=wallet_type),
                                         reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                                                      back='wallets',
                                                                                      back_name=backLexicon[
                                                                                          'backLexicon']))
    await state.clear()


@router.callback_query(AdminCallbackFactory.filter(), IsToken(AdminCallbackFactory), IsAdmin())
async def print_wallets(callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext) -> None:
    await state.clear()
    await state.update_data(name_net=callback_data.page)
    wallets_list: list[tuple[int, str]] = await WalletAPI.get_wallets_data(name_net=callback_data.page.upper())
    text, wallets_dict = await WalletService.preprocess_wallets(wallets=wallets_list)
    await state.update_data(**wallets_dict)
    await callback.message.edit_text(
        text=text,
        reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                     back='wallets',
                                                     back_page=callback_data.page,
                                                     sizes=await WalletService.get_size_wallet(
                                                         len_wallet=len(wallets_dict),
                                                         count_any_button=1),
                                                     **wallets_dict))


@router.callback_query(AdminCallbackFactory.filter(F.page.regexp(r'^TokenId-\d+$')), IsAdmin())
async def address_menu(callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext) -> None:
    await state.update_data(token=callback_data.page)
    state_data = await state.get_data()
    await callback.message.edit_text(text=botMessages['addressMenu'],
                                     reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                                                  back=state_data['name_net'],
                                                                                  back_page=callback_data.page,
                                                                                  sizes=(2, 1),
                                                                                  **addressMenu))


@router.callback_query(AdminCallbackFactory.filter(F.page == 'deleteAddress'), StateFilter(None), IsAdmin())
async def delete_address_menu(callback: CallbackQuery, callback_data: AdminCallbackFactory) -> None:
    sureDelete_copy = sureLexicon.copy()
    sureDelete_copy[callback_data.back_page] = sureDelete_copy.pop('no')
    await callback.message.edit_text(text=botMessages['sureDelete'],
                                     reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                                                  sizes=(2,),
                                                                                  **sureDelete_copy))


@router.callback_query(AdminCallbackFactory.filter(F.page == 'yes'), StateFilter(None), IsAdmin())
async def delete_address(callback: CallbackQuery, state: FSMContext) -> None:
    state_data = await state.get_data()
    address_id = int(state_data['token'].split('-')[1])
    await WalletAPI.delete_wallet(wallet_id=address_id)
    await callback.message.edit_text(text=botMessages['deleteAddress'].format(wallet=state_data[state_data['token']]),
                                     reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
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
                                     reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
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
                                     reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                                                  back=back_page,
                                                                                  back_name=backLexicon[
                                                                                      'cancelLexicon']))


@router.callback_query(AdminCallbackFactory.filter(F.page == 'checkPercent'),
                       StateFilter(FSMPercentEdit.check_percent), IsAdmin())
async def update_percent_wallet(callback: CallbackQuery,
                                state: FSMContext) -> None:
    await state.set_state(None)
    state_data = await state.get_data()
    wallet_id = int(state_data['token'].split('-')[1])
    percent = state_data['percent']
    await WalletAPI.update_percent(wallet_id=wallet_id, percent=percent)
    await callback.message.edit_text(text=botMessages['completedEditPercent'].format(percent=percent),
                                     reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                                                  back=state_data['token'],
                                                                                  back_name=backLexicon['backLexicon']))


@router.callback_query(MissionCallbackFactory.filter(F.page == 'revoke'), IsAdmin(checkAdminWork=True))
async def check_revoke_mission(callback: CallbackQuery, callback_data: MissionCallbackFactory,
                               state: FSMContext, bot: Bot) -> None:
    if (photo_id := (await state.get_data()).get('photoId')) is not None:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=photo_id)
        await state.update_data(photoId=None)
    mission_obj, _, _ = await SubmissionsAPI.get_mission_data(mission_id=callback_data.mission_id)
    if mission_obj.AdminId is None or mission_obj.AdminId == callback.from_user.id:
        await state.set_state(FSMRevokeMission.sure)
        await state.update_data(typeRevoke='SIMPLE')
        await callback.message.edit_text(text=botMessages['sureRevoke'].format(
            missionID=callback_data.mission_id),
            reply_markup=await Factories.create_fac_mission(MissionCallbackFactory,
                                                            mission_id=callback_data.mission_id,
                                                            back=callback_data.mission_id,
                                                            back_name=backLexicon['backLexicon'],
                                                            sizes=(1, 1),
                                                            **revokeMission))
    else:
        await callback.answer(text=errorLexicon['anotherAdminTakeMiss'])


@router.callback_query(MissionCallbackFactory.filter(F.page == 'revokeWithMessage'), IsAdmin(checkAdminWork=True))
async def get_message_to_revoke(callback: CallbackQuery, callback_data: MissionCallbackFactory,
                                state: FSMContext, bot: Bot) -> None:
    if (photo_id := (await state.get_data()).get('photoId')) is not None:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=photo_id)
        await state.update_data(photoId=None)
    mission_obj, _, _ = await SubmissionsAPI.get_mission_data(mission_id=callback_data.mission_id)
    if mission_obj.AdminId is None or mission_obj.AdminId == callback.from_user.id:
        await state.set_state(FSMRevokeMission.message)
        await state.update_data(missionID=callback_data.mission_id, messageID=callback.message.message_id)
        await callback.message.edit_text(
            text=botMessages['getMessageToRevoke'],
            reply_markup=await Factories.create_fac_mission(MissionCallbackFactory,
                                                            mission_id=callback_data.mission_id,
                                                            back=callback_data.mission_id))
    else:
        await callback.answer(text=errorLexicon['anotherAdminTakeMiss'])


@router.callback_query(MissionCallbackFactory.filter(F.page == 'YesRevokeMission'),
                       StateFilter(FSMRevokeMission.sure), IsAdmin(checkAdminWork=True))
async def revoke_mission(callback: CallbackQuery, callback_data: MissionCallbackFactory,
                         state: FSMContext, bot: Bot) -> None:
    state_data = await state.get_data()
    mission_obj, wallet_obj, user = await SubmissionsAPI.get_mission_data(mission_id=callback_data.mission_id)
    type_revoke = state_data['typeRevoke']
    message = state_data.get('messageRevoke', None)
    await callback.message.edit_text(
        text=botMessages['revokeSimpleA']
        if type_revoke == 'SIMPLE'
        else botMessages['revokeWithTextA'].format(messageRevoke=message),
        reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                     back='missions',
                                                     back_name=backLexicon['backMission']))
    await bot.send_message(chat_id=user.UserId,
                           text=botMessages['revokeSimpleU'].format(missionID=mission_obj.Id)
                           if type_revoke == 'SIMPLE'
                           else botMessages['revokeWithTextU'].format(missionID=mission_obj.Id,
                                                                      messageRevoke=message),
                           reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                                        back='missions',
                                                                        back_name=backLexicon['backMission']))
    await SubmissionsAPI.delete_mission_by_id(mission_id=mission_obj.Id)
    await state.clear()


@router.callback_query(MissionCallbackFactory.filter(F.page.isdigit()), IsAdmin(checkAdminWork=True))
async def mission_data(callback: CallbackQuery, callback_data: MissionCallbackFactory,
                       state: FSMContext, bot: Bot) -> None:
    await state.clear()
    await callback.message.delete()
    sendMission_copy: dict[str: str] = sendMission.copy()
    mission_obj, wallet_obj, user = await SubmissionsAPI.get_mission_data(mission_id=callback_data.mission_id)
    if mission_obj:
        if mission_obj.Status != 'COMPLETED':
            sendMission_copy = {**sendMission, **revokeButton}
        if mission_obj.TypeTrans.split('/')[1] == 'CRYPTO' and mission_obj.Status != 'COMPLETED':
            file_path: str = await QRCodeService.create_crypto_payment_qrcode(
                amount=mission_obj.AmountFrom,
                crypto_currency=mission_obj.CurrencyTo,
                address=mission_obj.AddressUser,
                description=f'UserId-{user.UserId}'
            )
            photo: FSInputFile = FSInputFile(file_path)
            message = await bot.send_photo(chat_id=callback.from_user.id, photo=photo)
            await state.update_data(photoId=message.message_id)
            await QRCodeService.delete_file(file_name=file_path)
        await bot.send_message(chat_id=callback.from_user.id,
                               text=botMessages['sendMission'].format(
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
                                   dataTime=mission_obj.DateTime
                               ),
                               reply_markup=await Factories.create_fac_mission(MissionCallbackFactory,
                                                                               mission_id=mission_obj.Id,
                                                                               back='missions',
                                                                               back_name=backLexicon['backMission'],
                                                                               sizes=(2, 1)
                                                                               if len(sendMission_copy) > 1
                                                                               else (1, 1),
                                                                               **sendMission_copy))


@router.callback_query(MissionCallbackFactory.filter(F.page.in_({'wait', 'accepted', 'completed', 'changeStatus'})),
                       IsAdmin(checkAdminWork=True))
async def get_missions(callback: CallbackQuery, callback_data: MissionCallbackFactory,
                       state: FSMContext, bot: Bot) -> None:
    if (photo_id := (await state.get_data()).get('photoId')) is not None:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=photo_id)
        await state.update_data(photoId=None)
    if callback_data.page != callback_data.back_page:
        mission_obj, _, user = await SubmissionsAPI.get_mission_data(mission_id=callback_data.mission_id)
        if mission_obj.AdminId is None or mission_obj.AdminId == callback.from_user.id:
            oldStatus = mission_obj.Status
            if callback_data.page != 'changeStatus':
                await SubmissionsAPI.update_mission_status(submission_id=callback_data.mission_id,
                                                           status=callback_data.page.upper())
                mission_obj.Status = callback_data.page.upper()
            copy_changeStatus = changeStatus.copy()
            copy_changeStatus[mission_obj.Status.lower()] = f'{mission_obj.Status} {checkMark["yes"]}'
            await callback.message.edit_text(text=botMessages['changeStatus'].format(
                missionID=mission_obj.Id,
                statusMission=mission_obj.Status
            ),
                reply_markup=await Factories.create_fac_mission(MissionCallbackFactory,
                                                                mission_id=callback_data.mission_id,
                                                                back=callback_data.mission_id,
                                                                back_name=backLexicon['backLexicon'],
                                                                back_page=callback_data.page,
                                                                sizes=(3, 1),
                                                                **copy_changeStatus))
            if callback_data.page in {'wait', 'accepted', 'completed'}:  # Notifying the user
                await bot.send_message(
                    chat_id=user.UserId,
                    text=botMessages['changeStatusUser'].format(
                        missionID=mission_obj.Id,
                        statusMission=changeStatus[mission_obj.Status.lower()].upper(),
                    ),
                    reply_markup=await Factories.create_fac_mission(MissionCallbackFactory,
                                                                    mission_id=callback_data.mission_id,
                                                                    back='main',
                                                                    back_name=backLexicon[
                                                                        'backMainMenu'],
                                                                    sizes=(1, 1),
                                                                    **informationMissionUser))
                await SubmissionsAPI.update_admin_id(submission_id=mission_obj.Id,
                                                     admin_id=None
                                                     if callback_data.page == 'wait'
                                                     else callback.from_user.id)
                logger.info("userID=%s, adminID=%s, oldStatus=%s, newStatus=%s",
                            user.UserId, callback.from_user.id, oldStatus, mission_obj.Status)
        elif mission_obj.AdminId != callback.from_user.id:
            copy_changeStatus = changeStatus.copy()
            copy_changeStatus[mission_obj.Status.lower()] = f'{mission_obj.Status} {checkMark["yes"]}'
            await callback.message.edit_text(
                text=errorLexicon['anotherAdminTakeMiss'],
                reply_markup=await Factories.create_fac_mission(MissionCallbackFactory,
                                                                mission_id=callback_data.mission_id,
                                                                back=callback_data.mission_id,
                                                                back_name=backLexicon['backLexicon'],
                                                                back_page=callback_data.page,
                                                                sizes=(3, 1),
                                                                **copy_changeStatus))

    await callback.answer()


@router.callback_query(MissionCallbackFactory.filter(F.page == 'missions'), IsAdmin(checkAdminWork=True))
@router.callback_query(AdminCallbackFactory.filter(F.page == 'missions'), IsAdmin(checkAdminWork=True))
async def get_missions_type(callback: CallbackQuery, callback_data: AdminCallbackFactory,
                            state: FSMContext, bot: Bot) -> None:
    if (photo_id := (await state.get_data()).get('photoId')) is not None:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=photo_id)
        await state.update_data(photoId=None)

    await callback.message.edit_text(text=botMessages['missionsText'].format(
        missionsCount=await SubmissionService.get_count_each_missions()
    ),
        reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                     back_page=callback_data.page,
                                                     back='settings',
                                                     sizes=(3,),
                                                     **listMissions))


@router.callback_query(AdminCallbackFactory.filter(F.page.in_({'accepted', 'completed', 'wait'})),
                       IsAdmin(checkAdminWork=True))
async def missions_return(callback: CallbackQuery, callback_data: AdminCallbackFactory,
                          state: FSMContext, bot: Bot) -> None:
    if (photo_id := (await state.get_data()).get('photoId')) is not None:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=photo_id)
        await state.update_data(photoId=None)
    try:
        mission_status = callback_data.page.upper()
        missions_data: list[Submissions] = await (
            SubmissionsAPI.get_missions_by_status(mission_status=mission_status,
                                                  pagination=True,
                                                  offset=callback_data.mission_page))
        if missions_data:
            mission_count = len(missions_data)
            mission_count_total = await SubmissionsAPI.get_count_missions_by_status(mission_status=mission_status)
            text, preprocess_mission = await SubmissionService.preprocess_mission_data(mission_data=missions_data)
            await callback.message.edit_text(
                text=text,
                reply_markup=await Factories.create_fac_pagination_missions(factory=AdminCallbackFactory,
                                                                            mission_status=callback_data.page,
                                                                            back_page=callback_data.page,
                                                                            back='missions',
                                                                            mission_count=mission_count,
                                                                            mission_count_total=mission_count_total,
                                                                            mission_page=callback_data.mission_page,
                                                                            **preprocess_mission))
        else:
            await callback.message.edit_text(text=errorLexicon['errorMission'],
                                             reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                                                          back_page=callback_data.page,
                                                                                          back='missions',
                                                                                          sizes=(3,),
                                                                                          **listMissions))
    except exceptions.TelegramBadRequest:
        pass
    finally:
        await callback.answer()


@router.callback_query(KYCCallbackFactory.filter(F.page == 'verifUser'))
async def approve_verif_user(callback: CallbackQuery, callback_data: KYCCallbackFactory, bot: Bot) -> None:
    await AdminAPI.update_kyc(user_id=callback_data.user_id, typeKYC=True)
    await callback.message.answer(text=botMessages['approveVerif'].format(
        userID=callback_data.user_id
    ), reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                    sizes=(2, 2),
                                                    back_page='main',
                                                    **startCallbackAdmin))
    await bot.send_message(chat_id=callback_data.user_id, text=botMessages['approveVerifUser'],
                           reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                                        sizes=(2, 1, 2),
                                                                        back_page='main',
                                                                        **startCallbackUser))
    await callback.message.delete()


@router.callback_query(KYCCallbackFactory.filter(F.page == 'reject'))
async def reject_verif_user(callback: CallbackQuery, callback_data: KYCCallbackFactory, bot: Bot) -> None:
    await callback.message.answer(text=botMessages['rejectVerifAdmin'].format(
        userID=callback_data.user_id
    ), reply_markup=await Factories.create_fac_menu(AdminCallbackFactory,
                                                    sizes=(2, 2),
                                                    back_page='main',
                                                    **startCallbackAdmin))
    await bot.send_message(chat_id=callback_data.user_id, text=botMessages['rejectVerifUser'],
                           reply_markup=await Factories.create_fac_menu(UserCallbackFactory,
                                                                        sizes=(2, 1, 2),
                                                                        back_page='main',
                                                                        **startCallbackUser))
    await callback.message.delete()
