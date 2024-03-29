from tronpy import AsyncTron
from tronpy.keys import PrivateKey

from CryptoWalletAPI.TRX.client import Client


class TrxAPI:
    def __init__(self, private_key: str, client: AsyncTron) -> None:
        self.client: AsyncTron = client
        self.private_key = PrivateKey(private_key_bytes=bytes.fromhex(private_key))
        self.wallet = self.client.generate_address(priv_key=self.private_key)

    async def send_trx(
        self, to_address: str, amount: int | float, memo: str = "any"
    ) -> dict:
        """
        Sends TRX to the specified wallet
        :param to_address: (str) Wallet where the funds will be sent
        :param amount: (int | float) Amount of funds
        :param memo: (str) Memo of the transaction
        :return:
        """

        tx_data = {"to_address": to_address, "amount": int(amount * 10**6)}
        transaction = await (
            self.client.trx.transfer(
                self.wallet["base58check_address"],
                to=tx_data["to_address"],
                amount=tx_data["amount"],
            )
            .memo(memo)
            .build()
        )
        transaction_ret = await transaction.sign(priv_key=self.private_key).broadcast()
        tx_wait = await transaction_ret.wait()
        return tx_wait

    async def get_balance(self) -> float:
        """

        :return:
        """
        return float(
            await self.client.get_account_balance(self.wallet["base58check_address"])
        )

    async def check_payment(self, amount: float) -> bool:
        """

        :param amount:
        :return:
        """
        return (await self.get_balance()) >= amount

    @property
    def address(self) -> str:
        return self.wallet["base58check_address"]


async def main():
    tron_obj = TrxAPI(
        private_key="fsafsaf",
        client=await Client().client,
    )

    return await tron_obj.get_balance()
