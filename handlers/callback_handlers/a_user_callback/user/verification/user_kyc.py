from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile

from factories.factory import UserCallbackFactory
from lexicon.lexicon import botMessages
from services.userService import UserService
from states.states import FSMVerify

router: Router = Router()


@router.callback_query(UserCallbackFactory.filter(F.page == "verify"))
async def user_verify(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(FSMVerify.get_photo)
    await callback.message.delete()
    verif_number: int = await UserService.verif_number()
    photo: FSInputFile = FSInputFile("src/img/verifExample.png")
    await callback.message.answer_photo(
        photo=photo, caption=botMessages["verif"].format(verifNumber=verif_number)
    )
    await state.update_data(verifNumber=verif_number)
