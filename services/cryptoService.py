import re
from typing import Coroutine, Any

import aiohttp

from CastomExceptions.castomException import NotFoundCryptoToken, BadRequest
from services import logger


class CryptoCheck:
    @staticmethod
    async def is_valid_eth_address(address: str) -> bool:
        """
        Checks if the address is an Ethereum crypto wallet
        :param address: (str) address crypto wallet
        :return: True | False
        """
        pattern = re.compile(r'^0x[a-fA-F0-9]{40}$')
        return bool(pattern.match(address))

    @staticmethod
    async def is_valid_btc_address(address: str) -> bool:
        """
        Checks if the address is a Bitcoin crypto wallet
        :param address: (str) address crypto wallet
        :return: True | False
        """
        pattern = re.compile(r'^[13][a-zA-Z0-9]{26,35}$')
        return bool(pattern.match(address))

    @staticmethod
    async def btc(wallet_address: str) -> Coroutine[Any, Any, dict]:
        """
        Gets bitcoin cryptocurrency wallet balance
        :param wallet_address: (str) address crypto wallet
        :return: (Coroutine[Any, Any, dict]) Cryptocurrency data dictionary
        """
        url = 'https://api.blockcypher.com/v1/btc/main/addrs/{wallet_address}/balance'
        async with aiohttp.ClientSession() as session:
            async with session.get(url.format(wallet_address=wallet_address)) as response:
                return await response.json()

    @staticmethod
    async def eth(wallet_address: str) -> Coroutine[Any, Any, dict]:
        """
        Gets ethereum cryptocurrency wallet balance
        :param wallet_address: (str) address crypto wallet
        :return: (Coroutine[Any, Any, dict]) Cryptocurrency data dictionary
        """
        url = 'https://api.blockcypher.com/v1/eth/main/addrs/{wallet_address}/balance'
        async with aiohttp.ClientSession() as session:
            async with session.get(url.format(wallet_address=wallet_address)) as response:
                return await response.json()

    @staticmethod
    async def ticker(currency: str) -> Coroutine[Any, Any, dict]:
        """
        Outputs currency exchange rate against other currencies
        :param currency: (str) short name of the currency, example - USD
        :return: (Coroutine[Any, Any, dict]) Currency dictionary
        """
        url = 'https://api.coinbase.com/v2/exchange-rates'
        params = {
            'currency': currency,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                return await response.json()

    @staticmethod
    async def get_balance(wallet_address: str, token: str, currency: str) -> float:
        """
        We get the cryptocurrency wallet balance and convert it to the required currency.
        :param wallet_address: (str) Address crypto wallet
        :param token: (str) Cryptocurrency wallet token. BTC or ETH
        :param currency: (str) Currency in which the amount of cryptocurrency wallet balance will be converted
        :return: (float) Cryptocurrency wallet balance
        """
        currency = currency.upper()
        token = token.upper()
        try:
            currency_rate = float((await CryptoCheck.ticker(token))['data']['rates'][currency])
            match token:
                case 'BTC':
                    money = (await CryptoCheck.btc(wallet_address=wallet_address))['balance'] / 1e8
                case 'ETH':
                    money = (await CryptoCheck.eth(wallet_address=wallet_address))['balance'] / 1e18
                case _:
                    raise NotFoundCryptoToken(f'The network {token} is not in the system')
            return currency_rate * money
        except KeyError:
            logger.error(f'The \033[35maddress=\033[0m'
                         f'\033[33m{wallet_address}\033[0m of this '
                         f'\033[35mnetwork=\033[0m\033[33m{token}\033[0m, '
                         f'\033[35mcurrency=\033[0m\033[33m{currency}\033[0m is not authentic')

    @staticmethod
    async def get_commission(currency: str) -> float:
        """
        Returns the network's commission for the time being.
        :param currency: (str) Currency for which you need to know the commission of the network. BTC or ETH
        :return: (float) commission value
        """
        match currency:
            case 'BTC':
                url = "https://api.blockchair.com/bitcoin/stats"
            case 'ETH':
                url = "https://api.blockchair.com/ethereum/stats"
            case _:
                raise NotFoundCryptoToken(f'The network {currency} is not in the system')
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    commission = data["data"]["average_transaction_fee_usd_24h"]
                    return commission
                else:
                    raise BadRequest(f'Bad request: {response.status}. Link: {url}')
