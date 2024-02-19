from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from databaseAPI.commands.userCommands.admin_commands import check_admin
from databaseAPI.commands.walletAddress_commands import get_all_name_net_wallets
from factories.factory import AdminCallbackFactory
from services.cryptoService import CryptoCheck
from services.walletService import check_number


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
    """
    Checks if the entered message is a valid cryptocurrency wallet address
    """
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        """
        Checks if the entered message is a valid cryptocurrency wallet address
        :param message: (aiogram.types.Message) User message
        :param state: (aiogram.fsm.context.FSMContext) State machine
        :return: (bool) Result on whether the address is a cryptocurrency wallet or not
        """
        state_data = await state.get_data()
        return (await CryptoCheck.validate_crypto_address(crypto=state_data['crypto_to'], address=message.text))[0]


class CheckState(BaseFilter):
    """
    Check if there is such an argument at the moment of the filter call
    """
    def __init__(self, pattern: str) -> None:
        """
        Takes an argument to check if it is in the FSM
        :param pattern: (str) Argument to be tested
        """
        self.pattern = pattern

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        """
        Check if there is such an argument at the moment of the filter call
        :param message: (aiogram.types.Message) User message
        :param state: (aiogram.fsm.context.FSMContext) State machine
        :return: (bool) Result to check if there is or not
        """
        state_data: dict[str: str] = await state.get_data()
        return state_data.get(self.pattern, False)


class IsToken(BaseFilter):
    """
    Checks if such currency (its brief designation) exists in the database
    """
    async def __call__(self, callback: CallbackQuery) -> bool:
        """
        Checks if such currency (its brief designation) exists in the database
        :param callback: (aiogram.types.CallbackQuery)
        :return: (bool) Result to exist or not
        """
        token = AdminCallbackFactory.unpack(callback.data).page
        token_in_base = await get_all_name_net_wallets()
        return token.upper() in token_in_base


class IsDigitPercent(BaseFilter):
    """
    Checks whether the entered message is an integer or a real number
    """
    async def __call__(self, message: Message) -> bool:
        """
        Checks whether the entered message is an integer or a real number
        :param message: (aiogram.types.Message) User message
        :return: The result on what is or is not
        """
        return await check_number(input_str=message.text)
