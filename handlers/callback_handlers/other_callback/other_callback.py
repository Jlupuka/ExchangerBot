from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from factories.factory import UserCallbackFactory, AdminCallbackFactory, MissionCallbackFactory
from services import logger

router: Router = Router()


@router.callback_query(UserCallbackFactory.filter())
async def send_any_message(callback: CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext) -> None:
    await callback.answer('Что?')
    logger.info("userID=%s, callbackData=(%s), state=%s", callback.from_user.id, callback_data, await state.get_state())


@router.callback_query(AdminCallbackFactory.filter())
async def send_any_message(callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext) -> None:
    await callback.answer('Что?')
    logger.info("userID=%s, callbackData=(%s), state=%s", callback.from_user.id, callback_data, await state.get_state())


@router.callback_query(MissionCallbackFactory.filter())
async def send_any_message(callback: CallbackQuery, callback_data: AdminCallbackFactory, state: FSMContext) -> None:
    await callback.answer('Что?')
    logger.info("userID=%s, callbackData=(%s), state=%s", callback.from_user.id, callback_data, await state.get_state())
