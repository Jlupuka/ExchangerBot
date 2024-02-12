from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from databaseAPI.commands.userCommands.admin_commands import check_admin
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


class IsEthBtcAddress(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        state_data = await state.get_data()
        match state_data['crypto_to']:
            case 'btc':
                btc = await CryptoCheck.is_valid_btc_address(address=message.text)
                return btc
            case 'eth':
                eth = await CryptoCheck.is_valid_eth_address(address=message.text)
                return eth
            case _:
                return False


class IsNumber(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.text.isdigit()
