from typing import Sequence

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from databaseAPI.commands.mnemonic_commands import MnemonicAPI
from databaseAPI.commands.walletAddress_commands import WalletAPI
from databaseAPI.models import Wallets
from databaseAPI.models.models import MnemonicWallets
from factories.factory import MissionCallbackFactory
from filters.filters import IsAdmin

router: Router = Router()


@router.callback_query(MissionCallbackFactory.filter(F.page == "sendFunds"), IsAdmin())
async def send_funds_handler(
    callback: CallbackQuery, callback_data: MissionCallbackFactory, state: FSMContext
) -> None:
    token: str = (await state.get_data())["currencyTo"]
    wallet_id: Sequence[Wallets] = await WalletAPI.select_wallets()
    wallet_mnemonic: Sequence[str] = await MnemonicAPI.select_mnemonic(
        MnemonicWallets, WalletId=wallet_id
    )
    print(wallet_mnemonic)
