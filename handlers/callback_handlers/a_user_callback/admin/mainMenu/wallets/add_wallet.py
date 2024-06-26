from aiogram import Router
from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from databaseAPI.commands.walletAddress_commands import WalletAPI
from databaseAPI.models.models import TypesWallet

from filters.filters import IsAdmin
from lexicon.lexicon import (
    botMessages,
    checkCorrectAddWallet,
    successfullyMessage,
    errorLexicon,
    backLexicon,
)

from keyboard.keyboard_factory import Factories
from factories.factory import AdminCallbackFactory
from states.states import FSMAddWallet

router: Router = Router()


@router.callback_query(
    AdminCallbackFactory.filter(F.page == "no"),
    StateFilter(FSMAddWallet.type_wallet),
    IsAdmin(),
)
@router.callback_query(AdminCallbackFactory.filter(F.page == "addWallet"), IsAdmin())
async def add_wallet_handler(
    callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext
) -> None:
    await state.clear()
    await state.set_state(FSMAddWallet.currency_to)
    await callback.message.edit_text(
        text=botMessages["addWallet"],
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory, back=callback_data.back_page
        ),
    )


@router.callback_query(AdminCallbackFactory.filter(F.page == "repeat"), IsAdmin())
async def repeat_get_wallet_address(callback: CallbackQuery, state: FSMContext) -> None:
    now_state: str = await state.get_state()
    text = "aaa"
    match now_state:
        case FSMAddWallet.type_wallet:
            text: str = botMessages["getNameNet"]
            await state.set_state(FSMAddWallet.address)
        case FSMAddWallet.address:
            text: str = botMessages["addWallet"]
            await state.set_state(FSMAddWallet.currency_to)
        case FSMAddWallet.mnemonic:
            token: str = (await state.get_data())["currency_to"].upper()
            text: str = botMessages["getMnemonicNet"].format(token=token)
    await callback.message.edit_text(
        text=text,
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory, back="wallets", back_name=backLexicon["backLexicon"]
        ),
    )


@router.callback_query(
    AdminCallbackFactory.filter(F.page.in_({"crypto", "rub"})),
    StateFilter(FSMAddWallet.type_wallet),
    IsAdmin(),
)
async def check_add_wallet_data(
    callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext
) -> None:
    await state.update_data(walletType=callback_data.page)
    await state.set_state(FSMAddWallet.check_correct)
    state_data: dict[str:str] = await state.get_data()
    name_net: str = state_data["currency_to"]
    address: str = state_data["address"]
    wallet_type: str = callback_data.page.upper()
    await callback.message.edit_text(
        text=botMessages["checkDataAddWallet"].format(
            nameNet=name_net, address=address, walletType=wallet_type
        ),
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory,
            back="wallets",
            back_name=backLexicon["backLexicon"],
            sizes=(2, 1),
            **checkCorrectAddWallet,
        ),
    )


@router.callback_query(
    AdminCallbackFactory.filter(F.page == "yes"),
    StateFilter(FSMAddWallet.check_correct),
    IsAdmin(),
)
async def add_wallet(callback: CallbackQuery, state: FSMContext) -> None:
    state_data: dict[str:str] = await state.get_data()
    name_net: str = state_data["currency_to"].upper()
    address: str = state_data["address"]
    wallet_type: TypesWallet = TypesWallet[state_data["walletType"]]
    response = await WalletAPI.add_wallet(
        name_net=name_net, address=address, type_wallet=wallet_type
    )
    if response:
        await callback.message.edit_text(
            text=successfullyMessage["addWallet"].format(
                nameNet=name_net, address=address, walletType=wallet_type.value
            ),
            reply_markup=await Factories.create_fac_menu(
                AdminCallbackFactory,
                back="wallets",
                back_name=backLexicon["backLexicon"],
            ),
        )
    else:
        await callback.message.edit_text(
            text=errorLexicon["WalletExist"].format(
                nameNet=name_net, address=address, walletType=wallet_type.value
            ),
            reply_markup=await Factories.create_fac_menu(
                AdminCallbackFactory,
                back="wallets",
                back_name=backLexicon["backLexicon"],
            ),
        )
    await state.clear()
