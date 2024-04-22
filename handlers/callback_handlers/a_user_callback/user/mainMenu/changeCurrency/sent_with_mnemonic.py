from typing import Union

from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from dataTemplates.data_templates import WalletTRX
from databaseAPI.commands.submissions_commands import SubmissionsAPI
from databaseAPI.models import Submissions, Users
from databaseAPI.models.models import TypesTrans
from lexicon.lexicon import (
    botMessages,
    backLexicon,
    sendMission,
    changeStatus,
    revokeButton,
    receiptVerification,
    errorLexicon,
)

from keyboard.keyboard_factory import Factories
from factories.factory import UserCallbackFactory, MissionCallbackFactory
from services import logger
from services.cryptoWalletAPIService import CryptoWalletAPIService
from services.dataTemplatesService import DataTemplatesService

from services.userService import UserService
from states.states import FSMCryptoFiat, FSMCryptoCrypto

router: Router = Router()


@router.callback_query(
    UserCallbackFactory.filter(F.page == "sent"),
    StateFilter(FSMCryptoFiat.money_sent_mnemonic, FSMCryptoCrypto.money_sent_mnemonic),
)
async def create_mission_(
    callback: CallbackQuery, state: FSMContext, user: Users, bot: Bot
) -> None:
    state_data: dict[str:str] = await state.get_data()
    walletCurrency: str = state_data["WalletCurrency"]
    wallet_template = await DataTemplatesService.select_crypto_data_templates(
        token=walletCurrency
    )
    wallet_data: Union[WalletTRX] = wallet_template(**state_data["WalletData"])
    _, crypto_api = await CryptoWalletAPIService.get_api_and_client(
        token=walletCurrency, private_key=wallet_data.private_key
    )
    amount_to: float = state_data["amount_to"]
    currency_to: str = state_data["currency_to"]
    amount_from: int = state_data["amount_from"]
    if (
        amount := (await crypto_api.balance) - 1
    ) > 1 and await crypto_api.check_payment(amount=amount_to):
        wallet_requisites: str = state_data["user_requisites"]
        wallet_id: int = state_data["walletId"]
        main_wallet_address: str = state_data["mainWalletAddress"]
        admin_obj: Users | None = await UserService.random_admin()
        type_trans: TypesTrans = TypesTrans[
            state_data["typeTransaction"].replace("-", "_").lower()
        ]
        send_funds = await crypto_api.send_funds(
            to_address=main_wallet_address, amount=amount, memo=str(user.UserId)
        )
        logger.info(f"A transaction has been completed -- {send_funds}")
        mission_obj: Submissions = await SubmissionsAPI.add_application(
            UserId=user.Id,
            WalletId=wallet_id,
            CurrencyTo=currency_to,
            AmountTo=amount_to,
            AmountFrom=amount_from,
            TypeTrans=type_trans,
            AddressUser=wallet_requisites,
        )
        await callback.message.answer(
            text=botMessages["createMission"].format(
                mission_id=mission_obj.Id,
                user_requisites=wallet_requisites,
                amount=amount_to,
                currency_to=currency_to,
            ),
            reply_markup=await Factories.create_fac_menu(
                UserCallbackFactory, back="main", back_name=backLexicon["backMainMenu"]
            ),
        )
        if admin_obj:
            sendMission_copy = {**sendMission, **revokeButton}
            await bot.send_message(
                chat_id=admin_obj.UserId,
                text=botMessages["sendMission"].format(
                    currencyTo=currency_to,
                    walletCurrency=walletCurrency,
                    missionID=mission_obj.Id,
                    adminID=mission_obj.AdminId,
                    userID=callback.from_user.id,
                    workWallet=wallet_data.base58check_address,
                    userRequisites=wallet_requisites,
                    amountFrom=amount_from,
                    amountTo=amount_to,
                    statusMission=changeStatus[
                        mission_obj.Status.value.lower()
                    ].upper(),
                    dataTime=mission_obj.created_at,
                ),
                reply_markup=await Factories.create_fac_mission(
                    MissionCallbackFactory,
                    mission_id=mission_obj.Id,
                    back="main",
                    back_name=backLexicon["backMainMenu"],
                    sizes=(2, 1),
                    **sendMission_copy,
                ),
            )
        await state.clear()
    if "ОШИБКА" not in callback.message.text:
        text = errorLexicon["sentUser"] + botMessages["receiptVerification"].format(
            amount_to=amount_to,
            currency_to=currency_to,
            amount_from=amount_from,
            type_transaction=walletCurrency,
            work_wallet=wallet_data.base58check_address,
        )
        await callback.message.edit_text(
            text=text,
            reply_markup=await Factories.create_fac_menu(
                UserCallbackFactory,
                back="main",
                back_name=backLexicon["cancelLexicon"],
                **receiptVerification,
            ),
        )
    await callback.answer()
