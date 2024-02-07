from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from factories.factory import UserCallbackFactory
from keyboard.keyboard_factory import create_fac_menu

from lexicon.lexicon import botMessages, startCallbackUser, checkCorrectAddress
from services import logger
from states.states import FSMFiatCrypto

router = Router()


@router.message(Command(commands=['start', 'cancel']))
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text=botMessages['startMessageAdmin'],
        reply_markup=await create_fac_menu(UserCallbackFactory,
                                           back_page='main',
                                           sizes=(2, 1, 2), **startCallbackUser)
    )


@router.message(StateFilter(FSMFiatCrypto.requisites))
async def add_mission(message: Message, state: FSMContext) -> None:
    await state.update_data(requisites=message.text)
    logger.debug(await state.get_data())
    await message.answer(text=botMessages['checkCorrectAddress'].format(message.text),
                         reply_markup=await create_fac_menu(UserCallbackFactory,
                                                            back='main',
                                                            sizes=(2, 1),
                                                            **checkCorrectAddress
                                                            ))
