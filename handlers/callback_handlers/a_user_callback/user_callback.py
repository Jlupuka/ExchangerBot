from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from lexicon.lexicon import botMessages, startCallbackUser, profileUser, listMissionsUser

from keyboard.keyboard_factory import create_fac_menu
from factories.factory import MainCallbackFactory

from magic_filter import F

router: Router = Router()


@router.callback_query(MainCallbackFactory.filter(F.page == 'main'))
async def main_handler(callback: CallbackQuery, state: FSMContext, callback_data: MainCallbackFactory) -> None:
    await state.clear()
    await callback.message.edit_text(
        text=botMessages['startMessageUser'],
        reply_markup=await create_fac_menu(back_page=callback_data.page, sizes=(2, 1, 2), **startCallbackUser)
    )


@router.callback_query(MainCallbackFactory.filter(F.page == 'info'))
async def info_handler(callback: CallbackQuery) -> None:
    # TODO: Сделать информационный текст о боте
    pass


@router.callback_query(MainCallbackFactory.filter(F.page == 'profile'))
async def profile_handler(callback: CallbackQuery, callback_data: MainCallbackFactory) -> None:
    await callback.message.edit_text(text=botMessages['profileTextUser'],
                                     reply_markup=await create_fac_menu(back_page=callback_data.page,
                                                                        back=callback_data.back_page,
                                                                        sizes=(2,), **profileUser))


@router.callback_query(MainCallbackFactory.filter(F.page == 'statistics'))
async def statistics_handler(callback: CallbackQuery, callback_data: MainCallbackFactory) -> None:
    await callback.message.edit_text(text=botMessages['statisticTextUser'],
                                     reply_markup=await create_fac_menu(back_page='main',
                                                                        back=callback_data.back_page))


@router.callback_query(MainCallbackFactory.filter(F.page == 'missions'))
async def missions_handler(callback: CallbackQuery, callback_data: MainCallbackFactory) -> None:
    await callback.message.edit_text(text=botMessages['missionsTextUser'],
                                     reply_markup=await create_fac_menu(back_page=callback_data.page,
                                                                        back=callback_data.back_page,
                                                                        sizes=(3,),
                                                                        **listMissionsUser))


@router.callback_query(MainCallbackFactory.filter(F.page == 'accepted'))
async def accepted_missions_handler(callback: CallbackQuery, callback_data: MainCallbackFactory) -> None:
    # TODO: Реализовать запрос к БД, для получения данных по заявкам. Так же сделать обработку\очистку
    #  данных под бота тг
    await callback.message.edit_text(text=botMessages['informationMissions'],
                                     reply_markup=await create_fac_menu(back_page='profile',
                                                                        back=callback_data.back_page,
                                                                        sizes=(3,),
                                                                        **listMissionsUser))


@router.callback_query(MainCallbackFactory.filter(F.page == 'completed'))
async def completed_missions_handler(callback: CallbackQuery, callback_data: MainCallbackFactory) -> None:
    # TODO: Реализовать запрос к БД, для получения данных по заявкам. Так же сделать обработку\очистку
    #  данных под бота тг
    await callback.message.edit_text(text=botMessages['informationMissions'],
                                     reply_markup=await create_fac_menu(back_page='profile',
                                                                        back=callback_data.back_page,
                                                                        sizes=(3,),
                                                                        **listMissionsUser))


@router.callback_query(MainCallbackFactory.filter(F.page == 'waiting'))
async def waiting_missions_handler(callback: CallbackQuery, callback_data: MainCallbackFactory) -> None:
    # TODO: Реализовать запрос к БД, для получения данных по заявкам. Так же сделать обработку\очистку
    #  данных под бота тг
    await callback.message.edit_text(text=botMessages['informationMissions'],
                                     reply_markup=await create_fac_menu(back_page='profile',
                                                                        back=callback_data.back_page,
                                                                        sizes=(3,),
                                                                        **listMissionsUser))
