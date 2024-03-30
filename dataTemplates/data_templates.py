from dataclasses import dataclass
from typing import Union


@dataclass
class MnemonicData:
    address: str
    balance: float
    mnemonic: str
    token: str


@dataclass
class SendData:
    user_address: str
    amount: Union[float, int]


@dataclass
class WalletTRX:
    seed_phrases: str
    base58check_address: str
    hex_address: str
    private_key: str
    public_key: str
