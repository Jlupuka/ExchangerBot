from importlib import import_module


__basedir__ = "CryptoWalletAPI"

from typing import Any


class CryptoWalletAPIService:
    @staticmethod
    async def get_crypto_attr(token: str, module_name: str, attr_name: str) -> Any:
        """
        Returns one of the classes for dealing with cryptocurrency. Client, wallet creation and wallet API
        Pulls out a folder "CryptoWalletAPI"
        :param token: (str) token cryptocurrency
        :param module_name: (str) Module Name
        :param attr_name: (str ) Class from module
        :return: Class object
        """
        module = import_module(f"{__basedir__}.{token.upper()}.{module_name}")
        attr_obj = getattr(module, attr_name)
        return attr_obj

    @staticmethod
    async def get_api_and_client(token: str, private_key: str) -> tuple:
        """
        Returns the client for working with the wallet API and the wallet API itself
        :param token: (str) token cryptocurrency
        :param private_key: (str) Mnemonic phrase for API wallet
        :return: (tuple[client, WalletAPI])
        """
        client = await CryptoWalletAPIService.get_crypto_attr(
            token=token,
            module_name="client",
            attr_name="Client",
        )
        crypto_api = await CryptoWalletAPIService.get_crypto_attr(
            token=token,
            module_name=f"{token.lower()}_api",
            attr_name=f"{token.capitalize()}API",
        )
        crypto_api = crypto_api(private_key=private_key, client=await client().client)
        return client, crypto_api
