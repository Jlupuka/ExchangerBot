from typing import Any

from aiogram import Router, F
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from keyboard.keyboard_factory import Factories
from lexicon.lexicon import errorLexicon

from dataTemplates.data_templates import MnemonicData, SendData
from factories.factory import MissionCallbackFactory
from filters.filters import IsAdmin
from states.states import FSMSendFunds

router: Router = Router()


@router.callback_query(
    MissionCallbackFactory.filter(F.page == "send"),
    IsAdmin(checkAdminWork=True),
    StateFilter(FSMSendFunds.check_sure),
)
async def error_send_funds(
    callback: CallbackQuery, callback_data: MissionCallbackFactory, state: FSMContext
) -> None:
    data: dict[str:Any] = await state.get_data()
    mnemonic_data: MnemonicData = MnemonicData(**data["MnemonicData"])
    send_data: SendData = SendData(**data["SendData"])
    await callback.message.edit_text(
        text=errorLexicon["sendFunds"].format(
            userAddress=send_data.user_address,
            adminAddress=mnemonic_data.address,
            balance=mnemonic_data.balance,
            token=mnemonic_data.token,
            amount=send_data.amount,
        ),
        reply_markup=await Factories.create_fac_mission(
            MissionCallbackFactory,
            mission_id=callback_data.mission_id,
            back=callback_data.mission_id,
        ),
    )
