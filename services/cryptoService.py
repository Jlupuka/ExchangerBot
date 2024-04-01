import math
import re
from typing import Coroutine, Any, Type, Union

import aiohttp

from CastomExceptions.castomException import (
    NotFoundCryptoToken,
    BadCryptoAddress,
)
from services.JsonService import JsonService

token_translate = {"XMR": "monero", "TRX": "tron"}


class CryptoCheck:
    @staticmethod
    async def ticker(currency: str) -> Coroutine[Any, Any, dict]:
        """
        Outputs currency exchange rate against other currencies
        :param currency: (str) short name of the currency, example - USD
        :return: (Coroutine[Any, Any, dict]) Currency dictionary
        """
        url = "https://api.coinbase.com/v2/exchange-rates"
        params = {
            "currency": currency,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                return await response.json()

    @staticmethod
    async def currency_rate(
        currency_from: str, currency_to: str, margins: float = 1.05
    ) -> float:
        """
        Returns the currency rate
        :param currency_from: (str) Name of currency to be transferred
        :param currency_to: (str) Name of currency to be converted
        :param margins: (float) Markup
        :return: (float) Price
        """
        if currency_to in {"XMR", "TRX"}:
            if currency_from in {"XMR", "TRX"}:
                if currency_from == currency_to:
                    return margins
                currency_to = await CryptoCheck.get_currency_by_coingecko(
                    currency_from=token_translate[currency_to]
                )
                currency_from = await CryptoCheck.get_currency_by_coingecko(
                    currency_from=token_translate[currency_from]
                )
                return round(currency_to / currency_from * margins, 7)
            currency = round(
                await CryptoCheck.get_currency_by_coingecko(
                    currency_from=token_translate[currency_to],
                    currency_to=currency_from.lower(),
                )
                * margins,
                7,
            )
            return (
                round(currency, 2)
                if currency_from in {"USD", "RUB"}
                else round(currency, 7)
            )
        return (
            1
            / float(
                (await CryptoCheck.ticker(currency_from))["data"]["rates"][currency_to]
            )
        ) * margins

    @staticmethod
    async def get_currency_by_coingecko(
        currency_from: str = "monero", currency_to: str = "usd"
    ) -> float:
        """
        Returns the currency rate by coingecko
        :param currency_from: (str) Name of currency to be transferred
        :param currency_to: (str) Name of currency to be converted
        :return: (float) Price
        """
        async with aiohttp.ClientSession() as session:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {"ids": currency_from, "vs_currencies": currency_to}
            async with session.get(url=url, params=params) as response:
                data = await response.json()
                currency_rate = data[currency_from][currency_to]
                return float(currency_rate)

    @staticmethod
    async def validate_crypto_address(token: str, address: str) -> Union[
        tuple[bool, Type[NotFoundCryptoToken]],
        tuple[bool, Type[BadCryptoAddress]],
        tuple[bool, None],
    ]:
        """
        Checks if the token and crypto address are valid
        :param token: (str) crypto token
        :param address: (str) address wallet
        :return: Logical expression, in case of error - error class
        """
        token = token.lower()
        patterns = await JsonService.get_token_patterns()
        if token == "rub":
            return patterns["rub"](address), None
        if token not in patterns:
            return False, NotFoundCryptoToken
        pattern = patterns[token]
        if not re.match(pattern, address):
            return False, BadCryptoAddress
        return True, None

    @staticmethod
    async def minimal_summa(
        minSum: Union[int, float], currency_from: str, currency_to: str
    ) -> float:
        """
        Converts the minimum exchange amount to the desired currency
        :param minSum: (Union[int, float]) minimal amount
        :param currency_from: (str) Name of currency to be transferred
        :param currency_to: (str) Name of currency to be converted
        :return: (float) Price
        """
        if currency_from != "RUB":
            currency_rate = await CryptoCheck.currency_rate(
                currency_from="RUB", currency_to=currency_from, margins=1
            )
        else:
            currency_rate = await CryptoCheck.currency_rate(
                currency_from=currency_from, currency_to=currency_to, margins=1
            )
        minSum /= currency_rate
        return (
            round(minSum, 2)
            if currency_from in {"RUB", "USD"}
            else float(format(minSum, ".7f"))
        )

    @staticmethod
    async def transaction_amount(
        amount: Union[int, float],
        currency_from: str,
        currency_to: str,
        margins: Union[float, int] = 1,
    ) -> float:
        """
        Returns the transfer amount in the desired currency
        :param amount: (Union[int, float]) Transfer amount
        :param currency_from: (str) Name of currency to be transferred
        :param currency_to: (str) Name of currency to be converted
        :param margins: (float) Markup
        :return: (float) Price
        """
        currency_rate = await CryptoCheck.currency_rate(
            currency_from=currency_to, currency_to=currency_from, margins=1
        )
        amount *= currency_rate / margins
        return (
            math.ceil(amount)
            if currency_to in {"RUB", "USD"}
            else float(format(amount, ".7f"))
        )
