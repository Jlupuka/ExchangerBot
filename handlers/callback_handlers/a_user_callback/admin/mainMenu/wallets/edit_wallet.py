from aiogram import Router
from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from databaseAPI.commands.walletAddress_commands import WalletAPI
from databaseAPI.models import Wallets
from filters.filters import IsAdmin, IsToken
from lexicon.lexicon import (
    botMessages,
    addressMenu,
    addressEdit,
    statusWork,
    backLexicon,
)

from keyboard.keyboard_factory import Factories
from factories.factory import AdminCallbackFactory

from services.walletService import WalletService
from states.states import FSMPercentEdit

router: Router = Router()


@router.callback_query(
    AdminCallbackFactory.filter(), IsToken(AdminCallbackFactory, check_state=False), IsAdmin()
)
async def print_wallets(
    callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext
) -> None:
    await state.clear()
    await state.update_data(name_net=callback_data.page)
    wallets = await WalletAPI.select_wallets(NameNet=callback_data.page.upper())
    wallets_list: list[tuple[int, str]] = await WalletService.preprocess_wallets_data(
        wallets=wallets
    )
    text, wallets_dict = await WalletService.preprocess_wallets(wallets=wallets_list)
    await state.update_data(**wallets_dict)
    await callback.message.edit_text(
        text=text,
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory,
            back="wallets",
            back_page=callback_data.page,
            sizes=await WalletService.get_size_wallet(
                len_wallet=len(wallets_dict), count_any_button=1
            ),
            **wallets_dict,
        ),
    )


@router.callback_query(
    AdminCallbackFactory.filter(F.page.regexp(r"^TokenId-\d+$")), IsAdmin()
)
async def address_menu(
    callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext
) -> None:
    await state.update_data(token=callback_data.page)
    state_data = await state.get_data()
    await callback.message.edit_text(
        text=botMessages["addressMenu"],
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory,
            back=state_data["name_net"],
            back_page=callback_data.page,
            sizes=(2, 1),
            **addressMenu,
        ),
    )


@router.callback_query(
    AdminCallbackFactory.filter(F.page.in_({"statusWork", "addressEdit"})),
    StateFilter(None, FSMPercentEdit.check_percent),
    IsAdmin(),
)
async def address_edit(
    callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext
) -> None:
    await state.set_state(None)
    state_data = await state.get_data()
    wallet_id = int(state_data["token"].split("-")[1])
    wallet_data: Wallets = (await WalletAPI.select_wallets(Id=wallet_id))[0]
    status_work = wallet_data.Status
    percent = wallet_data.Percent
    address = wallet_data.Address
    address_edit_copy = addressEdit.copy()
    if callback_data.page == "statusWork":
        status_work = (
            await WalletAPI.update_wallet(wallet_id=wallet_id, Status=not status_work)
        ).Status
    address_edit_copy["statusWork"] = statusWork[not status_work]
    await callback.message.edit_text(
        text=botMessages["addressEdit"].format(
            address=address, percent=percent, workType=statusWork[status_work]
        ),
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory,
            back_page=callback_data.back_page,
            back=state_data["token"],
            sizes=(2, 1),
            **address_edit_copy,
        ),
    )


@router.callback_query(
    AdminCallbackFactory.filter(F.page.in_({"percentEdit", "repeatGetPercent"})),
    StateFilter(None, FSMPercentEdit.check_percent),
    IsAdmin(),
)
async def percent_edit(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(FSMPercentEdit.get_percent)
    state_data: dict[str:str] = await state.get_data()
    back_page: str = state_data["token"]
    await callback.message.edit_text(
        text=botMessages["percentEdit"],
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory, back=back_page, back_name=backLexicon["cancelLexicon"]
        ),
    )


@router.callback_query(
    AdminCallbackFactory.filter(F.page == "checkPercent"),
    StateFilter(FSMPercentEdit.check_percent),
    IsAdmin(),
)
async def update_percent_wallet(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(None)
    state_data = await state.get_data()
    wallet_id = int(state_data["token"].split("-")[1])
    percent = state_data["percent"]
    await WalletAPI.update_wallet(wallet_id=wallet_id, Percent=percent)
    await callback.message.edit_text(
        text=botMessages["completedEditPercent"].format(percent=percent),
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory,
            back=state_data["token"],
            back_name=backLexicon["backLexicon"],
        ),
    )
