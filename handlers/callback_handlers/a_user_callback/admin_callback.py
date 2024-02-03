from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from filters.filters import IsAdmin
from lexicon.lexicon import botMessages, startCallbackAdmin

from keyboard.keyboard_factory import create_fac_menu
from factories.factory import AdminCallbackFactory

from magic_filter import F

from services import logger

router: Router = Router()


@router.callback_query(AdminCallbackFactory.filter(F.page == 'main'), IsAdmin())
async def start_handler_admin(callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        text=botMessages['startMessageAdmin'],
        reply_markup=await create_fac_menu(AdminCallbackFactory,
                                           sizes=(2, 2),
                                           back_page=callback_data.page,
                                           **startCallbackAdmin)
    )


@router.callback_query(AdminCallbackFactory.filter(F.page == 'statistics'), IsAdmin())
async def statistics_handler(callback: CallbackQuery, callback_data: AdminCallbackFactory) -> None:
    logger.info(callback_data)
    await callback.message.edit_text(text=botMessages['statisticTextUser'],
                                     reply_markup=await create_fac_menu(AdminCallbackFactory,
                                                                        back=callback_data.back_page))

