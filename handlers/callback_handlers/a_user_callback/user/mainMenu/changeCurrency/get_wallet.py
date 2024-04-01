from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from filters.filters import IsToken
from lexicon.lexicon import botMessages, writeFiatOrCrypto

from keyboard.keyboard_factory import Factories
from factories.factory import UserCallbackFactory
from services.stateService import StateService

from states.states import FSMFiatCrypto, FSMCryptoFiat, FSMCryptoCrypto

router: Router = Router()


@router.callback_query(
    UserCallbackFactory.filter(),
    IsToken(UserCallbackFactory),
    StateFilter(
        FSMFiatCrypto.currency_to,
        FSMCryptoFiat.currency_to,
        FSMCryptoCrypto.currency_to,
    ),
)
async def get_wallet(
    callback: CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext
) -> None:
    await state.update_data(currency_to=callback_data.page.upper())
    state_data: dict[str:str] = await state.get_data()
    await StateService.set_states(
        state_name="requisites", state_data=state_data, state=state
    )
    typeTransaction = state_data["typeTransaction"].split("-")[1]
    await callback.message.edit_text(
        text=botMessages["getAddressCrypto"].format(
            typeTransaction=writeFiatOrCrypto[typeTransaction]
        ),
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory, back=callback_data.back_page, back_page="main"
        ),
    )


@router.callback_query(
    UserCallbackFactory.filter(F.page.in_({"repeat", "no"})),
    StateFilter(
        FSMFiatCrypto.check_validate,
        FSMCryptoFiat.check_validate,
        FSMCryptoCrypto.check_validate,
    ),
)
async def repeat_get_wallet(callback: CallbackQuery, state: FSMContext) -> None:
    state_data: dict[str:str] = await state.get_data()
    typeTransaction = state_data["typeTransaction"].split("-")[1]
    await StateService.set_states(
        state_name="requisites", state_data=await state.get_data(), state=state
    )
    await callback.message.edit_text(
        text=botMessages["getAddressCrypto"].format(
            typeTransaction=writeFiatOrCrypto[typeTransaction]
        ),
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory, back=state_data["typeTransaction"], back_page="main"
        ),
    )
