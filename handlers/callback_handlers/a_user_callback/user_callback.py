from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from lexicon.lexicon import botMessages, startCallbackUser, profileUser, listMissionsUser, choiceToken, choiceMethod

from keyboard.keyboard_factory import create_fac_menu
from factories.factory import UserCallbackFactory

from magic_filter import F

from services import logger
from states.states import FSMFiatCrypto

router: Router = Router()


@router.callback_query(UserCallbackFactory.filter(F.page == 'main'))
async def main_handler(callback: CallbackQuery, state: FSMContext, callback_data: UserCallbackFactory) -> None:
    await state.clear()
    await callback.message.edit_text(
        text=botMessages['startMessageUser'],
        reply_markup=await create_fac_menu(UserCallbackFactory,
                                           back_page=callback_data.page,
                                           sizes=(2, 1, 2), **startCallbackUser)
    )


@router.callback_query(UserCallbackFactory.filter(F.page == 'info'))
async def info_handler(callback: CallbackQuery) -> None:
    # TODO: Сделать информационный текст о боте
    pass


@router.callback_query(UserCallbackFactory.filter(F.page == 'profile'))
async def profile_handler(callback: CallbackQuery, callback_data: UserCallbackFactory) -> None:
    await callback.message.edit_text(text=botMessages['profileTextUser'],
                                     reply_markup=await create_fac_menu(UserCallbackFactory,
                                                                        back_page=callback_data.page,
                                                                        back='main',
                                                                        sizes=(2,), **profileUser))


@router.callback_query(UserCallbackFactory.filter(F.page == 'statistics'))
async def statistics_handler(callback: CallbackQuery, callback_data: UserCallbackFactory) -> None:
    await callback.message.edit_text(text=botMessages['statisticTextUser'],
                                     reply_markup=await create_fac_menu(UserCallbackFactory,
                                                                        back_page='main',
                                                                        back=callback_data.back_page))


@router.callback_query(UserCallbackFactory.filter(F.page == 'missions'))
async def missions_handler(callback: CallbackQuery, callback_data: UserCallbackFactory) -> None:
    await callback.message.edit_text(text=botMessages['missionsTextUser'],
                                     reply_markup=await create_fac_menu(UserCallbackFactory,
                                                                        back_page=callback_data.page,
                                                                        back='profile',
                                                                        sizes=(3,),
                                                                        **listMissionsUser))


@router.callback_query(UserCallbackFactory.filter(F.page == 'accepted'))
async def accepted_missions_handler(callback: CallbackQuery, callback_data: UserCallbackFactory) -> None:
    # TODO: Реализовать запрос к БД, для получения данных по заявкам. Так же сделать обработку\очистку
    #  данных под бота тг
    await callback.message.edit_text(text=botMessages['informationMissions'],
                                     reply_markup=await create_fac_menu(UserCallbackFactory,
                                                                        back_page='missions',
                                                                        back=callback_data.back_page,
                                                                        sizes=(3,),
                                                                        **listMissionsUser))


@router.callback_query(UserCallbackFactory.filter(F.page == 'completed'))
async def completed_missions_handler(callback: CallbackQuery, callback_data: UserCallbackFactory) -> None:
    # TODO: Реализовать запрос к БД, для получения данных по заявкам. Так же сделать обработку\очистку
    #  данных под бота тг
    await callback.message.edit_text(text=botMessages['informationMissions'],
                                     reply_markup=await create_fac_menu(UserCallbackFactory,
                                                                        back_page='missions',
                                                                        back=callback_data.back_page,
                                                                        sizes=(3,),
                                                                        **listMissionsUser))


@router.callback_query(UserCallbackFactory.filter(F.page == 'waiting'))
async def waiting_missions_handler(callback: CallbackQuery, callback_data: UserCallbackFactory) -> None:
    # TODO: Реализовать запрос к БД, для получения данных по заявкам. Так же сделать обработку\очистку
    #  данных под бота тг
    await callback.message.edit_text(text=botMessages['informationMissions'],
                                     reply_markup=await create_fac_menu(UserCallbackFactory,
                                                                        back_page='missions',
                                                                        back=callback_data.back_page,
                                                                        sizes=(3,),
                                                                        **listMissionsUser))


@router.callback_query(UserCallbackFactory.filter(F.page == 'rub-crypto'))
async def choice_rub_crypto(callback: CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(FSMFiatCrypto.crypto_to)
    await callback.message.edit_text(text=botMessages['choiceToken'],
                                     reply_markup=await create_fac_menu(UserCallbackFactory,
                                                                        back_page=callback_data.page,
                                                                        back=callback_data.back_page,
                                                                        **choiceToken))


@router.callback_query(UserCallbackFactory.filter(F.page.in_({'eth', 'btc'})),
                       StateFilter(FSMFiatCrypto.crypto_to))
async def get_wallet(callback: CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext) -> None:
    await state.update_data(crypto_to=callback_data.page)
    logger.debug(await state.get_data())
    await state.set_state(FSMFiatCrypto.requisites)
    await callback.message.edit_text(text=botMessages['getAddressCrypto'],
                                     reply_markup=await create_fac_menu(UserCallbackFactory,
                                                                        back=callback_data.back_page,
                                                                        back_page='main'))


@router.callback_query(UserCallbackFactory.filter(F.page.in_({'repeat', 'no'})),
                       StateFilter(FSMFiatCrypto.check_validate))
async def repeat_get_wallet(callback: CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext) -> None:
    logger.debug(await state.get_data())
    await state.set_state(FSMFiatCrypto.requisites)
    await callback.message.edit_text(text=botMessages['getAddressCrypto'],
                                     reply_markup=await create_fac_menu(UserCallbackFactory,
                                                                        back='rub-crypto',
                                                                        back_page='main'))


@router.callback_query(UserCallbackFactory.filter(F.page == 'yes'), StateFilter(FSMFiatCrypto.check_validate))
async def choice_method_get_sum(callback: CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext) -> None:
    await state.set_state(FSMFiatCrypto.method)
    await callback.message.edit_text(text=botMessages['choiceMethod'],
                                     reply_markup=await create_fac_menu(UserCallbackFactory,
                                                                        back_page=callback_data.page,
                                                                        back='main',
                                                                        sizes=(3, 1),
                                                                        back_name=botMessages['cancelLexicon'],
                                                                        **choiceMethod))

# TODO: дальше смысла пользовательскую часть писать нет. надо написать админскую часть,
#  где можно добавлять и редактировать валюту и ее процент
