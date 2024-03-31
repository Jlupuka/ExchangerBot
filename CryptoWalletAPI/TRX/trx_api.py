from tronpy import AsyncTron
from tronpy.keys import PrivateKey


class TrxAPI:
    def __init__(self, private_key: str, client: AsyncTron) -> None:
        self.client: AsyncTron = client
        self.private_key = PrivateKey(private_key_bytes=bytes.fromhex(private_key))
        self.wallet = self.client.generate_address(priv_key=self.private_key)

    async def send_funds(self, to_address: str, amount: int | float, memo: str = "any") -> dict:
        """
        Sends TRX to the specified wallet
        :param to_address: (str) Wallet where the funds will be sent
        :param amount: (int | float) Amount of funds
        :param memo: (str) Memo of the transaction
        :return: (dict) Dictionary with translation certificate
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
        Returns the wallet balance to TRX
        :return: float
        """
        return float(await self.client.get_account_balance(self.wallet["base58check_address"]))

    async def check_payment(self, amount: float) -> bool:
        """
        Returns whether the wallet has an input amount of funds or not
        :param amount: number of funds
        :return: bool
        """
        return (await self.get_balance()) >= amount

    @property
    def address(self) -> str:
        return self.wallet["base58check_address"]
