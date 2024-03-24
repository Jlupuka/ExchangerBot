from aiogram import Router, F, Bot
from aiogram.enums import ContentType
from aiogram.types import Message, PhotoSize, FSInputFile
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from config import config

from keyboard.keyboard_factory import Factories

from lexicon.lexicon import botMessages, errorLexicon, kycVerifyCheckAdmin

from states.states import FSMVerify

router: Router = Router()


@router.message(F.content_type == ContentType.PHOTO, StateFilter(FSMVerify.get_photo))
async def verif_user(message: Message, state: FSMContext, bot: Bot) -> None:
    verif_number: int = (await state.get_data())["verifNumber"]
    admin_id: int = config.load_config().AdminId.ADMINID[0]
    photo: PhotoSize = message.photo[0]
    await bot.send_photo(
        chat_id=admin_id,
        photo=photo.file_id,
        caption=botMessages["sendVerifPhotoAdmin"].format(
            userID=message.from_user.id,
            verifNumber=verif_number,
        ),
        reply_markup=await Factories.create_kyc_fac(
            user_id=message.from_user.id,
            verif_number=verif_number,
            **kycVerifyCheckAdmin
        ),
    )
    await message.answer(text=botMessages["sendVerifPhoto"])
    await state.clear()


@router.message(StateFilter(FSMVerify.get_photo))
async def error_verif_user(message: Message, state: FSMContext) -> None:
    photo: FSInputFile = FSInputFile("src/img/verifExample.png")
    verif_number: int = (await state.get_data())["verifNumber"]
    await message.answer_photo(
        photo=photo,
        caption=errorLexicon["errorSendVerifPhoto"].format(
            contentType=message.content_type, numberVerif=verif_number
        ),
    )
