import re
from typing import Coroutine, Any

import aiohttp
import asyncio

from CastomExceptions.castomException import NotFoundCryptoToken
from services import logger


class CryptoCheck:
    @staticmethod
    async def is_valid_eth_address(address: str) -> bool:
        pattern = re.compile(r'^0x[a-fA-F0-9]{40}$')
        return bool(pattern.match(address))

    @staticmethod
    async def is_valid_btc_address(address: str) -> bool:
        pattern = re.compile(r'^[13][a-zA-Z0-9]{26,35}$')
        return bool(pattern.match(address))

    @staticmethod
    async def btc(wallet_address: str) -> dict:
        url = 'https://api.blockcypher.com/v1/btc/main/addrs/{wallet_address}/balance'
        async with aiohttp.ClientSession() as session:
            async with session.get(url.format(wallet_address=wallet_address)) as response:
                return await response.json()

    @staticmethod
    async def eth(wallet_address: str) -> dict:
        url = 'https://api.blockcypher.com/v1/eth/main/addrs/{wallet_address}/balance'
        async with aiohttp.ClientSession() as session:
            async with session.get(url.format(wallet_address=wallet_address)) as response:
                return await response.json()

    @staticmethod
    async def ticker(currency: str) -> Coroutine[Any, Any, dict]:
        url = 'https://api.coinbase.com/v2/exchange-rates'
        params = {
            'currency': currency,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                return await response.json()

    @staticmethod
    async def get_balance(wallet_address: str, currency_from: str, currency_to: str) -> float:
        currency_to = currency_to.upper()
        currency_from = currency_from.upper()
        try:
            currency_rate = float((await CryptoCheck.ticker(currency_from))['data']['rates'][currency_to])
            match currency_from:
                case 'BTC':
                    money = (await CryptoCheck.btc(wallet_address=wallet_address))['balance'] / 1e8
                case 'ETH':
                    money = (await CryptoCheck.eth(wallet_address=wallet_address))['balance'] / 1e18
                case _:
                    raise NotFoundCryptoToken(f'The network {currency_from} is not in the system')
            return currency_rate * money
        except KeyError as KE:
            logger.error(f'The \033[35maddress=\033[0m'
                         f'\033[33m{wallet_address}\033[0m of this '
                         f'\033[35mnetwork=\033[0m\033[33m{currency_from}\033[0m, '
                         f'\033[35mcurrency=\033[0m\033[33m{currency_to}\033[0m is not authentic')
