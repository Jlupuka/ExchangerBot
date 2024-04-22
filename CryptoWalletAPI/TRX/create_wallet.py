from tronpy import AsyncTron

from dataTemplates.data_templates import WalletTRX


class TRX:
    def __init__(self, private_key: str, client: AsyncTron) -> None:
        self.private_key = private_key
        self.client = client

    async def generate_wallet(self) -> WalletTRX:
        """
        Based on a mnemonic phrase, generates a TRX wallet
        :return Wallet TRX"""
        wallet: tuple[dict[str], str] = self.client.generate_address_with_mnemonic(
            self.private_key
        )
        return WalletTRX(wallet[1], **wallet[0])
