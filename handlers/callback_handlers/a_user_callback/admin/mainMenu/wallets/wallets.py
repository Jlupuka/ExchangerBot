from typing import NoReturn

from aiogram import Router
from aiogram import F

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from databaseAPI.commands.walletAddress_commands import WalletAPI

from filters.filters import IsAdmin
from lexicon.lexicon import botMessages, walletsMenu

from keyboard.keyboard_factory import Factories
from factories.factory import AdminCallbackFactory

from services.walletService import WalletService

router: Router = Router()


@router.callback_query(AdminCallbackFactory.filter(F.page == "wallets"), IsAdmin())
async def wallets_handler(
    callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext
) -> NoReturn:
    await state.clear()
    wallets_dict: dict[str:str] = await WalletService.get_wallets(
        func=WalletAPI.get_all_name_net_wallets
    )
    wallets_menu: dict[str:str] = walletsMenu.copy()
    if wallets_dict:
        wallets_menu = {
            **{key: wallets_dict[key] for key in sorted(wallets_dict)},
            **wallets_menu,
        }
    size: tuple[int, ...] = (
        await WalletService.get_size_wallet(len_wallet=len_wallet, count_any_button=2)
        if (len_wallet := len(wallets_dict)) > 1
        else (1, 1, 1)
    )
    await callback.message.edit_text(
        text=botMessages["walletsMenu"],
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory,
            back_page=callback_data.page,
            back="settings",
            sizes=size,
            **wallets_menu,
        ),
    )
