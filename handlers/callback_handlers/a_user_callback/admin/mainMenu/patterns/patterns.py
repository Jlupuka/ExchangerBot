from typing import Any

from aiogram import Router
from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from filters.filters import IsAdmin, IsToken
from lexicon.lexicon import (
    botMessages,
    patternsMenu,
    backLexicon,
    errorLexicon,
    yesLexicon,
)

from keyboard.keyboard_factory import Factories
from factories.factory import AdminCallbackFactory

from services.JsonService import JsonService

from services.walletService import WalletService
from states.states import FSMEditPatterns

router: Router = Router()


@router.callback_query(AdminCallbackFactory.filter(F.page == "editPatterns"), IsAdmin())
async def choice_patterns(
    callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext
) -> None:
    await state.set_state(FSMEditPatterns.choice_pattern)
    work_patterns = await JsonService.preprocess_patterns_for_button()
    patterns_text = await JsonService.preprocess_patterns_for_text()
    sizes: tuple[int, ...] = await WalletService.get_size_wallet(
        len_wallet=len(work_patterns), count_any_button=2
    )
    patternsMenu_copy = patternsMenu.copy()
    await callback.message.edit_text(
        text=botMessages["editPatterns"].format(patterns=patterns_text),
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory,
            back_page=callback_data.page,
            back="settings",
            sizes=sizes,
            **work_patterns,
            **patternsMenu_copy,
        ),
    )


@router.callback_query(AdminCallbackFactory.filter(F.page == "addPattern"), IsAdmin())
async def add_pattern(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(FSMEditPatterns.get_token_name)
    await callback.message.edit_text(
        text=botMessages["getTokenPattern"],
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory,
            back="settings",
            back_name=backLexicon["cancelLexicon"],
        ),
    )


@router.callback_query(
    AdminCallbackFactory.filter(F.page == "yes"),
    IsAdmin(),
    StateFilter(FSMEditPatterns.check_sure),
)
async def patterns(callback: CallbackQuery, state: FSMContext) -> None:
    state_data = await state.get_data()
    work_patterns = await JsonService.get_specific_data(name_data="patterns")
    if state_data["token"] not in work_patterns:
        work_patterns[state_data["token"]] = state_data["pattern"]
        await JsonService.save_token_patterns(patterns=work_patterns)
        patterns_button = await JsonService.preprocess_patterns_for_button()
        patterns_text = await JsonService.preprocess_patterns_for_text()
        sizes: tuple[int, ...] = await WalletService.get_size_wallet(
            len_wallet=len(work_patterns), count_any_button=2
        )
        patternsMenu_copy = patternsMenu.copy()
        await callback.message.edit_text(
            text=botMessages["addPatterns"].format(patterns=patterns_text),
            reply_markup=await Factories.create_fac_menu(
                AdminCallbackFactory,
                back="settings",
                sizes=sizes,
                **patterns_button,
                **patternsMenu_copy,
            ),
        )
        await state.clear()
    else:
        await callback.message.edit_text(
            text=errorLexicon["repeatPattern"],
            reply_markup=await Factories.create_fac_menu(
                AdminCallbackFactory, back="settings"
            ),
        )


@router.callback_query(
    AdminCallbackFactory.filter(),
    IsToken(AdminCallbackFactory, check_state=FSMEditPatterns.choice_pattern),
    IsAdmin(),
    StateFilter(FSMEditPatterns.choice_pattern),
)
async def verification_delete(
    callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext
) -> None:
    await state.update_data(patterns=callback_data.page)
    await callback.message.edit_text(
        text=botMessages["verificationDeletePattern"].format(
            pattern=callback_data.page
        ),
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory, back=callback_data.back_page, **yesLexicon
        ),
    )


@router.callback_query(
    AdminCallbackFactory.filter(F.page == "yes"),
    IsAdmin(),
    StateFilter(FSMEditPatterns.choice_pattern),
)
async def delete_pattern(callback: CallbackQuery, state: FSMContext) -> None:
    state_data: dict[str, Any] = await state.get_data()
    work_patterns = await JsonService.get_specific_data(name_data="patterns")
    token_delete = work_patterns.pop(state_data["patterns"])
    await JsonService.save_token_patterns(patterns=work_patterns)
    patterns_button = await JsonService.preprocess_patterns_for_button()
    patterns_text = await JsonService.preprocess_patterns_for_text()
    sizes: tuple[int, ...] = await WalletService.get_size_wallet(
        len_wallet=len(work_patterns), count_any_button=2
    )
    patternsMenu_copy = patternsMenu.copy()
    await callback.message.edit_text(
        text=botMessages["deletePatterns"].format(
            deletePattern=f"{state_data['patterns']} - {token_delete}",
            patterns=patterns_text,
        ),
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory,
            back="settings",
            sizes=sizes,
            **patterns_button,
            **patternsMenu_copy,
        ),
    )
