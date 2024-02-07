from aiogram import Router
from aiogram.types import CallbackQuery

from factories.factory import UserCallbackFactory, AdminCallbackFactory
from services import logger

router: Router = Router()


@router.callback_query(UserCallbackFactory.filter())
async def send_any_message(callback: CallbackQuery, callback_data: UserCallbackFactory) -> None:
    await callback.answer('Что?')
    logger.info(callback_data)


@router.callback_query(AdminCallbackFactory.filter())
async def send_any_message(callback: CallbackQuery, callback_data: AdminCallbackFactory) -> None:
    await callback.answer('Что?')
    logger.info(callback_data)


