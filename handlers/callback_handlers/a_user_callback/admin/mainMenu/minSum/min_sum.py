from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from factories.factory import AdminCallbackFactory
from filters.filters import IsAdmin
from keyboard.keyboard_factory import Factories
from lexicon.lexicon import botMessages, backLexicon
from services.JsonService import JsonService
from states.states import FSMEditMinSum

router: Router = Router()


@router.callback_query(AdminCallbackFactory.filter(F.page == "editMinSum"), IsAdmin())
async def edit_min_sum(
    callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext
) -> None:
    await state.set_state(FSMEditMinSum.get_sum)
    await callback.message.edit_text(
        text=botMessages["editMinSum"],
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory,
            back=callback_data.back_page,
            back_name=backLexicon["backMainMenu"],
        ),
    )


@router.callback_query(
    AdminCallbackFactory.filter(F.page == "yes"),
    IsAdmin(),
    StateFilter(FSMEditMinSum.check_sure),
)
async def update_min_sum(callback: CallbackQuery, state: FSMContext) -> None:
    json_data = await JsonService.read_json()
    minSum = (await state.get_data())["minSum"]
    json_data["minSum"] = minSum
    await JsonService.save_json(data=json_data)
    await callback.message.edit_text(
        text=botMessages["updateMinSum"].format(updateMinSum=minSum),
        reply_markup=await Factories.create_fac_menu(
            AdminCallbackFactory, back="settings"
        ),
    )
    await state.clear()
