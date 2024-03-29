from dataclasses import dataclass
from tronpy import AsyncTron


@dataclass
class WalletTRX:
    seed_phrases: str
    base58check_address: str
    hex_address: str
    private_key: str
    public_key: str


class TRX:
    def __init__(self, private_key: str, client: AsyncTron) -> None:
        self.private_key = private_key
        self.client = client

    async def generate_wallet(self) -> WalletTRX:
        wallet: tuple[dict[str], str] = self.client.generate_address_with_mnemonic(
            self.private_key
        )
        return WalletTRX(wallet[1], **wallet[0])
