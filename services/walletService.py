import random
import re
from typing import Sequence, Any

from databaseAPI.commands.walletAddress_commands import WalletAPI
from databaseAPI.models import Wallets
from lexicon.lexicon import cryptoSymbol


class WalletService:
    @staticmethod
    async def get_wallets(*args: str, **kwargs: dict[str:Any]) -> dict[str:str]:
        """
        Returns all short names of currencies that exist in the database
        :return: (dict[str]) key is the name in lower case, value - in upper case
        """
        wallets_data: set[Any] = set(await WalletAPI.select_wallets(*args, **kwargs))
        return {
            wallet.lower(): f'{wallet.upper()} {cryptoSymbol["symbol"]}'
            for wallet in sorted(wallets_data)
        }

    @staticmethod
    async def get_size_wallet(
        len_wallet: int, count_any_button: int = 0
    ) -> tuple[int, ...]:
        """
        Returns a tuple of numbers, where the numbers indicate how many buttons will be on one line
        :param len_wallet: (int) how many main buttons there are
        :param count_any_button: (int, default=0) how many side buttons
        :return: (tuple[int]) tuple with numbers, where numbers are the number of buttons in one line
        """
        result_wallet_size = list()
        for index in range(len_wallet):
            if index % 3 == 1:
                result_wallet_size.append(2)
            elif index % 3 == 2:
                result_wallet_size.append(1)
        return tuple(result_wallet_size + [1] * count_any_button)

    @staticmethod
    async def preprocess_wallets(
        wallets: list[tuple[int, str]]
    ) -> tuple[str, dict[str:str]]:
        """
        Converts wallet data to text for easier to understand information and returns a dictionary to create buttons
        :param wallets: (list[tuple[int, str]]) list where values are a tuple with wallet data - id, address
        :return: (tuple[str, dict[str: str]])
        """
        result_text = str()
        result_dict = dict()
        line_feed = "\n"
        for index in range(len_wallets := len(wallets)):
            result_text += (
                f"{wallets[index][0]}. <code>{wallets[index][1]}"
                f'</code>{"" if index == len_wallets - 1 else line_feed}'
            )
            result_dict[f"TokenId-{wallets[index][0]}"] = (
                f"🆔 {wallets[index][0]} | "
                f"💳 {wallets[index][1][:6]}...{wallets[index][1][-4:]}"
            )
        return "\n".join(sorted(result_text.split("\n"))), {
            address_id: result_dict[address_id] for address_id in sorted(result_dict)
        }

    @staticmethod
    async def check_number(input_str: str) -> bool:
        """
        Checks whether the text is an integer or a real number
        :param input_str: (str) text
        :return: (bool) verification result
        """
        if re.match(r"^\d*[.,]?\d+$", input_str):
            return True
        return False

    @staticmethod
    async def random_wallet(name_net: str) -> Wallets:
        wallets: Sequence[Wallets] = await WalletAPI.get_wallets_for_mission(
            name_net=name_net
        )
        return random.choice(wallets)

    @staticmethod
    async def preprocess_wallets_data(
        wallets: Sequence[Wallets],
    ) -> list[tuple[int, str]]:
        return [(wallet.Id, wallet.Address) for wallet in wallets]
