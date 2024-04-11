from aiogram import Router
from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from databaseAPI.commands.walletAddress_commands import WalletAPI
from filters.filters import IsAdmin
from lexicon.lexicon import botMessages, sureLexicon, addressDelete, errorLexicon

from keyboard.keyboard_factory import Factories
from factories.factory import AdminCallbackFactory

router: Router = Router()


@router.callback_query(
    AdminCallbackFactory.filter(F.page == "deleteAddress"), StateFilter(None), IsAdmin()
)
async def delete_address_menu(
    callback: CallbackQuery, callback_data: AdminCallbackFactory
) -> None:
    sureDelete_copy = sureLexicon.copy()
    sureDelete_copy[callback_data.back_page] = sureDelete_copy.pop("no")
    await callback.message.edit_text(
        text=botMessages["sureDelete"],
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory, sizes=(2,), **sureDelete_copy
        ),
    )


@router.callback_query(
    AdminCallbackFactory.filter(F.page == "yes"), StateFilter(None), IsAdmin()
)
async def delete_address(callback: CallbackQuery, state: FSMContext) -> None:
    state_data = await state.get_data()
    address_id = int(state_data["token"].split("-")[1])
    if await WalletAPI.delete_wallet(wallet_id=address_id):
        await callback.message.edit_text(
            text=botMessages["deleteWallet"].format(
                wallet=state_data[state_data["token"]]
            ),
            reply_markup=await Factories.create_fac_menu(
                AdminCallbackFactory, **addressDelete
            ),
        )
    else:
        callback.message.edit_text(
            text=errorLexicon["deleteWallet"].format(
                wallet=state_data[state_data["token"]]
            ),
            reply_markup=await Factories.create_fac_menu(
                AdminCallbackFactory, **addressDelete
            ),
        )
