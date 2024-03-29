from importlib import import_module


__basedir__ = "CryptoWalletAPI"


class CryptoWalletAPIService:
    @staticmethod
    async def get_crypto_attr(token: str, module_name: str, attr_name: str):
        module = import_module(f"{__basedir__}.{token.upper()}.{module_name}")
        attr_obj = getattr(module, attr_name)
        return attr_obj

    @staticmethod
    async def get_api_and_client(token: str, private_key: str) -> tuple:
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
