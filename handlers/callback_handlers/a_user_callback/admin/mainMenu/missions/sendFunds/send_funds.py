import json
from typing import Any

from aiogram import Router, F, Bot
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from redis.asyncio.client import Redis
from aiogram.types import CallbackQuery

from keyboard.keyboard_factory import Factories
from lexicon.lexicon import botMessages, send

from config.config import load_config
from dataTemplates.data_templates import MnemonicData, SendData
from databaseAPI.commands.submissions_commands import SubmissionsAPI
from databaseAPI.models import Wallets, Submissions
from factories.factory import MissionCallbackFactory
from filters.filters import CheckSendFunds, IsAdmin
from services.cryptoWalletAPIService import CryptoWalletAPIService
from services.walletService import WalletService
from states.states import FSMSendFunds

router: Router = Router()


@router.callback_query(
    MissionCallbackFactory.filter(F.page == "sendFunds"), IsAdmin(checkAdminWork=True)
)
async def send_funds_handler(
    callback: CallbackQuery,
    callback_data: MissionCallbackFactory,
    state: FSMContext,
    redis: Redis,
    bot: Bot,
) -> None:
    if (photo_id := (await state.get_data()).get("photoId")) is not None:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=photo_id)
        await state.clear()
    mission_obj: Submissions = (
        await SubmissionsAPI.select_missions(
            False,
            None,
            0,
            *(Submissions,),
            Id=callback_data.mission_id,
        )
    )[0]
    wallet: Wallets = await WalletService.random_wallet(
        special_filter=(Wallets.MnemonicId is not None,),
        mnemonic=True,
        NameNet=mission_obj.CurrencyTo,
    )
    match data := (await redis.get(f"mnemonic:{wallet.mnemonic.Id}")):
        case None:
            mnemonic: str = await WalletService.decrypt_private_key(
                encrypted_private_key=wallet.mnemonic.EncryptMnemonic,
                secret_key=load_config().SecretKey.SECRETKEY,
            )
            _, crypto_api = await CryptoWalletAPIService.get_api_and_client(
                token=mission_obj.CurrencyTo, private_key=mnemonic
            )
            address: str = crypto_api.address
            balance: float = await crypto_api.balance
            data = {
                "address": address,
                "balance": balance,
                "mnemonic": mnemonic,
                "token": mission_obj.CurrencyTo,
            }
            await redis.setex(
                name=f"mnemonic:{wallet.mnemonic.Id}", time=600, value=json.dumps(data)
            )
        case _:
            data: dict[str:Any] = json.loads(data)
    mnemonic_data: MnemonicData = MnemonicData(**data)
    send_data: SendData = SendData(
        user_address=mission_obj.AddressUser, amount=mission_obj.AmountTo
    )
    await state.update_data(
        MnemonicData=mnemonic_data.__dict__, SendData=send_data.__dict__
    )
    await callback.message.edit_text(
        text=botMessages["sendFunds"].format(
            adminAddress=mnemonic_data.address,
            balance=mnemonic_data.balance,
            amount=send_data.amount,
            userAddress=send_data.user_address,
            token=mnemonic_data.token,
        ),
        reply_markup=await Factories.create_fac_mission(
            MissionCallbackFactory,
            mission_id=callback_data.mission_id,
            back=callback_data.mission_id,
            sizes=(1, 1),
            **send,
        ),
    )
    await state.set_state(FSMSendFunds.check_sure)


@router.callback_query(
    MissionCallbackFactory.filter(F.page == "send"),
    IsAdmin(checkAdminWork=True),
    StateFilter(FSMSendFunds.check_sure),
    CheckSendFunds(),
)
async def send_handler(
    callback: CallbackQuery, callback_data: MissionCallbackFactory, state: FSMContext
) -> None:
    data: dict[str:Any] = await state.get_data()
    mnemonic_data: MnemonicData = MnemonicData(**data["MnemonicData"])
    send_data: SendData = SendData(**data["SendData"])
    _, crypto_api = await CryptoWalletAPIService.get_api_and_client(
        token=mnemonic_data.token, private_key=mnemonic_data.mnemonic
    )
    await crypto_api.send_funds(
        to_address=send_data.user_address,
        amount=send_data.amount,
        memo=str(callback_data.mission_id),
    )
    await callback.message.edit_text(
        text=botMessages["send"].format(
            userAddress=send_data.user_address,
            amount=send_data.amount,
            token=mnemonic_data.token,
            balance=mnemonic_data.balance,
        ),
        reply_markup=await Factories.create_fac_mission(
            MissionCallbackFactory,
            mission_id=callback_data.mission_id,
            back=callback_data.mission_id,
        ),
    )
