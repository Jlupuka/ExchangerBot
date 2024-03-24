from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from factories.factory import MissionCallbackFactory
from filters.filters import IsAdmin
from keyboard.keyboard_factory import Factories

from lexicon.lexicon import botMessages, backLexicon, revokeMission

from states.states import FSMRevokeMission

router: Router = Router()


@router.message(StateFilter(FSMRevokeMission.message), IsAdmin())
async def sure_revoke_mission(message: Message, state: FSMContext, bot: Bot) -> None:
    await state.set_state(FSMRevokeMission.sure)
    await state.update_data(typeRevoke="WithMessage", messageRevoke=message.text)
    message_id: int = (await state.get_data())["messageID"]
    mission_id: int = (await state.get_data())["missionID"]
    await message.answer(
        text=botMessages["sureRevokeWithMessage"].format(
            missionID=mission_id, messageRevoke=message.text
        ),
        reply_markup=await Factories.create_fac_mission(
            MissionCallbackFactory,
            mission_id=mission_id,
            back=mission_id,
            back_name=backLexicon["backLexicon"],
            sizes=(1, 1),
            **revokeMission
        ),
    )
    await bot.delete_message(chat_id=message.from_user.id, message_id=message_id)
    await message.delete()
