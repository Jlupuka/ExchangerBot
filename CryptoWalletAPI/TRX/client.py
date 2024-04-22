from tronpy import AsyncTron
from tronpy.providers import AsyncHTTPProvider

from config.config import load_config


class Client:
    @property
    async def client(self) -> AsyncTron:
        """
        :return: (AsyncTron) AsyncTron client
        """
        return await self.get_client()

    @staticmethod
    async def get_client() -> AsyncTron:
        """
        Creates an AsyncTron client
        :return: (AsyncTron) AsyncTron client
        """
        return AsyncTron(
            AsyncHTTPProvider(api_key=load_config().TronGridAPI.APIKEY),
            conf={"fee_limit": 1 * 10**6},
        )
