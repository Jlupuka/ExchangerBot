from importlib import import_module

__baseFileModule___ = "dataTemplates.data_templates"

from typing import Union

from dataTemplates.data_templates import WalletTRX


class DataTemplatesService:
    @staticmethod
    async def select_crypto_data_templates(token: str) -> Union[WalletTRX]:
        """
        Returns the data transformation template
        :param token: (str) Token cryptocurrency
        :return: (Union[WalletTRX])
        """
        module = import_module(f"{__baseFileModule___}")
        return getattr(module, f"Wallet{token}")
