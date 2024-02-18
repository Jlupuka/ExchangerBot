from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from databaseAPI.commands.userCommands.admin_commands import check_admin
from databaseAPI.commands.walletAddress_commands import get_all_wallets
from factories.factory import AdminCallbackFactory
from services.cryptoService import CryptoCheck


class IsAdmin(BaseFilter):
    """
    A filter that will check if the user is an administrator or not
    """

    async def __call__(self, message: Message) -> bool:
        """
        A filter that will check if the user is an administrator or not
        :param message: aiogram.filters.Message
        :return: bool
        """
        return await check_admin(user_id=message.from_user.id)


class IsCryptoAddress(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        state_data = await state.get_data()
        return (await CryptoCheck.validate_crypto_address(crypto=state_data['crypto_to'], address=message.text))[0]


class IsNumber(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.text.isdigit()


class CheckState(BaseFilter):
    def __init__(self, pattern: str) -> None:
        self.pattern = pattern

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        state_data: dict[str: str] = await state.get_data()
        return state_data.get(self.pattern, False)


class IsToken(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        token = AdminCallbackFactory.unpack(callback.data).page
        token_in_base = await get_all_wallets()
        return token.upper() in token_in_base
