from typing import Type, Union

from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from databaseAPI.commands.walletAddress_commands import WalletAPI
from factories.factory import AdminCallbackFactory, UserCallbackFactory
from services.cryptoService import CryptoCheck
from services.dataService import JsonService
from services.walletService import WalletService


class IsAdmin(BaseFilter):
    """
    A filter that will check if the user is an administrator or not
    """

    def __init__(self, checkAdminWork: bool = False) -> None:
        self.checkAdminWork = checkAdminWork

    async def __call__(
        self, update: Union[Message | CallbackQuery], state: FSMContext
    ) -> bool:
        """
        A filter that will check if the user is an administrator or not
        :param update: aiogram.filters.Message
        :return: bool
        """
        is_admin: bool = (await state.get_data())["userIsAdmin"]
        return is_admin


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
        return (
            await CryptoCheck.validate_crypto_address(
                token=state_data["currency_to"], address=message.text
            )
        )[0]


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
        state_data: dict[str:str] = await state.get_data()
        return state_data.get(self.pattern, False)


class IsToken(BaseFilter):
    def __init__(
        self, factory: Type[AdminCallbackFactory] | Type[UserCallbackFactory]
    ) -> None:
        self.factory = factory

    """
    Checks if such currency (its brief designation) exists in the database
    """

    async def __call__(self, callback: CallbackQuery) -> bool:
        """
        Checks if such currency (its brief designation) exists in the database
        :param callback: (aiogram.types.CallbackQuery)
        :return: (bool) Result to exist or not
        """
        token = self.factory.unpack(callback.data).page
        token_in_base = await WalletAPI.get_all_name_net_wallets()
        return token.upper() in token_in_base


class IsDigit(BaseFilter):
    """
    Checks whether the entered message is an integer or a real number
    """

    def __init__(self, check_min: bool = False, check_percent: bool = False) -> None:
        self.check_min = check_min
        self.check_percent = check_percent

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        """
        Checks whether the entered message is an integer or a real number
        :param message: (aiogram.types.Message) User message
        :param state: (aiogram.fsm.context.FSMContext) State machine
        :return: The result on what is or is not
        """
        is_number = await WalletService.check_number(input_str=message.text)
        if is_number:
            if self.check_min is False:
                return (
                    1.01 <= float(message.text) <= 1.70
                    if self.check_percent
                    else is_number
                )
            state_data = await state.get_data()
            min_sum = await JsonService.get_specific_data(name_data="minSum")
            return (
                await CryptoCheck.transaction_amount(
                    amount=float(message.text),
                    currency_to="RUB",
                    currency_from=state_data["currency_from"].upper(),
                )
                >= min_sum
            )
        return False
