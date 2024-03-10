import math
import re
from typing import Coroutine, Any, Type

import aiohttp

from CastomExceptions.castomException import NotFoundCryptoToken, BadRequest, BadCryptoAddress
from services import logger
from services.dataService import JsonService

token_translate = {
    'XMR': 'monero',
    'TRX': 'tron'
}


class CryptoCheck:
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
    async def currency_rate(currency_from: str, currency_to: str, margins: float = 1.05) -> float:
        if currency_to in {'XMR', 'TRX'}:
            if currency_from in {'XMR', 'TRX'}:
                return margins
            currency = round(await CryptoCheck.get_currency_by_coingecko(currency_from=token_translate[currency_to],
                                                                         currency_to=currency_from.lower()) * margins,
                             7)
            return round(currency, 2) if currency_from in {'USD', 'RUB'} else round(currency, 7)
        return (1 / float((await CryptoCheck.ticker(currency_from))['data']['rates'][currency_to])) * margins

    @staticmethod
    async def get_currency_by_coingecko(currency_from: str = 'monero', currency_to: str = 'usd') -> float:
        async with aiohttp.ClientSession() as session:
            url = 'https://api.coingecko.com/api/v3/simple/price'
            params = {
                'ids': currency_from,
                'vs_currencies': currency_to
            }
            async with session.get(url=url, params=params) as response:
                data = await response.json()
                currency_rate = data[currency_from][currency_to]
                return float(currency_rate)

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
            currency_rate: float = await CryptoCheck.currency_rate(currency_from=token, currency_to=currency)
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
                         f'\033[35m network=\033[0m\033[33m{token}\033[0m, '
                         f'\033[35m currency=\033[0m\033[33m{currency}\033[0m is not authentic')

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

    @staticmethod
    async def validate_crypto_address(token: str, address: str) -> tuple[bool, Type[NotFoundCryptoToken]] | tuple[
        bool, Type[BadCryptoAddress]] | tuple[bool, None]:
        """
        Checks if the token and crypto address are valid
        :param token: (str) crypto token
        :param address: (str) address wallet
        :return: Logical expression, in case of error - error class
        """
        token = token.lower()
        patterns = await JsonService.get_token_patterns()
        if token == 'rub':
            return patterns['rub'](address), None
        if token not in patterns:
            return False, NotFoundCryptoToken
        pattern = patterns[token]
        if not re.match(pattern, address):
            return False, BadCryptoAddress
        return True, None

    @staticmethod
    async def minimal_summa(minSum: int | float, currency_from: str, currency_to: str) -> float:
        if currency_from != 'RUB':
            currency_rate = await CryptoCheck.currency_rate(currency_from='RUB',
                                                            currency_to=currency_from,
                                                            margins=1)
        else:
            currency_rate = await CryptoCheck.currency_rate(currency_from=currency_from,
                                                            currency_to=currency_to,
                                                            margins=1)
        minSum /= currency_rate
        return round(minSum, 2) if currency_from in {'RUB', 'USD'} else float(format(minSum, '.7f'))

    @staticmethod
    async def transaction_amount(amount: int | float, currency_from: str,
                                 currency_to: str,
                                 margins: float | int = 1) -> float:
        currency_rate = await CryptoCheck.currency_rate(currency_from=currency_to,
                                                        currency_to=currency_from,
                                                        margins=1)
        amount *= currency_rate / margins
        return math.ceil(amount) if currency_to in {'RUB', 'USD'} else float(format(amount, '.7f'))
