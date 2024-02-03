from aiogram import Router
from aiogram.types import CallbackQuery

router: Router = Router()


@router.callback_query()
async def send_any_message(callback: CallbackQuery) -> None:
    await callback.answer('Что?')
